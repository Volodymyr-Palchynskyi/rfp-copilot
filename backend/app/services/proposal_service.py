import logging
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx
from google import genai
from google.genai import errors, types
from pydantic_core import from_json

from app.core.config import settings
from app.schemas.proposal import ProposalDraft, ProposalRequest, ProposalResponse, ReferenceProject, Usage
from app.services.knowledge_service import KnowledgeService, ReferenceContext

logger = logging.getLogger(__name__)

# A streamed event: {"event": "references" | "section" | "complete", "data": <json-serialisable>}
StreamEvent = dict[str, Any]


def is_retryable(exc: Exception) -> bool:
    """Failures where another model may well succeed: rate limits, overload, outages, timeouts."""
    if isinstance(exc, errors.APIError):
        return exc.code == 429 or exc.code >= 500
    return isinstance(exc, httpx.TransportError)


class ProposalService:
    def __init__(self, knowledge: KnowledgeService | None = None):
        self.knowledge = knowledge
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in settings or .env file.")

        self.model_name = settings.GEMINI_MODEL
        self.models = [self.model_name]
        if settings.GEMINI_FALLBACK_MODEL and settings.GEMINI_FALLBACK_MODEL != self.model_name:
            self.models.append(settings.GEMINI_FALLBACK_MODEL)
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=settings.GEMINI_TIMEOUT_S * 1000),
        )

        self.system_instruction = (
            "You are a Principal Enterprise Solutions Architect and Tech Lead. "
            "Your job is to analyze client RFP requirements, technical briefs, and constraints, "
            "then generate a realistic, production-ready, highly professional Technical Proposal. "
            "Estimates must be pragmatic (not overly optimistic). "
            "Select modern, industry-standard technologies suitable for production. "
            "When REFERENCE PROJECTS are provided, treat their hours as real historical data: "
            "ground your estimates in the closest analogies, adjust explicitly for scope differences, "
            "reuse their lessons learned as risks, and explain this in estimation_basis. "
            "Never invent reference projects that were not provided. "
            "ESTIMATION RULES: "
            "(1) Hours are total delivery effort of a human team, not just coding: discovery and design, "
            "development, code review, automated and manual QA, UAT, DevOps and CI/CD, project management, "
            "documentation and post-release stabilisation. Do not assume AI-assisted speedups. "
            "(2) Always list QA/UAT, DevOps and integration work as explicit features; real projects "
            "spend a large share of hours there. A non-trivial module (third-party integration, "
            "real-time updates, offline sync, payments, role-based access with audit) usually takes "
            "several hundred hours with testing, not tens. "
            "(3) With references, estimate module by module: reuse the hours of the matching module in a "
            "reference, and add separate estimates for modules that have no analogue. Never shrink the "
            "total because only part of the brief resembles a reference. "
            "(4) Without close references, build the estimate bottom-up from the modules and state the "
            "uncertainty in estimation_basis instead of defaulting to a small number."
        )

    async def generate_proposal(self, request: ProposalRequest) -> ProposalResponse:
        """
        Retrieves similar past projects (RAG), asks Gemini for a structured draft grounded
        in them, then computes totals and attaches references in code.
        """
        started = time.perf_counter()
        references = await self._retrieve_references(request)

        prompt = self._build_prompt(request, references)
        response, model = await self._generate_with_fallback(prompt)
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        draft = ProposalDraft.model_validate_json(response.text)
        usage = self._usage(response.usage_metadata, model, started, first_token_at=None)
        return self._assemble(draft, self._to_reference_models(references), usage)

    async def stream_proposal(self, request: ProposalRequest) -> AsyncIterator[StreamEvent]:
        """
        Same pipeline as generate_proposal, but yields events while Gemini is still writing:

        - references: the retrieved past projects (available before generation starts)
        - section:    {key, value} whenever a top-level field of the draft changed. Values may be
                      partial (a half-written string, a list whose last item is incomplete).
        - complete:   the final validated ProposalResponse, with computed totals
        """
        started = time.perf_counter()
        references = await self._retrieve_references(request)
        reference_models = self._to_reference_models(references)
        yield {"event": "references", "data": [r.model_dump() for r in reference_models]}

        prompt = self._build_prompt(request, references)
        text = ""
        emitted: dict[str, Any] = {}
        usage_metadata = None
        first_token_at: float | None = None
        model = self.models[0]

        for attempt, model in enumerate(self.models):
            try:
                stream = await self.client.aio.models.generate_content_stream(
                    model=model, contents=prompt, config=self._generation_config()
                )
                async for chunk in stream:
                    usage_metadata = chunk.usage_metadata or usage_metadata
                    if not chunk.text:
                        continue
                    if first_token_at is None:
                        first_token_at = time.perf_counter()
                    text += chunk.text
                    try:
                        partial = from_json(text, allow_partial="trailing-strings")
                    except ValueError:
                        continue  # chunk boundary fell somewhere unparseable, wait for more text
                    if not isinstance(partial, dict):
                        continue
                    for key, value in partial.items():
                        if emitted.get(key) != value:
                            emitted[key] = value
                            yield {"event": "section", "data": {"key": key, "value": value}}
                break
            except Exception as exc:
                # Falling back is only safe before the client has seen any output: restarting
                # mid-draft with another model would splice two different proposals together.
                is_last = attempt == len(self.models) - 1
                if text or is_last or not is_retryable(exc):
                    raise
                logger.warning("Model %s failed (%s), falling back to %s", model, exc, self.models[attempt + 1])
                yield {"event": "notice", "data": {"fallback_model": self.models[attempt + 1]}}

        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        draft = ProposalDraft.model_validate_json(text)
        usage = self._usage(usage_metadata, model, started, first_token_at)
        yield {"event": "complete", "data": self._assemble(draft, reference_models, usage).model_dump()}

    # ------------------------------------------------------------------ helpers

    def _generation_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            response_mime_type="application/json",
            response_schema=ProposalDraft,
            temperature=0.2,
        )

    @staticmethod
    def _build_prompt(request: ProposalRequest, references: list[ReferenceContext]) -> str:
        return f"""
Analyze the following client request and build a detailed technical proposal:

CLIENT NAME: {request.client_name}
BUDGET TIER: {request.budget_level}
TARGET TIMELINE: {request.target_timeline_weeks or 'Flexible / Not specified'}

PROJECT REQUIREMENTS & BRIEF:
{request.project_description}

{ProposalService._format_references(references)}

GUIDELINES:
1. Provide a clear, compelling project title and executive summary.
2. Recommend an appropriate modern tech stack with clear justification for each choice.
3. Break down the scope into distinct modules/features with realistic min and max engineering hours.
4. Highlight real technical risks and actionable mitigation strategies.
5. Fill estimation_basis explaining which reference projects informed the numbers.
"""

    @staticmethod
    def _assemble(
        draft: ProposalDraft, references: list[ReferenceProject], usage: Usage | None = None
    ) -> ProposalResponse:
        return ProposalResponse(
            **draft.model_dump(),
            total_hours_min=sum(f.hours_min for f in draft.features),
            total_hours_max=sum(f.hours_max for f in draft.features),
            references=references,
            usage=usage,
        )

    async def _generate_with_fallback(self, prompt: str) -> tuple[types.GenerateContentResponse, str]:
        for attempt, model in enumerate(self.models):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model, contents=prompt, config=self._generation_config()
                )
                return response, model
            except Exception as exc:
                if attempt == len(self.models) - 1 or not is_retryable(exc):
                    raise
                logger.warning("Model %s failed (%s), falling back to %s", model, exc, self.models[attempt + 1])
        raise RuntimeError("No models configured")  # unreachable: self.models is never empty

    def _usage(self, metadata: Any, model: str, started: float, first_token_at: float | None) -> Usage | None:
        """Token counts come from Gemini; cost is only estimated if prices are configured."""
        if metadata is None:
            return None
        input_tokens = metadata.prompt_token_count or 0
        output_tokens = metadata.candidates_token_count or 0
        thinking_tokens = metadata.thoughts_token_count or 0
        cost = None
        if settings.PRICE_INPUT_PER_MTOK or settings.PRICE_OUTPUT_PER_MTOK:
            cost = (
                input_tokens * settings.PRICE_INPUT_PER_MTOK
                + (output_tokens + thinking_tokens) * settings.PRICE_OUTPUT_PER_MTOK
            ) / 1_000_000
        usage = Usage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
            total_tokens=metadata.total_token_count or input_tokens + output_tokens + thinking_tokens,
            latency_s=round(time.perf_counter() - started, 1),
            first_token_s=round(first_token_at - started, 1) if first_token_at else None,
            estimated_cost_usd=round(cost, 5) if cost is not None else None,
        )
        logger.info("proposal usage: %s", usage.model_dump_json())
        return usage

    @staticmethod
    def _to_reference_models(references: list[ReferenceContext]) -> list[ReferenceProject]:
        return [
            ReferenceProject(
                project_id=r.project_id,
                title=r.title,
                industry=r.industry,
                stack=r.stack,
                total_hours=r.total_hours,
                duration_weeks=r.duration_weeks,
                relevance_score=round(r.score, 4),
                matched_sections=[section for section, _ in r.chunks],
            )
            for r in references
        ]

    async def _retrieve_references(self, request: ProposalRequest) -> list[ReferenceContext]:
        """Retrieval is an enhancement: if it fails we still produce a proposal without grounding."""
        if self.knowledge is None:
            return []
        try:
            return await self.knowledge.find_references(request.project_description)
        except Exception:
            logger.exception("Reference retrieval failed, continuing without RAG context")
            return []

    @staticmethod
    def _format_references(references: list[ReferenceContext]) -> str:
        if not references:
            return "REFERENCE PROJECTS: none available."
        blocks = []
        for r in references:
            sections = "\n\n".join(f"[{section}]\n{text}" for section, text in r.chunks)
            blocks.append(
                f"### {r.title} (id={r.project_id}, industry={r.industry}, stack={r.stack}, "
                f"total_hours={r.total_hours}, duration_weeks={r.duration_weeks})\n{sections}"
            )
        return "REFERENCE PROJECTS (real historical data from our past deliveries):\n\n" + "\n\n".join(blocks)

import logging
from collections.abc import AsyncIterator
from typing import Any

from google import genai
from google.genai import types
from pydantic_core import from_json

from app.core.config import settings
from app.schemas.proposal import ProposalDraft, ProposalRequest, ProposalResponse, ReferenceProject
from app.services.knowledge_service import KnowledgeService, ReferenceContext

logger = logging.getLogger(__name__)

# A streamed event: {"event": "references" | "section" | "complete", "data": <json-serialisable>}
StreamEvent = dict[str, Any]


class ProposalService:
    def __init__(self, knowledge: KnowledgeService | None = None):
        self.knowledge = knowledge
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in settings or .env file.")

        self.model_name = settings.GEMINI_MODEL
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

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
        references = await self._retrieve_references(request)

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=self._build_prompt(request, references),
            config=self._generation_config(),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        draft = ProposalDraft.model_validate_json(response.text)
        return self._assemble(draft, self._to_reference_models(references))

    async def stream_proposal(self, request: ProposalRequest) -> AsyncIterator[StreamEvent]:
        """
        Same pipeline as generate_proposal, but yields events while Gemini is still writing:

        - references: the retrieved past projects (available before generation starts)
        - section:    {key, value} whenever a top-level field of the draft changed. Values may be
                      partial (a half-written string, a list whose last item is incomplete).
        - complete:   the final validated ProposalResponse, with computed totals
        """
        references = await self._retrieve_references(request)
        reference_models = self._to_reference_models(references)
        yield {"event": "references", "data": [r.model_dump() for r in reference_models]}

        text = ""
        emitted: dict[str, Any] = {}
        stream = await self.client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=self._build_prompt(request, references),
            config=self._generation_config(),
        )
        async for chunk in stream:
            if not chunk.text:
                continue
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

        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        draft = ProposalDraft.model_validate_json(text)
        yield {"event": "complete", "data": self._assemble(draft, reference_models).model_dump()}

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
    def _assemble(draft: ProposalDraft, references: list[ReferenceProject]) -> ProposalResponse:
        return ProposalResponse(
            **draft.model_dump(),
            total_hours_min=sum(f.hours_min for f in draft.features),
            total_hours_max=sum(f.hours_max for f in draft.features),
            references=references,
        )

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

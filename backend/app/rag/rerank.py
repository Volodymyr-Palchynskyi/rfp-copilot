import logging
from dataclasses import dataclass

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)

_EXCERPT_CHARS = 1500

_SYSTEM = (
    "You decide which past projects are useful analogies for estimating a NEW project. "
    "Judge by modules and scope: which parts of the new brief have a counterpart in the past project whose "
    "effort could be reused. A shared industry, shared technology or generic words like 'dashboard' or "
    "'portal' are NOT enough on their own. Be strict: a wrongly included project misleads the estimate, "
    "a missing one only loses a hint.\n\n"
    "Relevance scale:\n"
    "3 = same kind of product, most major modules have a counterpart\n"
    "2 = at least one substantial module (a large part of the scope) has a clear counterpart\n"
    "1 = only generic similarity (same industry or stack, no reusable module)\n"
    "0 = unrelated"
)


@dataclass(frozen=True)
class Candidate:
    project_id: str
    title: str
    industry: str
    stack: str
    excerpt: str


class ProjectJudgement(BaseModel):
    # `reason` comes first so the model explains before it scores.
    project_id: str
    reason: str = Field(description="One sentence: which parts of the new brief this project covers, or why it does not apply")
    relevance: int = Field(ge=0, le=3)


class RerankResult(BaseModel):
    judgements: list[ProjectJudgement]


class Reranker:
    """LLM relevance judge over vector-search candidates. One call per request, all candidates at once."""

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in settings or .env file.")
        self._client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=settings.RERANK_TIMEOUT_S * 1000),
        )
        self._model = settings.RERANK_MODEL or settings.GEMINI_MODEL

    async def judge(self, brief: str, candidates: list[Candidate]) -> dict[str, ProjectJudgement]:
        blocks = "\n\n".join(
            f"### project_id={c.project_id}\n{c.title} (industry: {c.industry}; stack: {c.stack})\n"
            f"{c.excerpt[:_EXCERPT_CHARS]}"
            for c in candidates
        )
        prompt = f"NEW PROJECT BRIEF:\n{brief}\n\nCANDIDATE PAST PROJECTS:\n\n{blocks}\n\nJudge every candidate."
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM,
                response_mime_type="application/json",
                response_schema=RerankResult,
                temperature=0.0,
                thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            ),
        )
        if not response.text:
            raise RuntimeError("Reranker returned an empty response.")
        result = RerankResult.model_validate_json(response.text)
        known = {c.project_id for c in candidates}
        return {j.project_id: j for j in result.judgements if j.project_id in known}

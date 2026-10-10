from typing import Literal
from pydantic import BaseModel, Field

from app.core.config import settings


# ==============================================================================
# 1. INCOMING REQUEST (Payload from Angular Frontend Form)
# ==============================================================================
class ProposalRequest(BaseModel):
    client_name: str = Field(
        min_length=1,
        max_length=120,
        description="Client company name or stakeholder name",
        examples=["Acme Corp"]
    )
    project_description: str = Field(
        min_length=20,
        max_length=settings.MAX_BRIEF_CHARS,
        description="Raw requirements, client RFP notes, or project description"
    )
    budget_level: Literal["budget", "standard", "enterprise"] = Field(
        default="standard",
        description="Target budget tier and solution reliability requirement"
    )
    target_timeline_weeks: int | None = Field(
        default=None,
        description="Desired target delivery timeline in weeks (optional)"
    )


# ==============================================================================
# 2. PROPOSAL DOMAIN ENTITIES
# ==============================================================================
class TechStackItem(BaseModel):
    category: Literal["Frontend", "Backend", "Database", "AI/ML", "DevOps/Cloud"] = Field(
        description="Technology domain category"
    )
    name: str = Field(description="Name of the technology/framework (e.g. 'Angular 19', 'FastAPI')")
    reason: str = Field(description="Clear technical rationale why this tech fits the requirements")


class FeatureEstimate(BaseModel):
    module: str = Field(description="Module or Epic name (e.g. 'Auth & Security', 'AI Pipeline')")
    title: str = Field(description="Specific feature or deliverable title")
    description: str = Field(description="Brief functional scope description")
    complexity: Literal["low", "medium", "high"] = Field(description="Implementation complexity level")
    hours_min: int = Field(ge=1, description="Minimum estimated engineering hours")
    hours_max: int = Field(ge=1, description="Maximum estimated engineering hours")


class RiskItem(BaseModel):
    risk: str = Field(description="Identified technical or architectural risk")
    impact: Literal["low", "medium", "high"] = Field(description="Potential impact severity")
    mitigation: str = Field(description="Recommended prevention or mitigation strategy")


class ReferenceProject(BaseModel):
    """A past project retrieved from the knowledge base and used to ground the estimate."""

    project_id: str
    title: str
    industry: str
    stack: str
    total_hours: int
    duration_weeks: int
    relevance_score: float = Field(description="Best cosine similarity among matched chunks")
    matched_sections: list[str]


# ==============================================================================
# 3. LLM OUTPUT (schema given to Gemini) AND API RESPONSE (draft + computed fields)
# ==============================================================================
class ProposalDraft(BaseModel):
    """Everything the model is responsible for. Totals and references are computed in code."""

    project_title: str = Field(description="Compelling, professional project proposal title")
    executive_summary: str = Field(description="High-level summary (2-3 paragraphs) for decision makers")
    architecture_overview: str = Field(
        description="High-level architectural approach (monolith, microservices, modular, etc.)")

    tech_stack: list[TechStackItem] = Field(description="Curated list of recommended technologies")
    features: list[FeatureEstimate] = Field(description="Itemized scope of work with effort estimates")
    risks: list[RiskItem] = Field(description="Risk assessment with mitigation strategies")

    estimated_duration_weeks: int = Field(description="Realistic delivery timeline in weeks")
    estimation_basis: str = Field(
        description="How the estimates were derived: which reference projects were used as "
                    "analogies and how scope differences were adjusted. If no reference projects "
                    "were provided, state that the estimate is based on general experience only."
    )


class Usage(BaseModel):
    """Cost and latency of one generation, for observability and the README numbers."""

    model: str
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    total_tokens: int
    latency_s: float = Field(description="Wall time from request start to the final event")
    first_token_s: float | None = Field(description="Time until the model produced its first token")
    estimated_cost_usd: float | None = Field(
        description="None unless PRICE_INPUT_PER_MTOK / PRICE_OUTPUT_PER_MTOK are configured"
    )


class ProposalResponse(ProposalDraft):
    total_hours_min: int = Field(description="Sum of feature hours_min, computed server-side")
    total_hours_max: int = Field(description="Sum of feature hours_max, computed server-side")
    references: list[ReferenceProject] = Field(
        default_factory=list,
        description="Past projects retrieved from the knowledge base for this request",
    )
    usage: Usage | None = None

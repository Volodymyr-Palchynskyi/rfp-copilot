from typing import Literal
from pydantic import BaseModel, Field


# ==============================================================================
# 1. INCOMING REQUEST (Payload from Angular Frontend Form)
# ==============================================================================
class ProposalRequest(BaseModel):
    client_name: str = Field(
        description="Client company name or stakeholder name",
        examples=["Acme Corp"]
    )
    project_description: str = Field(
        min_length=20,
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


# ==============================================================================
# 3. ROOT PROPOSAL RESPONSE (Structured Output from Gemini -> Sent to Angular)
# ==============================================================================
class ProposalResponse(BaseModel):
    project_title: str = Field(description="Compelling, professional project proposal title")
    executive_summary: str = Field(description="High-level summary (2-3 paragraphs) for decision makers")
    architecture_overview: str = Field(
        description="High-level architectural approach (monolith, microservices, modular, etc.)")

    tech_stack: list[TechStackItem] = Field(description="Curated list of recommended technologies")
    features: list[FeatureEstimate] = Field(description="Itemized scope of work with effort estimates")
    risks: list[RiskItem] = Field(description="Risk assessment with mitigation strategies")

    total_hours_min: int = Field(description="Aggregated minimum engineering hours")
    total_hours_max: int = Field(description="Aggregated maximum engineering hours")
    estimated_duration_weeks: int = Field(description="Realistic delivery timeline in weeks")
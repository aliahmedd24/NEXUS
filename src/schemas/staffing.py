"""Staffing schemas: sourcing options, frontier points, and staffing plans."""

from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.common import SourcingStrategy


class SourcingOption(BaseModel):
    """One sourcing strategy for a role."""

    strategy: SourcingStrategy
    candidate_id: UUID | None = None
    candidate_name: str | None = None
    estimated_cost_eur: float = 0
    estimated_time_days: int = 90
    quality_estimate: float = Field(0.5, ge=0.0, le=1.0)
    risk_level: str = "medium"
    rationale: str = ""


class EfficientFrontierPoint(BaseModel):
    """One point on the efficient frontier curve."""

    budget_eur: float
    resilience_improvement: float
    selected_hires: list[str] = Field(default_factory=list)
    roi: float = 0.0


class StaffingPlanItem(BaseModel):
    """One hire in a staffing plan."""

    role_id: UUID
    role_title: str = ""
    recommended_candidate_id: UUID | None = None
    recommended_candidate_name: str = ""
    sourcing_strategy: SourcingStrategy = SourcingStrategy.EXTERNAL_HIRE
    sourcing_options: list[SourcingOption] = Field(default_factory=list)
    fit_score: float = Field(0.0, ge=0.0, le=1.0)
    resilience_contribution: float = 0.0
    estimated_cost_eur: float = 0
    priority_rank: int = 0
    rationale: str = ""


class StaffingPlan(BaseModel):
    """Complete staffing plan with portfolio optimization."""

    plan_id: UUID | None = None
    scenario_name: str = ""
    items: list[StaffingPlanItem] = Field(default_factory=list)
    total_cost_eur: float = 0
    total_resilience_improvement: float = 0.0
    efficient_frontier: list[EfficientFrontierPoint] = Field(
        default_factory=list
    )
    constraints_applied: list[str] = Field(default_factory=list)

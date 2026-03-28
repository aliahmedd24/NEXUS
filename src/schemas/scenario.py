"""Scenario schemas: capability demand vectors and scenario objects."""

from uuid import UUID

from pydantic import BaseModel, Field


class CapabilityDemandVector(BaseModel):
    """12-dimension capability demand profile for a scenario.

    Each field is 0.0-1.0, representing how critical that dimension is
    under the given scenario conditions.
    """

    strategic_thinking: float = Field(0.5, ge=0.0, le=1.0)
    operational_execution: float = Field(0.5, ge=0.0, le=1.0)
    people_development: float = Field(0.5, ge=0.0, le=1.0)
    innovation_orientation: float = Field(0.5, ge=0.0, le=1.0)
    stakeholder_management: float = Field(0.5, ge=0.0, le=1.0)
    cultural_sensitivity: float = Field(0.5, ge=0.0, le=1.0)
    crisis_leadership: float = Field(0.5, ge=0.0, le=1.0)
    change_management: float = Field(0.5, ge=0.0, le=1.0)
    technical_depth: float = Field(0.5, ge=0.0, le=1.0)
    risk_calibration: float = Field(0.5, ge=0.0, le=1.0)
    industry_knowledge: float = Field(0.5, ge=0.0, le=1.0)
    digital_fluency: float = Field(0.5, ge=0.0, le=1.0)

    def to_dict(self) -> dict[str, float]:
        """Convert to a plain dict of dimension -> value."""
        return self.model_dump()


class ScenarioObject(BaseModel):
    """A scenario with its metadata and capability demand profile."""

    id: UUID | None = None
    name: str
    description: str = ""
    probability: float = Field(0.5, ge=0.0, le=1.0)
    time_horizon_months: int = 12
    affected_org_units: list[UUID] = Field(default_factory=list)
    demand_vector: CapabilityDemandVector = Field(
        default_factory=CapabilityDemandVector
    )

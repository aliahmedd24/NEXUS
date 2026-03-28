"""Chemistry schemas: team compatibility and balance assessments."""

from uuid import UUID

from pydantic import BaseModel, Field


class PairwiseCompatibility(BaseModel):
    """Compatibility assessment between two leaders."""

    leader_a_id: UUID
    leader_b_id: UUID
    leader_a_name: str = ""
    leader_b_name: str = ""
    synergy_score: float = Field(0.0, ge=-1.0, le=1.0)
    friction_dimensions: list[str] = Field(default_factory=list)
    synergy_dimensions: list[str] = Field(default_factory=list)
    groupthink_risk: float = Field(0.0, ge=0.0, le=1.0)
    relationship_type: str = ""


class TeamBalanceCard(BaseModel):
    """Balance analysis for a team with a potential new member."""

    cognitive_diversity: float = Field(0.0, ge=0.0, le=1.0)
    gap_dimensions: list[str] = Field(default_factory=list)
    overlap_dimensions: list[str] = Field(default_factory=list)
    diversity_delta: float = 0.0
    gaps_filled: list[str] = Field(default_factory=list)
    new_overlaps: list[str] = Field(default_factory=list)


class TeamChemistryReport(BaseModel):
    """Complete team chemistry analysis."""

    team_id: UUID | None = None
    pairwise: list[PairwiseCompatibility] = Field(default_factory=list)
    balance: TeamBalanceCard = Field(default_factory=TeamBalanceCard)
    overall_chemistry: float = Field(0.0, ge=-1.0, le=1.0)
    trajectory_6mo: float = 0.0
    trajectory_12mo: float = 0.0
    trajectory_18mo: float = 0.0
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

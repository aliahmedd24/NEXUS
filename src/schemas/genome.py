"""Genome schemas: leadership genome profiles and comparisons."""

from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.common import ConfidenceLevel, DimensionScore


class LeadershipGenome(BaseModel):
    """Complete leadership genome profile for a leader or candidate."""

    leader_id: UUID
    leader_name: str = ""
    leader_type: str = ""
    dimensions: list[DimensionScore] = Field(default_factory=list)
    overall_strength: float = Field(0.0, ge=0.0, le=1.0)
    bias_corrections_applied: dict[str, str] = Field(default_factory=dict)

    @property
    def dimension_dict(self) -> dict[str, float]:
        """Quick lookup: dimension name -> corrected score (or raw if no correction)."""
        return {
            d.dimension: (
                d.corrected_score if d.corrected_score is not None else d.raw_score
            )
            for d in self.dimensions
        }


class GenomeComparison(BaseModel):
    """Comparison of two leadership genomes."""

    leader_a_id: UUID
    leader_b_id: UUID
    leader_a_name: str = ""
    leader_b_name: str = ""
    fit_score_a: float = Field(0.0, ge=0.0, le=1.0)
    fit_score_b: float = Field(0.0, ge=0.0, le=1.0)
    advantages_a: list[str] = Field(default_factory=list)
    advantages_b: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM

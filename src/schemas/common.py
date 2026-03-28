"""Common schemas: enums, base types, and shared models."""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence level for a score or assessment."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SeverityStatus(str, Enum):
    """Severity of a vulnerability or risk."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourcingStrategy(str, Enum):
    """How a role vacancy can be filled."""

    INTERNAL_MOVE = "internal_move"
    INTERNAL_DEVELOP = "internal_develop"
    EXTERNAL_HIRE = "external_hire"
    INTERIM = "interim"


class DimensionScore(BaseModel):
    """A single dimension score with metadata."""

    dimension: str
    raw_score: float = Field(ge=0.0, le=10.0)
    corrected_score: float | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_interval: tuple[float, float] | None = None
    source_count: int = 1


class NexusBaseResponse(BaseModel):
    """Base response for all NEXUS API and agent outputs."""

    agent: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

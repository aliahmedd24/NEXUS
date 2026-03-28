"""Brief schemas: decision briefs, dissens reports, and trade-offs."""

from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.common import ConfidenceLevel


class TradeOffEntry(BaseModel):
    """One trade-off in a decision brief."""

    dimension: str
    option_a: str = ""
    option_b: str = ""
    impact_description: str = ""
    recommendation: str = ""


class DissensReport(BaseModel):
    """Mandatory dissenting opinion in STAFF briefs.

    Forces the system to articulate the strongest counter-argument
    to the primary recommendation, preventing groupthink.
    """

    dissenting_position: str = ""
    supporting_evidence: list[str] = Field(default_factory=list)
    risk_if_ignored: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class DecisionBrief(BaseModel):
    """Complete decision brief for executive review."""

    brief_id: UUID | None = None
    title: str = ""
    executive_summary: str = ""
    recommendation: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    trade_offs: list[TradeOffEntry] = Field(default_factory=list)
    dissens: DissensReport | None = None
    key_risks: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    generated_by: list[str] = Field(default_factory=list)

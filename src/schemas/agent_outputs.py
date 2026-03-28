"""Pydantic output schemas for every NEXUS agent.

These are used as output_schema on LlmAgent to force structured responses.
The LLM returns JSON matching these schemas, which ADK auto-validates.
"""

from pydantic import BaseModel, Field


# ─── DIAGNOSE Mode Outputs ───────────────────────────────────────────


class ScenarioAnalysisOutput(BaseModel):
    """Output schema for Scenario Architect Agent."""

    scenario_id: str
    scenario_name: str
    category: str
    narrative_summary: str = Field(
        description="2-3 sentence business impact summary"
    )
    probability: float = Field(ge=0.0, le=1.0)
    top_capability_demands: list[str] = Field(
        description="Top 3 capability dimensions that spike in demand",
        min_length=1,
        max_length=5,
    )
    affected_org_units: list[str] = Field(
        description="Names of most affected organizational units",
    )
    recommendation: str = Field(
        description="Recommended next action for the decision-maker",
    )


class VulnerabilityHeatmapCell(BaseModel):
    """One cell in the vulnerability heatmap."""

    role_id: str = Field(description="UUID of the role — needed by cascade_modeler")
    role_title: str
    leader_name: str | None = None
    gap_score: float = Field(ge=0.0, le=1.0)
    status: str = Field(description="green, yellow, or red")
    top_gap_dimensions: list[str] = []
    bench_strength: int = Field(ge=0)


class VulnerabilityReportOutput(BaseModel):
    """Output schema for Vulnerability Scanner Agent."""

    scenario_id: str = Field(description="UUID of the scenario — needed by cascade_modeler")
    scenario_name: str
    aggregate_resilience_score: float = Field(ge=0.0, le=1.0)
    critical_count: int
    warning_count: int
    covered_count: int
    heatmap: list[VulnerabilityHeatmapCell]
    single_points_of_failure: list[str] = Field(
        description="Leaders who are sole holders of critical capabilities",
    )
    priority_actions: list[str] = Field(
        description="Top 3 recommended actions based on the vulnerability scan",
    )


class CascadeNodeOutput(BaseModel):
    """One node in a cascade chain."""

    org_unit_name: str
    impact_type: str
    severity_description: str
    estimated_cost_eur: float = 0


class CascadeReportOutput(BaseModel):
    """Output schema for Cascade Modeler Agent."""

    trigger_role: str
    trigger_scenario: str
    cascade_chain: list[CascadeNodeOutput]
    total_exposure_eur: float
    production_units_at_risk: int = 0
    delay_days_estimated: int = 0
    optimal_intervention: str = Field(
        description="The single best intervention point and why",
    )
    business_translation: str = Field(
        description="What this cascade means in plain business terms for BMW leadership",
    )


# ─── STAFF Mode Outputs ──────────────────────────────────────────────


class AdaptedJDOutput(BaseModel):
    """Output schema for Dynamic JD Generator Agent."""

    role_type: str
    scenario_name: str
    top_5_requirements: list[dict] = Field(
        description="Top 5 competency requirements ranked by adapted weight",
    )
    key_changes: list[str] = Field(
        description="What changed from the base JD due to the scenario",
    )
    critique_flags: list[str] = Field(
        description="Any issues found: conflicts, unicorn detection, bias",
    )
    estimated_market_pool_size: str = Field(
        description="Estimate: 'abundant (100+)', 'moderate (20-100)', 'scarce (<20)', 'unicorn (<5)'",
    )


class CandidateRankingEntry(BaseModel):
    """One candidate in the ranking."""

    candidate_id: str = Field(description="UUID of the candidate leader — needed by team_chemistry")
    candidate_name: str
    leader_type: str
    overall_fit_score: float = Field(ge=0.0, le=1.0)
    top_strengths: list[str]
    top_gaps: list[str]
    bias_correction_note: str = Field(
        default="",
        description="Note if bias correction significantly changed this candidate's score",
    )


class GenomeAnalysisOutput(BaseModel):
    """Output schema for Leadership Genome Agent."""

    role_type: str
    scenario_name: str
    org_unit_id: str = Field(
        description="UUID of the org unit for the target role — needed by team_chemistry",
    )
    ranked_candidates: list[CandidateRankingEntry]
    bias_detection_summary: str = Field(
        description="Summary of bias corrections applied",
    )
    data_quality_warnings: list[str] = Field(
        description="Dimensions or candidates with insufficient data",
    )


class ChemistryPairOutput(BaseModel):
    """Compatibility between candidate and one team member."""

    team_member_name: str
    synergy_score: float = Field(ge=-1.0, le=1.0)
    key_dynamic: str
    explanation: str


class TeamChemistryOutput(BaseModel):
    """Output schema for Team Chemistry Engine Agent."""

    candidate_name: str
    target_role: str
    overall_team_fit: float = Field(ge=0.0, le=1.0)
    pairwise_assessments: list[ChemistryPairOutput]
    team_balance_changes: list[str] = Field(
        description="What improves or degrades by adding this candidate",
    )
    risk_flags: list[str] = Field(
        description="Specific predicted friction points",
    )
    headline_insight: str = Field(
        description="One sentence: why this candidate is or isn't right for THIS team",
    )


class StaffingRecommendation(BaseModel):
    """One role in the staffing plan."""

    role_title: str
    sourcing_strategy: str
    recommended_candidate: str | None = None
    alternative_candidate: str | None = None
    estimated_cost_eur: float = 0
    estimated_time_days: int = 90
    rationale: str


class PortfolioOptimizerOutput(BaseModel):
    """Output schema for Pipeline & Portfolio Optimizer Agent."""

    staffing_recommendations: list[StaffingRecommendation]
    total_investment_eur: float
    aggregate_resilience_improvement: float = Field(
        description="Percentage improvement in organizational resilience",
    )
    roi_estimate: str = Field(
        description="Return on talent investment: 'For every 1 EUR invested, X EUR in risk reduction'",
    )
    sequencing_rationale: str = Field(
        description="Which hires to make first and why",
    )
    plan_b_summary: str = Field(
        description="What to do if the top candidate declines",
    )


# ─── LEARN Mode Outputs ──────────────────────────────────────────────


class DecisionReplayEntry(BaseModel):
    """One replayed historical decision."""

    role_title: str
    decision_date: str
    selected_candidate: str
    runner_up: str | None = None
    actual_outcome_summary: str
    counterfactual_summary: str
    divergence_category: str
    root_cause: str


class ReplayAnalysisOutput(BaseModel):
    """Output schema for Decision Replay Agent."""

    decisions_analyzed: int
    replays: list[DecisionReplayEntry]
    overall_decision_quality: str = Field(
        description="Summary: 'X of Y decisions were optimal, Z were costly errors'",
    )


class BiasEntry(BaseModel):
    """One detected bias."""

    dimension: str
    direction: str
    magnitude_pct: float
    explanation: str


class LearningReportOutput(BaseModel):
    """Output schema for Pattern Intelligence Agent."""

    bias_mirror: list[BiasEntry] = Field(
        description="Top 2-3 most significant biases with magnitudes",
    )
    success_dna: list[str] = Field(
        description="Top 3 dimensions that predict successful hires",
    )
    failure_signals: list[str] = Field(
        description="Top 3 dimensions that predict failures",
    )
    calibration_updated: bool
    improvement_trend: str = Field(
        description="Has decision quality improved over time?",
    )


# ─── Brief Output ────────────────────────────────────────────────────


class DecisionBriefOutput(BaseModel):
    """Output schema for Decision Brief Generator Agent."""

    mode: str
    title: str
    executive_summary: str = Field(
        description="Maximum 3 sentences",
        max_length=500,
    )
    recommendation: str
    key_evidence: list[str]
    trade_offs: list[str]
    dissent_report: str | None = Field(
        default=None,
        description="Where agents disagreed — MANDATORY for STAFF briefs",
    )
    confidence_level: str
    confidence_reasoning: str
    suggested_next_steps: list[str]

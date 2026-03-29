export interface Scenario {
  id: string;
  name: string;
  category: string;
  narrative: string;
  probability: number;
  capability_demand_vector: Record<string, number>;
  time_horizon_months: number;
  affected_org_units?: string[];
}

export interface HeatmapCell {
  role_id: string;
  role_title: string;
  leader_name: string | null;
  gap_score: number;
  status: 'red' | 'yellow' | 'green';
  gap_dimensions: Record<string, number>;
}

export interface CascadeNode {
  org_unit_id: string;
  org_unit_name: string;
  depth: number;
  impact_score: number;
  dependency_type: string;
  coupling_strength: number;
  mechanical_cost_eur: number;
  estimated_delay_days: number;
}

export interface CascadeReport {
  role_title: string;
  scenario_name: string;
  cascade_direction: string;
  cascade_chain: CascadeNode[];
  mechanical_total_eur: number;
  optimal_intervention: {
    org_unit_id: string;
    impact_blocked_pct: number;
  } | null;
}

export interface DiagnoseResult {
  scenario_name: string;
  heatmap: HeatmapCell[];
  critical_count: number;
  warning_count: number;
  covered_count: number;
  aggregate_resilience_score: number;
  cascades: CascadeReport[];
}

export interface GenomeDimension {
  dimension: string;
  raw_score: number;
  corrected_score: number;
  confidence_interval: [number, number];
  source_count: number;
}

export interface LeaderGenome {
  leader_id: string;
  full_name: string;
  leader_type: string;
  dimensions: GenomeDimension[];
  corrections_applied: Record<string, number>;
  review_count: number;
  feedback_count: number;
  overall_strength: number;
}

export interface CandidateFit {
  leader_id: string;
  full_name: string;
  leader_type: string;
  role_type: string;
  mechanical_fit_score: number;
  dimension_fits: Record<string, number>;
  strengths: { dimension: string; fit: number }[];
  gaps: { dimension: string; fit: number }[];
  calibration_applied: boolean;
}

export interface StaffResult {
  role_type: string;
  scenario_id: string;
  ranking: CandidateFit[];
  chemistry: TeamChemistry | null;
}

export interface PairwiseAssessment {
  team_member_id: string;
  team_member_name: string;
  role_title: string;
  mechanical_synergy_score: number;
  friction_dimensions: string[];
  synergy_dimensions: string[];
}

export interface TeamChemistry {
  candidate_id: string;
  candidate_name: string;
  org_unit_id: string;
  pairwise_assessments: PairwiseAssessment[];
  team_member_count: number;
  mechanical_avg_synergy: number;
  team_balance: {
    composition_score: number;
    diversity_score: number;
    complementarity_score: number;
  };
}

export interface EfficientFrontierPoint {
  budget_eur: number;
  resilience_improvement: number;
  selected_hires: string[];
  roi: number;
}

export interface StaffingPlan {
  plan_items: {
    role_id: string;
    role_title: string;
    recommended_candidate: string;
    fit_score: number;
    mechanical_cost_eur: number;
    sourcing_strategy: string;
  }[];
  total_cost_eur: number;
  budget_eur: number;
  within_budget: boolean;
  efficient_frontier: EfficientFrontierPoint[];
  roi_estimate: Record<string, number>;
}

export interface HistoricalDecision {
  id: string;
  decision_date: string;
  role_id: string;
  role_title: string;
  selected_candidate_id: string;
  selected_name: string;
  runner_up_candidate_id?: string;
  runner_up_name?: string;
  scenario_context: string;
  decision_rationale: string;
  decision_making_dimensions: Record<string, number>;
  outcomes: DecisionOutcome[];
}

export interface DecisionOutcome {
  id: string;
  decision_id: string;
  months_elapsed: number;
  performance_rating: number;
  goal_completion_pct: number;
  team_engagement_delta: number;
  team_attrition_delta: number;
  still_in_role: boolean;
  outcome_category: string;
  quality_of_hire?: number;
}

export interface BiasPattern {
  [dimension: string]: number;
}

export interface DecisionReplay {
  id: string;
  decision_date: string;
  role_id: string;
  selected_candidate_id: string;
  selected_candidate_name: string;
  selected_candidate_genome: Record<string, number>;
  runner_up_candidate_id?: string;
  runner_up_candidate_name?: string;
  runner_up_candidate_genome?: Record<string, number>;
  decision_rationale: string;
  decision_making_dimensions: Record<string, number>;
  outcomes: DecisionOutcome[];
}

export type Mode = 'diagnose' | 'staff' | 'learn';

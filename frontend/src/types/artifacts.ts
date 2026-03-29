import { type Mode } from './api';

export interface ArtifactItem {
  id: string;
  vizType: string;
  toolName: string;
  data: unknown;
  timestamp: number;
  label: string;
}

export interface ArtifactGroup {
  id: string;
  mode: Mode;
  userQuery: string;
  items: ArtifactItem[];
  agentName: string;
  completedAt: number | null;
  createdAt: number;
}

/** Human-readable labels for each visualization type. */
export const VIZ_TYPE_LABELS: Record<string, string> = {
  // DIAGNOSE
  diagnose_heatmap: 'Vulnerability Heatmap',
  diagnose_cascade: 'Cascade Impact Analysis',
  diagnose_spof: 'Single Points of Failure',
  // STAFF
  staff_ranking: 'Candidate Ranking',
  staff_genome: 'Leadership Genome Profile',
  staff_chemistry: 'Team Chemistry Analysis',
  staff_plan: 'Staffing Plan & Frontier',
  staff_fit: 'Individual Candidate Fit',
  // LEARN
  learn_decisions: 'Historical Decisions Timeline',
  learn_biases: 'Bias Pattern Analysis',
  learn_replay: 'Decision Replay',
  learn_outcomes: 'Decision Outcomes',
  learn_counterfactual: 'Counterfactual Simulation',
  learn_calibration: 'Calibration Coefficients',
  learn_calibration_updated: 'Updated Calibration',
};

/** Map viz types back to their pipeline mode. */
export const VIZ_TYPE_TO_MODE: Record<string, Mode> = {
  diagnose_heatmap: 'diagnose',
  diagnose_cascade: 'diagnose',
  diagnose_spof: 'diagnose',
  staff_ranking: 'staff',
  staff_genome: 'staff',
  staff_chemistry: 'staff',
  staff_plan: 'staff',
  staff_fit: 'staff',
  learn_decisions: 'learn',
  learn_biases: 'learn',
  learn_replay: 'learn',
  learn_outcomes: 'learn',
  learn_counterfactual: 'learn',
  learn_calibration: 'learn',
  learn_calibration_updated: 'learn',
};

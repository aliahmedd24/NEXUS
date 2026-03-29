const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  // Scenarios
  getScenarios: () => fetchJSON<any[]>('/api/scenarios'),
  suggestScenarios: (context = '') =>
    fetchJSON<any>(`/api/scenarios/suggest?context=${encodeURIComponent(context)}`),

  // Diagnose
  runDiagnose: (scenarioId?: string, scenarioName?: string) =>
    fetchJSON<any>('/api/diagnose/run', {
      method: 'POST',
      body: JSON.stringify({ scenario_id: scenarioId, scenario_name: scenarioName }),
    }),
  createCompound: (scenarioNameA: string, scenarioNameB: string) =>
    fetchJSON<any>('/api/diagnose/compound', {
      method: 'POST',
      body: JSON.stringify({ scenario_a_name: scenarioNameA, scenario_b_name: scenarioNameB }),
    }),
  getCascade: (roleId: string, scenarioId: string) =>
    fetchJSON<any>(`/api/diagnose/cascade/${roleId}?scenario_id=${scenarioId}`),

  // Staff
  runStaff: (roleType: string, scenarioId = '', orgUnitId = '') =>
    fetchJSON<any>('/api/staff/run', {
      method: 'POST',
      body: JSON.stringify({ role_type: roleType, scenario_id: scenarioId, org_unit_id: orgUnitId }),
    }),
  getCandidates: (roleType = '') =>
    fetchJSON<any[]>(`/api/staff/candidates?role_type=${encodeURIComponent(roleType)}`),
  getGenome: (leaderId: string) =>
    fetchJSON<any>(`/api/staff/genome/${leaderId}`),
  getFit: (leaderId: string, roleType: string, scenarioId = '') =>
    fetchJSON<any>(`/api/staff/fit/${leaderId}?role_type=${encodeURIComponent(roleType)}&scenario_id=${scenarioId}`),
  getChemistry: (candidateId: string, orgUnitId: string) =>
    fetchJSON<any>(`/api/staff/chemistry`, {
      method: 'POST',
      body: JSON.stringify({ candidate_id: candidateId, org_unit_id: orgUnitId }),
    }),
  getStaffingPlan: (roleIds: string[], scenarioId: string, budgetEur: number) =>
    fetchJSON<any>('/api/staff/plan', {
      method: 'POST',
      body: JSON.stringify({ role_ids: roleIds, scenario_id: scenarioId, budget_eur: budgetEur }),
    }),

  // Learn
  getDecisions: (limit = 10) =>
    fetchJSON<any[]>(`/api/learn/decisions?limit=${limit}`),
  replayDecision: (decisionId: string) =>
    fetchJSON<any>(`/api/learn/replay/${decisionId}`),
  getOutcomes: (decisionId: string) =>
    fetchJSON<any>(`/api/learn/outcomes/${decisionId}`),
  getBiases: () => fetchJSON<any>('/api/learn/biases'),
  getCalibration: () => fetchJSON<any>('/api/learn/calibration'),
  runLearn: () => fetchJSON<any>('/api/learn/run', { method: 'POST' }),

  // Chat / Agent
  createSession: () => fetchJSON<{ session_id: string }>('/api/chat/session', { method: 'POST' }),
  sendMessage: (message: string, sessionId: string, mode?: string) =>
    fetch(`${API_BASE}/api/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId, mode }),
    }),

  // Health
  health: () => fetchJSON<any>('/health'),
};

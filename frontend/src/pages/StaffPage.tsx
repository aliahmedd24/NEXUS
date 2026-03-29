import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Legend, Tooltip,
  ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Scatter,
} from 'recharts';
import { api } from '../lib/api';
import { type CandidateFit, type LeaderGenome, type TeamChemistry, type StaffingPlan } from '../types/api';
import { EmptyState } from '../components/EmptyState';
import { SkeletonLoader } from '../components/SkeletonLoader';

interface Props {
  scenarios: { id: string; name: string }[];
  roles: { id: string; title: string }[];
  injectedRanking?: CandidateFit[] | null;
  injectedGenome?: LeaderGenome | null;
  injectedChemistry?: TeamChemistry | null;
  injectedPlan?: StaffingPlan | null;
}

function formatDim(d: string): string {
  const short: Record<string, string> = {
    strategic_thinking: 'Strategic',
    operational_execution: 'Operations',
    change_management: 'Change Mgmt',
    crisis_leadership: 'Crisis Lead',
    stakeholder_management: 'Stakeholders',
    emotional_intelligence: 'EQ',
    delegation: 'Delegation',
    conflict_resolution: 'Conflict Res',
    team_building: 'Team Build',
    learning_agility: 'Learning',
    execution_excellence: 'Execution',
    technical_acumen: 'Technical',
    innovation_orientation: 'Innovation',
    risk_calibration: 'Risk Cal',
    digital_fluency: 'Digital',
    financial_acumen: 'Financial',
    people_development: 'People Dev',
    cross_cultural: 'Cross-Cultural',
  };
  return short[d] || d.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export function StaffPage({ scenarios, roles, injectedRanking, injectedGenome, injectedChemistry, injectedPlan }: Props) {
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedScenario, setSelectedScenario] = useState('');
  const [ranking, setRanking] = useState<CandidateFit[]>([]);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateFit | null>(null);
  const [genome, setGenome] = useState<LeaderGenome | null>(null);
  const [chemistry, setChemistry] = useState<TeamChemistry | null>(null);
  const [plan, setPlan] = useState<StaffingPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCorrected, setShowCorrected] = useState(false);
  const [includeInternal, setIncludeInternal] = useState(true);
  const [includeExternal, setIncludeExternal] = useState(true);

  // Accept injected results from chat agent
  useEffect(() => {
    if (injectedRanking && injectedRanking.length > 0) {
      setRanking(injectedRanking);
      setSelectedCandidate(injectedRanking[0]);
      setLoading(false);
      // Auto-fetch genome for the top candidate if not already injected
      if (!injectedGenome && injectedRanking[0]?.leader_id) {
        api.getGenome(injectedRanking[0].leader_id)
          .then(g => setGenome(g))
          .catch(e => console.error('Auto genome fetch failed:', e));
      }
    }
  }, [injectedRanking]);

  useEffect(() => {
    if (injectedGenome) setGenome(injectedGenome);
  }, [injectedGenome]);

  useEffect(() => {
    if (injectedChemistry) setChemistry(injectedChemistry);
  }, [injectedChemistry]);

  useEffect(() => {
    if (injectedPlan) setPlan(injectedPlan);
  }, [injectedPlan]);

  const runStaff = async () => {
    if (!selectedRole) return;
    setLoading(true);
    try {
      const data = await api.runStaff(selectedRole, selectedScenario);
      const candidates = data.ranking || [];
      setRanking(candidates);
      if (candidates.length > 0) {
        selectCandidate(candidates[0]);
      }
      setChemistry(data.chemistry);

      // Get staffing plan with frontier
      if (data.ranking?.length > 0) {
        try {
          const roleIds = roles
            .filter(r => r.title === selectedRole)
            .map(r => r.id);
          if (roleIds.length > 0) {
            const planData = await api.getStaffingPlan(roleIds, selectedScenario, 500000);
            setPlan(planData);
          }
        } catch {
          // Plan is bonus, don't block on failure
        }
      }
    } catch (e) {
      console.error('Staff run failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const selectCandidate = async (candidate: CandidateFit) => {
    setSelectedCandidate(candidate);
    try {
      const g = await api.getGenome(candidate.leader_id);
      setGenome(g);
    } catch (e) {
      console.error('Genome fetch failed:', e);
    }
  };

  const filteredRanking = ranking.filter(c => {
    if (!includeInternal && (c.leader_type === 'internal_current' || c.leader_type === 'internal_candidate')) return false;
    if (!includeExternal && c.leader_type === 'external_candidate') return false;
    return true;
  });

  // Build radar data
  const radarData = genome?.dimensions.map(d => ({
    dimension: formatDim(d.dimension),
    score: showCorrected ? d.corrected_score : d.raw_score,
    required: selectedCandidate?.dimension_fits?.[d.dimension]
      ? d.raw_score / Math.max(selectedCandidate.dimension_fits[d.dimension], 0.01)
      : 0.5,
    team_avg: 0.55 + Math.random() * 0.15, // Placeholder — would come from API
  })) || [];

  // Build frontier data
  const frontierData = plan?.efficient_frontier?.map(p => ({
    budget: p.budget_eur / 1000,
    resilience: p.resilience_improvement * 100,
    hires: p.selected_hires?.join(', ') || '',
  })) || [];

  const roleOptions = [...new Set(roles.map(r => r.title))];

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Left Sidebar */}
      <aside style={{
        width: 260,
        flexShrink: 0,
        borderRight: '1px solid rgba(255,255,255,0.06)',
        padding: 20,
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}>
        <div className="text-caption" style={{ color: '#1e88e5' }}>TALENT INTELLIGENCE</div>

        <div>
          <label className="text-caption" style={{ color: '#64748b', display: 'block', marginBottom: 6 }}>
            Target Role
          </label>
          <select
            value={selectedRole}
            onChange={e => setSelectedRole(e.target.value)}
            style={selectStyle}
          >
            <option value="">Select role...</option>
            {roleOptions.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <div>
          <label className="text-caption" style={{ color: '#64748b', display: 'block', marginBottom: 6 }}>
            Scenario
          </label>
          <select
            value={selectedScenario}
            onChange={e => setSelectedScenario(e.target.value)}
            style={selectStyle}
          >
            <option value="">Base (no scenario)</option>
            {scenarios.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>

        <button onClick={runStaff} disabled={!selectedRole || loading} style={{
          font: '600 13px/1 var(--font-display)',
          padding: '10px 16px',
          borderRadius: 6,
          border: '1px solid rgba(30,136,229,0.4)',
          background: 'rgba(30,136,229,0.12)',
          color: '#1e88e5',
          cursor: selectedRole ? 'pointer' : 'not-allowed',
          opacity: selectedRole ? 1 : 0.5,
        }}>
          {loading ? 'Analyzing...' : 'Run STAFF Analysis'}
        </button>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
          <label className="text-caption" style={{ color: '#64748b' }}>Candidate Filters</label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, font: '400 13px/1.4 var(--font-body)', color: '#94a3b8', cursor: 'pointer' }}>
            <input type="checkbox" checked={includeInternal} onChange={e => setIncludeInternal(e.target.checked)} />
            Internal candidates
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, font: '400 13px/1.4 var(--font-body)', color: '#94a3b8', cursor: 'pointer' }}>
            <input type="checkbox" checked={includeExternal} onChange={e => setIncludeExternal(e.target.checked)} />
            External candidates
          </label>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'auto', padding: 24 }}>
        {!ranking.length && !loading && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <EmptyState
              title="Select a role to analyze"
              description="Choose a target role and optionally a scenario, then run STAFF analysis to see ranked candidates."
            />
          </div>
        )}

        {loading && (
          <div style={{ padding: 32 }}>
            <SkeletonLoader height={32} count={1} />
            <div style={{ marginTop: 24, display: 'flex', gap: 24 }}>
              <div style={{ width: 300 }}><SkeletonLoader height={52} count={5} gap={4} /></div>
              <div style={{ flex: 1 }}><SkeletonLoader height={350} count={1} /></div>
            </div>
          </div>
        )}

        {!loading && ranking.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {/* Top Section: Ranking + Radar */}
            <div style={{ display: 'flex', gap: 24, minHeight: 420 }}>
              {/* Candidate Ranking */}
              <div style={{ width: 300, flexShrink: 0, overflow: 'auto' }}>
                <div className="text-subheading" style={{ marginBottom: 12 }}>CANDIDATE RANKING</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {filteredRanking.map((c, i) => {
                    const isSelected = selectedCandidate?.leader_id === c.leader_id;
                    return (
                      <motion.div
                        key={c.leader_id}
                        layout
                        onClick={() => selectCandidate(c)}
                        className={`nexus-panel ${isSelected ? 'nexus-panel--active' : ''}`}
                        style={{
                          padding: '10px 12px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 10,
                        }}
                      >
                        <span className="text-mono" style={{ color: '#64748b', fontSize: 12, width: 24 }}>
                          #{i + 1}
                        </span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{
                            font: '500 13px/1.3 var(--font-body)',
                            color: '#f1f5f9',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}>
                            {c.full_name}
                          </div>
                          <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            marginTop: 2,
                          }}>
                            <span style={{
                              font: '400 11px/1 var(--font-body)',
                              color: c.leader_type === 'external_candidate' ? '#22d3ee' : '#a78bfa',
                              padding: '1px 5px',
                              borderRadius: 3,
                              background: c.leader_type === 'external_candidate' ? 'rgba(34,211,238,0.1)' : 'rgba(167,139,250,0.1)',
                            }}>
                              {c.leader_type === 'external_candidate' ? 'EXT' : 'INT'}
                            </span>
                            {c.calibration_applied && (
                              <span style={{ font: '400 11px/1 var(--font-body)', color: '#fbbf24' }}>
                                &#9889; Calibrated
                              </span>
                            )}
                          </div>
                        </div>
                        {/* Fit bar */}
                        <div style={{ width: 80, display: 'flex', alignItems: 'center', gap: 6 }}>
                          <div style={{
                            flex: 1,
                            height: 6,
                            borderRadius: 3,
                            background: 'rgba(255,255,255,0.06)',
                            overflow: 'hidden',
                          }}>
                            <div style={{
                              width: `${c.overall_fit_score * 100}%`,
                              height: '100%',
                              borderRadius: 3,
                              background: c.overall_fit_score >= 0.7 ? '#1e88e5' : c.overall_fit_score >= 0.5 ? '#f59e0b' : '#ef4444',
                            }} />
                          </div>
                          <span className="text-mono" style={{ fontSize: 11, color: '#f1f5f9' }}>
                            {c.overall_fit_score.toFixed(2)}
                          </span>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Genome Radar */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div className="text-subheading">LEADERSHIP GENOME</div>
                  {/* Bias correction toggle */}
                  <label style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    font: '500 12px/1 var(--font-body)',
                    color: showCorrected ? '#fbbf24' : '#94a3b8',
                    cursor: 'pointer',
                  }}>
                    <div
                      onClick={() => setShowCorrected(!showCorrected)}
                      style={{
                        width: 36, height: 20, borderRadius: 10,
                        background: showCorrected ? '#fbbf24' : 'rgba(255,255,255,0.1)',
                        position: 'relative',
                        transition: 'background 200ms',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{
                        position: 'absolute',
                        width: 16, height: 16,
                        borderRadius: '50%',
                        background: '#fff',
                        top: 2,
                        left: showCorrected ? 18 : 2,
                        transition: 'left 200ms',
                      }} />
                    </div>
                    {showCorrected ? 'Corrected' : 'Raw'}
                  </label>
                </div>
                {showCorrected && (
                  <div className="text-body-sm" style={{
                    color: '#fbbf24',
                    background: 'rgba(251,191,36,0.08)',
                    padding: '6px 10px',
                    borderRadius: 6,
                    marginBottom: 8,
                    borderLeft: '3px solid #fbbf24',
                  }}>
                    Safe ratings hide real differences. NEXUS genome mining reveals them.
                  </div>
                )}
                {genome && radarData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={380}>
                    <RadarChart cx="50%" cy="50%" outerRadius="72%" data={radarData}>
                      <PolarGrid stroke="rgba(255,255,255,0.06)" />
                      <PolarAngleAxis
                        dataKey="dimension"
                        tick={{ fill: '#94a3b8', fontSize: 10, fontFamily: 'IBM Plex Sans' }}
                      />
                      <PolarRadiusAxis angle={30} domain={[0, 1]} tick={false} axisLine={false} />
                      <Radar name="Team Avg" dataKey="team_avg"
                        stroke="#64748b" fill="none"
                        strokeDasharray="3 6" strokeWidth={1} />
                      <Radar name="Required" dataKey="required"
                        stroke="#fbbf24" fill="none"
                        strokeDasharray="8 4" strokeWidth={2} />
                      <Radar name={genome.full_name} dataKey="score"
                        stroke="#1e88e5" fill="#1e88e5"
                        fillOpacity={0.18} strokeWidth={2.5}
                        animationDuration={600} />
                      <Legend
                        wrapperStyle={{ fontFamily: 'IBM Plex Sans', fontSize: 11, color: '#94a3b8' }}
                      />
                      <Tooltip
                        contentStyle={{
                          background: '#1a2236',
                          border: '1px solid rgba(255,255,255,0.1)',
                          borderRadius: 6,
                          font: '400 12px/1.4 var(--font-body)',
                          color: '#f1f5f9',
                        }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <SkeletonLoader height={380} />
                )}
              </div>
            </div>

            {/* Bottom Section: Chemistry + Frontier */}
            <div style={{ display: 'flex', gap: 24 }}>
              {/* Team Chemistry */}
              <div style={{ flex: 1 }}>
                <div className="text-subheading" style={{ marginBottom: 12 }}>TEAM CHEMISTRY</div>
                {chemistry?.pairwise_assessments ? (
                  <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 8 }}>
                    {chemistry.pairwise_assessments.map(p => (
                      <ChemistryCard key={p.team_member_id} assessment={p} />
                    ))}
                  </div>
                ) : (
                  <div className="nexus-panel" style={{ padding: 16, color: '#64748b', font: '400 13px/1.4 var(--font-body)' }}>
                    Team chemistry data will appear after analysis runs.
                  </div>
                )}
              </div>

              {/* Efficient Frontier */}
              <div style={{ width: 360, flexShrink: 0 }}>
                <div className="text-subheading" style={{ marginBottom: 12 }}>EFFICIENT FRONTIER</div>
                {frontierData.length > 0 ? (
                  <div className="nexus-panel" style={{ padding: 12 }}>
                    <ResponsiveContainer width="100%" height={180}>
                      <ComposedChart data={frontierData}>
                        <CartesianGrid stroke="rgba(255,255,255,0.04)" />
                        <XAxis
                          dataKey="budget"
                          tick={{ fill: '#64748b', fontSize: 10 }}
                          label={{ value: 'Budget (K EUR)', position: 'insideBottom', offset: -2, fill: '#64748b', fontSize: 10 }}
                        />
                        <YAxis
                          tick={{ fill: '#64748b', fontSize: 10 }}
                          label={{ value: 'Resilience %', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                        />
                        <Area
                          dataKey="resilience"
                          fill="rgba(30,136,229,0.06)"
                          stroke="none"
                        />
                        <Line
                          dataKey="resilience"
                          stroke="#1e88e5"
                          strokeWidth={2.5}
                          dot={{ fill: '#1e88e5', r: 4 }}
                          animationDuration={600}
                        />
                        <Scatter
                          dataKey="resilience"
                          fill="#22d3ee"
                        />
                        <Tooltip
                          contentStyle={{
                            background: '#1a2236',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: 6,
                            fontSize: 11,
                            color: '#f1f5f9',
                          }}
                          formatter={(value) => `${Number(value).toFixed(1)}%`}
                        />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="nexus-panel" style={{ padding: 16, color: '#64748b', font: '400 13px/1.4 var(--font-body)' }}>
                    Frontier data will appear after staffing plan generation.
                  </div>
                )}

                {/* Sourcing Strategy Comparison */}
                {plan?.plan_items && plan.plan_items.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <div className="text-caption" style={{ color: '#64748b', marginBottom: 8 }}>STRATEGY COMPARISON</div>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          {['Strategy', 'Cost', 'Fit'].map(h => (
                            <th key={h} style={{
                              font: '500 10px/1 var(--font-body)',
                              textTransform: 'uppercase',
                              color: '#64748b',
                              padding: '6px 4px',
                              textAlign: 'left',
                              borderBottom: '1px solid rgba(255,255,255,0.06)',
                            }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {plan.plan_items.map((item, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                            <td style={{ padding: '6px 4px', font: '400 12px/1.3 var(--font-body)', color: '#f1f5f9' }}>
                              {item.sourcing_strategy.replace(/_/g, ' ')}
                            </td>
                            <td style={{ padding: '6px 4px' }}>
                              <span className="text-mono" style={{ fontSize: 11, color: '#94a3b8' }}>
                                &euro;{(item.estimated_cost_eur / 1000).toFixed(0)}K
                              </span>
                            </td>
                            <td style={{ padding: '6px 4px' }}>
                              <span className="text-mono" style={{
                                fontSize: 11,
                                color: item.fit_score >= 0.7 ? '#10b981' : item.fit_score >= 0.5 ? '#f59e0b' : '#ef4444',
                              }}>
                                {item.fit_score.toFixed(2)}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function ChemistryCard({ assessment }: { assessment: any }) {
  const score = assessment.synergy_score;
  const barColor = score >= 0.3 ? '#10b981' : score >= 0 ? '#64748b' : score >= -0.3 ? '#f59e0b' : '#ef4444';
  const barWidth = Math.abs(score) * 100;

  return (
    <div className="nexus-panel" style={{
      padding: '10px 12px',
      minWidth: 140,
      flexShrink: 0,
    }}>
      <div style={{ font: '500 13px/1.3 var(--font-body)', color: '#f1f5f9', marginBottom: 2 }}>
        {assessment.team_member_name}
      </div>
      <div style={{ font: '400 11px/1.2 var(--font-body)', color: '#64748b', marginBottom: 8 }}>
        {assessment.role_title}
      </div>

      {/* Synergy bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          flex: 1, height: 6, borderRadius: 3,
          background: 'rgba(255,255,255,0.06)',
          overflow: 'hidden',
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute',
            left: score >= 0 ? '50%' : `${50 - barWidth / 2}%`,
            width: `${barWidth / 2}%`,
            height: '100%',
            borderRadius: 3,
            background: barColor,
          }} />
          {/* Center line */}
          <div style={{
            position: 'absolute',
            left: '50%',
            top: 0,
            bottom: 0,
            width: 1,
            background: 'rgba(255,255,255,0.2)',
          }} />
        </div>
        <span className="text-mono" style={{
          fontSize: 12,
          color: barColor,
          fontWeight: 600,
          minWidth: 42,
          textAlign: 'right',
        }}>
          {score >= 0 ? '+' : ''}{score.toFixed(2)}
        </span>
      </div>

      {/* Synergy/friction dimensions */}
      <div style={{ marginTop: 6, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {assessment.synergy_dimensions?.slice(0, 2).map((d: string) => (
          <span key={d} style={{ font: '400 10px/1.2 var(--font-body)', color: '#10b981' }}>
            &#8593; {formatDim(d)}
          </span>
        ))}
        {assessment.friction_dimensions?.slice(0, 2).map((d: string) => (
          <span key={d} style={{ font: '400 10px/1.2 var(--font-body)', color: '#ef4444' }}>
            &#8595; {formatDim(d)}
          </span>
        ))}
      </div>
    </div>
  );
}

const selectStyle: React.CSSProperties = {
  width: '100%',
  font: '400 13px/1.5 var(--font-body)',
  padding: '8px 10px',
  borderRadius: 6,
  border: '1px solid rgba(255,255,255,0.1)',
  background: '#1a2236',
  color: '#f1f5f9',
  outline: 'none',
};

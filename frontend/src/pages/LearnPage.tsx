import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { api } from '../lib/api';
import { type HistoricalDecision, type DecisionReplay, type BiasPattern } from '../types/api';
import { SkeletonLoader } from '../components/SkeletonLoader';

function formatDim(d: string): string {
  return d.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getVerdictColor(category: string): string {
  if (category === 'optimal' || category === 'success') return '#10b981';
  if (category === 'suboptimal' || category === 'misstep') return '#f59e0b';
  return '#ef4444';
}

function getVerdictLabel(category: string): string {
  if (category === 'optimal' || category === 'success') return 'OPTIMAL';
  if (category === 'suboptimal' || category === 'misstep') return 'SUBOPTIMAL';
  if (category === 'costly_error') return 'COSTLY ERROR';
  return 'CRITICAL MISS';
}

interface Props {
  injectedDecisions?: HistoricalDecision[] | null;
  injectedBiases?: BiasPattern | null;
  injectedReplay?: DecisionReplay | null;
}

export function LearnPage({ injectedDecisions, injectedBiases, injectedReplay }: Props = {}) {
  const [decisions, setDecisions] = useState<HistoricalDecision[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<HistoricalDecision | null>(null);
  const [replay, setReplay] = useState<DecisionReplay | null>(null);
  const [biases, setBiases] = useState<BiasPattern | null>(null);
  const [loading, setLoading] = useState(true);
  const [calibrating, setCalibrating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // Accept injected results from chat agent
  useEffect(() => {
    if (injectedDecisions && injectedDecisions.length > 0) {
      setDecisions(injectedDecisions);
      setSelectedDecision(injectedDecisions[0]);
      setLoading(false);
    }
  }, [injectedDecisions]);

  useEffect(() => {
    if (injectedBiases) setBiases(injectedBiases);
  }, [injectedBiases]);

  useEffect(() => {
    if (injectedReplay) setReplay(injectedReplay);
  }, [injectedReplay]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [decisionsData, biasData] = await Promise.all([
        api.getDecisions(),
        api.getBiases(),
      ]);
      setDecisions(decisionsData);
      setBiases(biasData);
      if (decisionsData.length > 0) {
        handleSelectDecision(decisionsData[0]);
      }
    } catch (e) {
      console.error('Learn data load failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDecision = async (decision: HistoricalDecision) => {
    setSelectedDecision(decision);
    try {
      const replayData = await api.replayDecision(decision.id);
      setReplay(replayData);
    } catch (e) {
      console.error('Replay failed:', e);
    }
  };

  const handleCalibrate = async () => {
    setCalibrating(true);
    try {
      const result = await api.runLearn();
      setBiases(result.biases);
    } catch (e) {
      console.error('Calibration failed:', e);
    } finally {
      setCalibrating(false);
    }
  };

  // Bias mirror data
  const biasData = biases
    ? Object.entries(biases)
        .map(([dim, value]) => ({
          dimension: formatDim(dim),
          value: typeof value === 'number' ? value * 100 : 0,
          raw: typeof value === 'number' ? value : 0,
        }))
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    : [];

  // Determine primary outcome category for each decision
  const getDecisionVerdict = (d: HistoricalDecision): string => {
    if (!d.outcomes || d.outcomes.length === 0) return 'unknown';
    const latest = d.outcomes.reduce((a, b) => a.months_elapsed > b.months_elapsed ? a : b);
    return latest.outcome_category || 'unknown';
  };

  if (loading) {
    return (
      <div style={{ padding: 32 }}>
        <SkeletonLoader height={32} count={1} />
        <div style={{ marginTop: 24, display: 'flex', gap: 24 }}>
          <div style={{ width: 300 }}><SkeletonLoader height={52} count={6} gap={4} /></div>
          <div style={{ flex: 1 }}><SkeletonLoader height={300} count={1} /></div>
        </div>
      </div>
    );
  }

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
        <div className="text-caption" style={{ color: '#a78bfa' }}>DECISION REPLAY</div>

        <button
          onClick={handleCalibrate}
          disabled={calibrating}
          style={{
            font: '600 12px/1 var(--font-display)',
            padding: '8px 14px',
            borderRadius: 6,
            border: '1px solid rgba(167,139,250,0.4)',
            background: 'rgba(167,139,250,0.1)',
            color: '#a78bfa',
            cursor: calibrating ? 'wait' : 'pointer',
          }}
        >
          {calibrating ? 'Calibrating...' : 'Run Calibration'}
        </button>

        <div className="text-body-sm" style={{ color: '#64748b' }}>
          {decisions.length} historical decisions loaded
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'auto', padding: 24 }}>
        <div style={{ display: 'flex', gap: 24, minHeight: 320 }}>
          {/* Decision Timeline */}
          <div style={{ width: 300, flexShrink: 0 }}>
            <div className="text-subheading" style={{ marginBottom: 12 }}>DECISION TIMELINE</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {decisions.map((d, i) => {
                const verdict = getDecisionVerdict(d);
                const isSelected = selectedDecision?.id === d.id;
                const verdictColor = getVerdictColor(verdict);
                return (
                  <div
                    key={d.id}
                    onClick={() => handleSelectDecision(d)}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 12,
                      cursor: 'pointer',
                      padding: '10px 12px',
                      borderRadius: 6,
                      background: isSelected ? 'rgba(167,139,250,0.06)' : 'transparent',
                      borderLeft: isSelected ? '3px solid #a78bfa' : '3px solid transparent',
                      transition: 'all 150ms',
                    }}
                  >
                    {/* Timeline dot + line */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 16, flexShrink: 0 }}>
                      <div style={{
                        width: verdict.includes('critical') || verdict.includes('costly') ? 14 : 10,
                        height: verdict.includes('critical') || verdict.includes('costly') ? 14 : 10,
                        borderRadius: '50%',
                        background: verdictColor,
                        border: verdict.includes('critical') || verdict.includes('costly')
                          ? `2px solid ${verdictColor}`
                          : 'none',
                        flexShrink: 0,
                        marginTop: 4,
                      }} />
                      {i < decisions.length - 1 && (
                        <div style={{ width: 1, height: 24, background: 'rgba(255,255,255,0.06)' }} />
                      )}
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div className="text-mono" style={{ fontSize: 10, color: '#64748b' }}>
                        {d.decision_date?.slice(0, 10)}
                      </div>
                      <div style={{
                        font: '500 13px/1.3 var(--font-body)',
                        color: '#f1f5f9',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {d.role_title}
                      </div>
                      <span style={{
                        font: '600 10px/1 var(--font-mono)',
                        color: verdictColor,
                        textTransform: 'uppercase',
                      }}>
                        {getVerdictLabel(verdict)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Replay Detail */}
          <div style={{ flex: 1 }}>
            {selectedDecision && replay && (
              <motion.div
                key={selectedDecision.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="text-subheading" style={{ marginBottom: 12 }}>REPLAY DETAIL</div>
                <div className="nexus-panel" style={{ padding: 20 }}>
                  <div className="text-heading" style={{ color: '#f1f5f9', marginBottom: 4 }}>
                    {selectedDecision.role_title}
                  </div>
                  <div className="text-mono" style={{ fontSize: 11, color: '#64748b', marginBottom: 16 }}>
                    {selectedDecision.decision_date?.slice(0, 10)}
                  </div>

                  {/* Selected vs Runner-up */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                    <CandidateCard
                      label="SELECTED"
                      name={replay.selected_candidate_name || selectedDecision.selected_name}
                      genome={replay.selected_candidate_genome}
                      outcome={selectedDecision.outcomes?.[0]}
                    />
                    {replay.runner_up_candidate_name && (
                      <CandidateCard
                        label="RUNNER-UP"
                        name={replay.runner_up_candidate_name}
                        genome={replay.runner_up_candidate_genome}
                        isRunnerUp
                      />
                    )}
                  </div>

                  {/* Rationale */}
                  <div style={{ marginBottom: 16 }}>
                    <div className="text-caption" style={{ color: '#64748b', marginBottom: 6 }}>RATIONALE</div>
                    <div className="text-body-sm" style={{ color: '#94a3b8' }}>
                      {selectedDecision.decision_rationale || replay.decision_rationale || 'No rationale recorded.'}
                    </div>
                  </div>

                  {/* Verdict */}
                  {selectedDecision.outcomes?.length > 0 && (() => {
                    const verdict = getDecisionVerdict(selectedDecision);
                    return (
                      <div style={{
                        padding: '10px 14px',
                        borderRadius: 6,
                        border: `1px solid ${getVerdictColor(verdict)}33`,
                        background: `${getVerdictColor(verdict)}0a`,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                      }}>
                        <span style={{ color: getVerdictColor(verdict), fontSize: 16 }}>
                          {verdict === 'optimal' || verdict === 'success' ? '\u2705' : verdict === 'suboptimal' || verdict === 'misstep' ? '\u26A0\uFE0F' : '\u274C'}
                        </span>
                        <span className="text-body-sm" style={{ color: getVerdictColor(verdict), fontWeight: 600 }}>
                          VERDICT: {getVerdictLabel(verdict)}
                        </span>
                      </div>
                    );
                  })()}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Bias Mirror */}
        {biasData.length > 0 && (
          <div style={{ marginTop: 32 }}>
            <div className="text-subheading" style={{ marginBottom: 12 }}>BIAS MIRROR</div>
            <div className="nexus-panel" style={{ padding: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                <span className="text-caption" style={{ color: '#22d3ee' }}>&#9664; Underweighted</span>
                <span className="text-caption" style={{ color: '#ef4444' }}>Overweighted &#9654;</span>
              </div>
              <ResponsiveContainer width="100%" height={Math.max(200, biasData.length * 36)}>
                <BarChart data={biasData} layout="vertical" margin={{ left: 120, right: 40 }}>
                  <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.04)" />
                  <XAxis
                    type="number"
                    tick={{ fill: '#64748b', fontSize: 10 }}
                    domain={['dataMin - 5', 'dataMax + 5']}
                  />
                  <YAxis
                    type="category"
                    dataKey="dimension"
                    tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'IBM Plex Sans' }}
                    width={110}
                  />
                  <ReferenceLine x={0} stroke="rgba(255,255,255,0.15)" strokeWidth={1} />
                  <Tooltip
                    contentStyle={{
                      background: '#1a2236',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 6,
                      fontSize: 12,
                      color: '#f1f5f9',
                    }}
                    formatter={(value) => `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(1)}%`}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} animationDuration={600}>
                    {biasData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={entry.value >= 0 ? '#ef4444' : '#22d3ee'}
                        fillOpacity={0.8}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function CandidateCard({ label, name, genome, outcome, isRunnerUp }: {
  label: string;
  name: string;
  genome?: Record<string, number>;
  outcome?: any;
  isRunnerUp?: boolean;
}) {
  return (
    <div style={{
      padding: 14,
      borderRadius: 8,
      border: `1px solid ${isRunnerUp ? 'rgba(255,255,255,0.06)' : 'rgba(30,136,229,0.2)'}`,
      background: isRunnerUp ? 'rgba(255,255,255,0.02)' : 'rgba(30,136,229,0.04)',
    }}>
      <div className="text-caption" style={{ color: isRunnerUp ? '#64748b' : '#1e88e5', marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ font: '500 14px/1.3 var(--font-body)', color: '#f1f5f9', marginBottom: 8 }}>
        {name}
      </div>
      {genome && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {Object.entries(genome).slice(0, 4).map(([dim, score]) => (
            <span key={dim} className="text-mono" style={{
              fontSize: 10,
              padding: '2px 5px',
              borderRadius: 3,
              background: 'rgba(255,255,255,0.04)',
              color: '#94a3b8',
            }}>
              {formatDim(dim).slice(0, 8)}: {(score as number).toFixed(2)}
            </span>
          ))}
        </div>
      )}
      {outcome && (
        <div style={{ marginTop: 8 }}>
          <span className="text-mono" style={{ fontSize: 11, color: '#94a3b8' }}>
            QoH @ {outcome.months_elapsed}mo: {(outcome.performance_rating / 10).toFixed(2)}
          </span>
        </div>
      )}
    </div>
  );
}

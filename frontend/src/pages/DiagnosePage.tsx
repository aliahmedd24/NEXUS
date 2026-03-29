import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { type DiagnoseResult, type HeatmapCell, type CascadeReport } from '../types/api';
import { DetailSlidePanel } from '../components/DetailSlidePanel';
import { EmptyState } from '../components/EmptyState';
import { SkeletonLoader } from '../components/SkeletonLoader';

interface Props {
  scenarios: { id: string; name: string; probability: number }[];
  onResultReady: (result: DiagnoseResult) => void;
  compoundScenario?: any;
  injectedResult?: DiagnoseResult | null;
  injectedCascade?: CascadeReport | null;
}

function getGapCellColor(gap: number): string {
  if (gap < 0.15) return '#10b981';
  if (gap < 0.35) return '#f59e0b';
  return '#ef4444';
}

function statusBadge(status: string) {
  const colors: Record<string, { bg: string; fg: string }> = {
    red: { bg: 'rgba(239,68,68,0.12)', fg: '#ef4444' },
    yellow: { bg: 'rgba(245,158,11,0.12)', fg: '#f59e0b' },
    green: { bg: 'rgba(16,185,129,0.12)', fg: '#10b981' },
  };
  const c = colors[status] || colors.yellow;
  return (
    <span style={{
      font: '600 11px/1 var(--font-mono)',
      padding: '3px 8px',
      borderRadius: 4,
      background: c.bg,
      color: c.fg,
      textTransform: 'uppercase',
    }}>
      {status === 'red' ? 'CRITICAL' : status === 'yellow' ? 'WARNING' : 'COVERED'}
    </span>
  );
}

export function DiagnosePage({ scenarios, onResultReady, compoundScenario, injectedResult, injectedCascade }: Props) {
  const [selectedScenario, setSelectedScenario] = useState('');
  const [result, setResult] = useState<DiagnoseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedCell, setSelectedCell] = useState<HeatmapCell | null>(null);
  const [cascade, setCascade] = useState<CascadeReport | null>(null);
  const [showCascades, setShowCascades] = useState(true);
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [prevResult, setPrevResult] = useState<DiagnoseResult | null>(null);

  const dimensions = result?.heatmap?.[0]?.gap_dimensions
    ? Object.keys(result.heatmap[0].gap_dimensions)
    : [];

  // Accept injected results from chat agent
  useEffect(() => {
    if (injectedResult) {
      setPrevResult(result);
      setResult(injectedResult);
      onResultReady(injectedResult);
      setLoading(false);
    }
  }, [injectedResult]);

  useEffect(() => {
    if (injectedCascade) {
      setCascade(injectedCascade);
    }
  }, [injectedCascade]);

  useEffect(() => {
    if (compoundScenario) {
      runDiagnose(compoundScenario.id || undefined, compoundScenario.id ? undefined : compoundScenario.name);
    }
  }, [compoundScenario]);

  const runDiagnose = async (scenarioId?: string, scenarioName?: string) => {
    setLoading(true);
    setPrevResult(result);
    try {
      const data = await api.runDiagnose(scenarioId, scenarioName);
      setResult(data);
      onResultReady(data);
    } catch (e) {
      console.error('Diagnose failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioSelect = (id: string) => {
    setSelectedScenario(id);
    setSelectedCell(null);
    setCascade(null);
    runDiagnose(id);
  };

  const handleCellClick = async (cell: HeatmapCell) => {
    if (cell.status !== 'red') return;
    setSelectedCell(cell);
    try {
      const scenarioId = selectedScenario || compoundScenario?.id || '';
      const data = await api.getCascade(cell.role_id, scenarioId);
      setCascade(data);
    } catch (e) {
      console.error('Cascade fetch failed:', e);
    }
  };

  const filteredHeatmap = result?.heatmap
    ?.filter(c => !criticalOnly || c.status === 'red')
    .sort((a, b) => {
      const order = { red: 0, yellow: 1, green: 2 };
      return (order[a.status] ?? 1) - (order[b.status] ?? 1);
    }) || [];

  // Suggested scenarios (top 3 by probability)
  const suggested = [...scenarios].sort((a, b) => b.probability - a.probability).slice(0, 3);

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
        gap: 20,
      }}>
        <div>
          <div className="text-caption" style={{ color: '#ef4444', marginBottom: 12 }}>STRESS TEST</div>

          <label className="text-caption" style={{ color: '#64748b', display: 'block', marginBottom: 6 }}>
            Scenario
          </label>
          <select
            value={selectedScenario}
            onChange={e => handleScenarioSelect(e.target.value)}
            style={{
              width: '100%',
              font: '400 13px/1.5 var(--font-body)',
              padding: '8px 10px',
              borderRadius: 6,
              border: '1px solid rgba(255,255,255,0.1)',
              background: '#1a2236',
              color: '#f1f5f9',
              outline: 'none',
            }}
          >
            <option value="">Select scenario...</option>
            {scenarios.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {/* Suggested Scenarios */}
        {!result && suggested.length > 0 && (
          <div className="nexus-panel" style={{ padding: 12 }}>
            <div className="text-caption" style={{ color: '#22d3ee', marginBottom: 10 }}>
              &#9733; RECOMMENDED
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {suggested.map(s => (
                <button
                  key={s.id}
                  onClick={() => handleScenarioSelect(s.id)}
                  style={{
                    font: '400 12px/1.4 var(--font-body)',
                    padding: '6px 10px',
                    borderRadius: 6,
                    border: '1px solid rgba(255,255,255,0.06)',
                    background: 'rgba(30,136,229,0.06)',
                    color: '#f1f5f9',
                    cursor: 'pointer',
                    textAlign: 'left',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span>{s.name}</span>
                  <span className="text-mono" style={{ color: '#22d3ee', fontSize: 11 }}>
                    {Math.round(s.probability * 100)}%
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <label className="text-caption" style={{ color: '#64748b' }}>Filters</label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, font: '400 13px/1.4 var(--font-body)', color: '#94a3b8', cursor: 'pointer' }}>
            <input type="checkbox" checked={criticalOnly} onChange={e => setCriticalOnly(e.target.checked)} />
            Critical roles only
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, font: '400 13px/1.4 var(--font-body)', color: '#94a3b8', cursor: 'pointer' }}>
            <input type="checkbox" checked={showCascades} onChange={e => setShowCascades(e.target.checked)} />
            Show cascades
          </label>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div className="text-caption" style={{ color: '#64748b' }}>Legend</div>
          <LegendItem color="#ef4444" label="Critical (>35% gap)" />
          <LegendItem color="#f59e0b" label="Warning (15-35%)" />
          <LegendItem color="#10b981" label="Covered (<15%)" />
          <LegendItem color="#374151" label="Vacant" striped />
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'auto', padding: 24, position: 'relative' }}>
        {loading && (
          <div style={{ padding: 32 }}>
            <SkeletonLoader height={32} count={1} />
            <div style={{ marginTop: 24 }}>
              <SkeletonLoader height={44} count={8} gap={4} />
            </div>
          </div>
        )}

        {!loading && !result && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <EmptyState
              title="Select a scenario to begin"
              description="Choose a stress scenario from the sidebar to test your leadership structure against crisis conditions."
            />
          </div>
        )}

        {!loading && result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <div className="text-display-md" style={{ color: '#f1f5f9' }}>
                  Organizational Resilience Map
                </div>
                <div className="text-body-sm" style={{ color: '#94a3b8', marginTop: 4 }}>
                  {result.scenario_name}
                  <span style={{ margin: '0 8px', color: 'rgba(255,255,255,0.1)' }}>|</span>
                  Resilience: <span className="text-mono" style={{
                    color: result.aggregate_resilience_score >= 0.7 ? '#10b981' :
                           result.aggregate_resilience_score >= 0.5 ? '#f59e0b' : '#ef4444'
                  }}>{result.aggregate_resilience_score.toFixed(2)}</span>
                  <span style={{ margin: '0 8px', color: 'rgba(255,255,255,0.1)' }}>|</span>
                  <span style={{ color: '#ef4444' }}>{result.critical_count} Critical</span>
                </div>
              </div>
            </div>

            {/* Heatmap Table */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={thStyle}>Role</th>
                    <th style={thStyle}>Leader</th>
                    {dimensions.map(d => (
                      <th key={d} style={{ ...thStyle, fontSize: 10, maxWidth: 80 }}>
                        {formatDimension(d)}
                      </th>
                    ))}
                    <th style={thStyle}>Gap</th>
                    <th style={thStyle}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {filteredHeatmap.map((cell, rowIdx) => {
                      const prevCell = prevResult?.heatmap?.find(c => c.role_id === cell.role_id);
                      const changed = prevCell && prevCell.status !== cell.status;
                      return (
                        <motion.tr
                          key={cell.role_id}
                          initial={{ opacity: 0 }}
                          animate={{
                            opacity: 1,
                            scale: changed ? [1, 1.02, 1] : 1,
                          }}
                          transition={{ delay: rowIdx * 0.03 }}
                          onClick={() => handleCellClick(cell)}
                          style={{
                            cursor: cell.status === 'red' ? 'pointer' : 'default',
                            borderBottom: '1px solid rgba(255,255,255,0.04)',
                          }}
                        >
                          <td style={{ ...tdStyle, fontWeight: 500, color: '#f1f5f9', maxWidth: 200 }}>
                            {cell.role_title}
                          </td>
                          <td style={{ ...tdStyle, color: cell.leader_name ? '#94a3b8' : '#64748b' }}>
                            {cell.leader_name || (
                              <span style={{ fontStyle: 'italic' }}>Vacant</span>
                            )}
                          </td>
                          {dimensions.map((dim, colIdx) => {
                            const gap = cell.gap_dimensions[dim] || 0;
                            const isVacant = !cell.leader_name;
                            return (
                              <td key={dim} style={tdStyle}>
                                <motion.div
                                  initial={{ opacity: 0 }}
                                  animate={{ opacity: 1 }}
                                  transition={{ delay: rowIdx * 0.03 + colIdx * 0.015 }}
                                  title={`${formatDimension(dim)}: Gap ${gap.toFixed(2)}`}
                                  style={{
                                    width: 36,
                                    height: 22,
                                    borderRadius: 3,
                                    background: isVacant
                                      ? 'repeating-linear-gradient(45deg, #1e293b, #1e293b 3px, #374151 3px, #374151 6px)'
                                      : getGapCellColor(gap),
                                    opacity: isVacant ? 0.5 : Math.max(0.3, 1 - gap * 0.5),
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    font: '500 9px/1 var(--font-mono)',
                                    color: 'rgba(255,255,255,0.8)',
                                  }}
                                >
                                  {!isVacant && (1 - gap).toFixed(2)}
                                </motion.div>
                              </td>
                            );
                          })}
                          <td style={tdStyle}>
                            <span className="text-mono" style={{
                              color: getGapCellColor(cell.gap_score),
                              fontWeight: 600,
                              fontSize: 13,
                            }}>
                              {cell.gap_score.toFixed(2)}
                              {changed && prevCell && (
                                <span style={{ color: '#ef4444', fontSize: 10, marginLeft: 4 }}>
                                  {cell.gap_score > prevCell.gap_score ? '↑' : '↓'}
                                </span>
                              )}
                            </span>
                          </td>
                          <td style={tdStyle}>
                            {statusBadge(cell.status)}
                          </td>
                        </motion.tr>
                      );
                    })}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>

            {/* Inline cascades for RED cells */}
            {showCascades && result.cascades && result.cascades.length > 0 && (
              <div style={{ marginTop: 32 }}>
                <div className="text-subheading" style={{ marginBottom: 16 }}>CASCADE IMPACTS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {result.cascades.map((c, i) => (
                    <div key={i} className="nexus-panel nexus-panel--critical" style={{ padding: 16 }}>
                      <div className="text-heading" style={{ color: '#f1f5f9', marginBottom: 8 }}>
                        {c.role_title} &times; {c.scenario_name}
                      </div>
                      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
                        <div>
                          <span className="text-caption" style={{ color: '#64748b' }}>Total Exposure</span>
                          <div className="score-badge score-badge--critical" style={{ marginTop: 4 }}>
                            &euro;{(c.total_impact_eur / 1_000_000).toFixed(1)}M
                          </div>
                        </div>
                        <div>
                          <span className="text-caption" style={{ color: '#64748b' }}>Chain Length</span>
                          <div className="text-mono-lg" style={{ color: '#f1f5f9', marginTop: 4 }}>
                            {c.cascade_chain.length} units
                          </div>
                        </div>
                        {c.optimal_intervention && (
                          <div>
                            <span className="text-caption" style={{ color: '#64748b' }}>Blocks</span>
                            <div className="score-badge score-badge--success" style={{ marginTop: 4 }}>
                              {Math.round((c.optimal_intervention.impact_blocked_pct || 0) * 100)}% of cascade
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </main>

      {/* Right Detail Panel */}
      <DetailSlidePanel
        open={!!selectedCell && !!cascade}
        onClose={() => { setSelectedCell(null); setCascade(null); }}
        title="Cascade Impact Analysis"
      >
        {cascade && selectedCell && (
          <CascadeDetail cell={selectedCell} cascade={cascade} />
        )}
      </DetailSlidePanel>
    </div>
  );
}

function CascadeDetail({ cell, cascade }: { cell: HeatmapCell; cascade: CascadeReport }) {
  const totalCost = cascade.cascade_chain.reduce((sum, n) => sum + (n.estimated_cost_eur || 0), 0);
  const totalDelay = cascade.cascade_chain.reduce((max, n) => Math.max(max, n.estimated_delay_days || 0), 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <div className="text-body-sm" style={{ color: '#94a3b8' }}>
          {cell.role_title} &times; {cascade.scenario_name}
        </div>
        <div className="text-caption" style={{ color: '#64748b', marginTop: 4 }}>
          {cascade.cascade_direction}
        </div>
      </div>

      {/* Cascade Chain */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {/* Trigger node */}
        <CascadeNodeCard
          name={cell.role_title}
          label="TRIGGER"
          impact={cell.gap_score}
          cost={0}
          isFirst
        />

        {cascade.cascade_chain.map((node, i) => (
          <CascadeNodeCard
            key={i}
            name={node.org_unit_name}
            label={node.dependency_type}
            impact={node.impact_score}
            cost={node.estimated_cost_eur}
            depth={node.depth}
          />
        ))}
      </div>

      {/* Summary */}
      <div style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        paddingTop: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span className="text-caption" style={{ color: '#64748b' }}>TOTAL EXPOSURE</span>
          <span className="score-badge score-badge--critical">
            &euro;{(totalCost / 1_000_000).toFixed(1)}M
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span className="text-caption" style={{ color: '#64748b' }}>MAX DELAY</span>
          <span className="text-mono" style={{ color: '#f1f5f9' }}>{totalDelay} days</span>
        </div>
        {cascade.optimal_intervention && (
          <div style={{
            marginTop: 8,
            padding: 12,
            borderRadius: 6,
            border: '1px solid rgba(16,185,129,0.2)',
            background: 'rgba(16,185,129,0.06)',
          }}>
            <div className="text-caption" style={{ color: '#10b981', marginBottom: 4 }}>OPTIMAL INTERVENTION</div>
            <div className="text-body-sm" style={{ color: '#f1f5f9' }}>
              Fill this role to block {Math.round((cascade.optimal_intervention.impact_blocked_pct || 0) * 100)}% of the cascade.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CascadeNodeCard({ name, label, impact, cost, isFirst }: {
  name: string; label: string; impact: number; cost: number; depth?: number; isFirst?: boolean;
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'stretch' }}>
      {/* Vertical line */}
      <div style={{
        width: 24,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        flexShrink: 0,
      }}>
        <div style={{
          width: 10, height: 10,
          borderRadius: '50%',
          background: isFirst ? '#ef4444' : '#1e88e5',
          flexShrink: 0,
          marginTop: 14,
        }} />
        <div style={{
          width: 2,
          flex: 1,
          background: 'rgba(30,136,229,0.3)',
        }} />
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        padding: '8px 12px',
        marginBottom: 4,
        borderRadius: 6,
        border: '1px solid rgba(255,255,255,0.06)',
        background: isFirst ? 'rgba(239,68,68,0.06)' : 'rgba(30,136,229,0.04)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="text-body-sm" style={{ color: '#f1f5f9', fontWeight: 500 }}>{name}</span>
          <span className="text-caption" style={{
            color: isFirst ? '#ef4444' : '#1e88e5',
            padding: '2px 6px',
            borderRadius: 3,
            background: isFirst ? 'rgba(239,68,68,0.12)' : 'rgba(30,136,229,0.12)',
          }}>
            {label}
          </span>
        </div>
        {!isFirst && (
          <div style={{ display: 'flex', gap: 16, marginTop: 4 }}>
            <span className="text-mono" style={{ fontSize: 11, color: '#94a3b8' }}>
              Impact: {impact.toFixed(2)}
            </span>
            {cost > 0 && (
              <span className="text-mono" style={{ fontSize: 11, color: '#ef4444' }}>
                &euro;{(cost / 1_000_000).toFixed(2)}M
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function LegendItem({ color, label, striped }: { color: string; label: string; striped?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{
        width: 12, height: 12, borderRadius: 2,
        background: striped
          ? `repeating-linear-gradient(45deg, ${color}, ${color} 2px, #1e293b 2px, #1e293b 4px)`
          : color,
      }} />
      <span className="text-body-sm" style={{ color: '#94a3b8' }}>{label}</span>
    </div>
  );
}

function formatDimension(dim: string): string {
  return dim.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

const thStyle: React.CSSProperties = {
  font: '500 11px/1 var(--font-body)',
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: '#64748b',
  padding: '8px 6px',
  textAlign: 'left',
  borderBottom: '1px solid rgba(255,255,255,0.08)',
  whiteSpace: 'nowrap',
};

const tdStyle: React.CSSProperties = {
  padding: '6px',
  font: '400 13px/1.4 var(--font-body)',
  whiteSpace: 'nowrap',
};

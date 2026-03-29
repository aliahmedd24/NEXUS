import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { type ArtifactGroup } from '../types/artifacts';
import { saveAs } from 'file-saver';

interface Props {
  open: boolean;
  onToggle: () => void;
  groups: ArtifactGroup[];
  onRemoveGroup: (id: string) => void;
  onClearAll: () => void;
}

const MODE_COLORS: Record<string, string> = {
  diagnose: '#ef4444',
  staff: '#1e88e5',
  learn: '#a78bfa',
};

const MODE_LABELS: Record<string, string> = {
  diagnose: 'DIAGNOSE',
  staff: 'STAFF',
  learn: 'LEARN',
};

export function ArtifactsPanel({ open, onToggle, groups, onRemoveGroup, onClearAll }: Props) {
  return (
    <>
      {/* Toggle Button — bottom-left */}
      <button
        onClick={onToggle}
        style={{
          position: 'fixed',
          bottom: 48,
          left: 20,
          zIndex: 1000,
          width: 48,
          height: 48,
          borderRadius: '50%',
          border: '2px solid #fbbf24',
          background: open ? '#fbbf24' : 'rgba(10,15,26,0.95)',
          color: open ? '#0a0f1a' : '#fbbf24',
          fontSize: 18,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(251,191,36,0.2)',
          transition: 'all 200ms',
        }}
        title={open ? 'Close artifacts' : 'View artifacts & reports'}
      >
        {open ? '\u2715' : '\u2193'}
        {/* Count badge */}
        {!open && groups.length > 0 && (
          <span style={{
            position: 'absolute',
            top: -4,
            right: -4,
            width: 20,
            height: 20,
            borderRadius: '50%',
            background: '#fbbf24',
            color: '#0a0f1a',
            font: '700 11px/20px var(--font-mono)',
            textAlign: 'center',
          }}>
            {groups.length}
          </span>
        )}
      </button>

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: -340, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -340, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: 'fixed',
              top: 56,
              left: 0,
              bottom: 36,
              width: 340,
              zIndex: 999,
              display: 'flex',
              flexDirection: 'column',
              background: 'rgba(10,15,26,0.97)',
              borderRight: '1px solid rgba(251,191,36,0.2)',
              backdropFilter: 'blur(20px)',
            }}
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              flexShrink: 0,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: '50%',
                background: '#fbbf24',
                boxShadow: '0 0 8px #fbbf24',
              }} />
              <div style={{ flex: 1 }}>
                <div style={{
                  font: '600 14px/1 var(--font-display)',
                  color: '#f1f5f9',
                  letterSpacing: '0.04em',
                }}>
                  Artifacts
                </div>
                <div style={{
                  font: '400 11px/1.2 var(--font-body)',
                  color: '#64748b',
                  marginTop: 2,
                }}>
                  {groups.length} report{groups.length !== 1 ? 's' : ''} available
                </div>
              </div>
              {groups.length > 0 && (
                <button
                  onClick={onClearAll}
                  style={{
                    font: '500 10px/1 var(--font-body)',
                    color: '#64748b',
                    background: 'none',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: 4,
                    padding: '4px 8px',
                    cursor: 'pointer',
                  }}
                >
                  Clear all
                </button>
              )}
            </div>

            {/* Body */}
            <div style={{
              flex: 1,
              overflow: 'auto',
              padding: '12px 16px',
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}>
              {groups.length === 0 && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  textAlign: 'center',
                  padding: 32,
                }}>
                  <div>
                    <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.3 }}>{'\u2193'}</div>
                    <div style={{
                      font: '500 13px/1.5 var(--font-body)',
                      color: '#64748b',
                    }}>
                      Chat with NEXUS agents to generate downloadable reports.
                      Artifacts appear here as agents run tools.
                    </div>
                  </div>
                </div>
              )}

              {groups.map(group => (
                <ArtifactGroupCard
                  key={group.id}
                  group={group}
                  onRemove={() => onRemoveGroup(group.id)}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// ── Artifact Group Card ──────────────────────────────────────────────

function ArtifactGroupCard({ group, onRemove }: { group: ArtifactGroup; onRemove: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const [exporting, setExporting] = useState<'excel' | 'word' | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const modeColor = MODE_COLORS[group.mode] || '#fbbf24';
  const timeAgo = getTimeAgo(group.completedAt || group.createdAt);

  const handleExportExcel = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setExporting('excel');
    setExportError(null);
    try {
      const { generateExcelReport } = await import('../lib/reportGenerators/excelGenerator');
      const blob = await generateExcelReport(group);
      saveAs(blob, `NEXUS-${group.mode}-report-${Date.now()}.xlsx`);
    } catch (err) {
      console.error('Excel export failed:', err);
      setExportError(`Excel export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setExporting(null);
    }
  };

  const handleExportWord = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setExporting('word');
    setExportError(null);
    try {
      const { generateWordReport } = await import('../lib/reportGenerators/wordGenerator');
      const blob = await generateWordReport(group);
      saveAs(blob, `NEXUS-${group.mode}-report-${Date.now()}.docx`);
    } catch (err) {
      console.error('Word export failed:', err);
      setExportError(`Word export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="nexus-panel" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Card Header — clickable to expand */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '12px 14px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 10,
        }}
      >
        {/* Mode badge */}
        <span style={{
          font: '700 9px/1 var(--font-mono)',
          padding: '3px 6px',
          borderRadius: 3,
          background: `${modeColor}18`,
          color: modeColor,
          border: `1px solid ${modeColor}33`,
          flexShrink: 0,
          marginTop: 2,
        }}>
          {MODE_LABELS[group.mode] || group.mode.toUpperCase()}
        </span>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            font: '500 12px/1.4 var(--font-body)',
            color: '#e2e8f0',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {group.userQuery}
          </div>
          <div style={{
            font: '400 10px/1.2 var(--font-body)',
            color: '#64748b',
            marginTop: 3,
            display: 'flex',
            gap: 8,
          }}>
            <span>{timeAgo}</span>
            <span>{group.items.length} artifact{group.items.length !== 1 ? 's' : ''}</span>
          </div>
        </div>

        <span style={{
          color: '#64748b',
          fontSize: 10,
          transition: 'transform 150ms',
          transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
          flexShrink: 0,
          marginTop: 4,
        }}>
          {'\u25B6'}
        </span>
      </div>

      {/* Expanded: item list + export buttons */}
      {expanded && (
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
          {/* Item list */}
          <div style={{ padding: '8px 14px', display: 'flex', flexDirection: 'column', gap: 4 }}>
            {group.items.map(item => (
              <div key={item.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '4px 0',
              }}>
                <span style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: modeColor,
                  flexShrink: 0,
                  opacity: 0.6,
                }} />
                <span style={{
                  font: '400 11px/1.3 var(--font-body)',
                  color: '#94a3b8',
                  flex: 1,
                }}>
                  {item.label}
                </span>
                <span style={{
                  font: '400 9px/1 var(--font-mono)',
                  color: '#475569',
                }}>
                  {item.toolName}
                </span>
              </div>
            ))}
          </div>

          {/* Export error message */}
          {exportError && (
            <div style={{
              padding: '6px 14px',
              borderTop: '1px solid rgba(239,68,68,0.2)',
              font: '400 11px/1.4 var(--font-body)',
              color: '#ef4444',
              background: 'rgba(239,68,68,0.06)',
            }}>
              {exportError}
            </div>
          )}

          {/* Export buttons */}
          <div style={{
            padding: '10px 14px',
            borderTop: '1px solid rgba(255,255,255,0.04)',
            display: 'flex',
            gap: 8,
          }}>
            <button
              onClick={handleExportExcel}
              disabled={exporting !== null}
              style={{
                flex: 1,
                font: '600 11px/1 var(--font-display)',
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid rgba(16,185,129,0.3)',
                background: 'rgba(16,185,129,0.08)',
                color: '#10b981',
                cursor: exporting ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
              }}
            >
              {exporting === 'excel' ? (
                <span style={{
                  display: 'inline-block', width: 12, height: 12,
                  border: '2px solid rgba(16,185,129,0.3)',
                  borderTop: '2px solid #10b981',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }} />
              ) : (
                '\u{1F4CA}'
              )}
              Excel
            </button>

            <button
              onClick={handleExportWord}
              disabled={exporting !== null}
              style={{
                flex: 1,
                font: '600 11px/1 var(--font-display)',
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid rgba(30,136,229,0.3)',
                background: 'rgba(30,136,229,0.08)',
                color: '#1e88e5',
                cursor: exporting ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
              }}
            >
              {exporting === 'word' ? (
                <span style={{
                  display: 'inline-block', width: 12, height: 12,
                  border: '2px solid rgba(30,136,229,0.3)',
                  borderTop: '2px solid #1e88e5',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }} />
              ) : (
                '\u{1F4DD}'
              )}
              Word
            </button>

            <button
              onClick={onRemove}
              style={{
                font: '400 11px/1 var(--font-body)',
                padding: '8px',
                borderRadius: 6,
                border: '1px solid rgba(255,255,255,0.06)',
                background: 'transparent',
                color: '#64748b',
                cursor: 'pointer',
              }}
              title="Remove artifact"
            >
              {'\u2715'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function getTimeAgo(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60_000) return 'just now';
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return new Date(ts).toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
}

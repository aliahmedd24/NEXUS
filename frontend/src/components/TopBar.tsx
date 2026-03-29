import { type Mode } from '../types/api';

const modes: { key: Mode; label: string; color: string }[] = [
  { key: 'diagnose', label: 'DIAGNOSE', color: '#ef4444' },
  { key: 'staff', label: 'STAFF', color: '#1e88e5' },
  { key: 'learn', label: 'LEARN', color: '#a78bfa' },
];

interface Props {
  activeMode: Mode;
  onModeChange: (mode: Mode) => void;
  scenarioName?: string;
  onInjectClick?: () => void;
}

export function TopBar({ activeMode, onModeChange, scenarioName, onInjectClick }: Props) {
  return (
    <header style={{
      height: 56,
      background: 'rgba(17, 24, 39, 0.85)',
      backdropFilter: 'blur(16px) saturate(1.2)',
      borderBottom: '1px solid rgba(255,255,255,0.06)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      flexShrink: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 20, height: 20,
          background: '#1e88e5',
          transform: 'rotate(45deg)',
          borderRadius: 3,
        }} />
        <span style={{
          font: '800 20px/1 var(--font-display)',
          color: '#1e88e5',
          letterSpacing: '0.06em',
        }}>NEXUS</span>
      </div>

      <nav style={{ display: 'flex', gap: 6 }}>
        {modes.map(m => {
          const isActive = activeMode === m.key;
          return (
            <button
              key={m.key}
              onClick={() => onModeChange(m.key)}
              style={{
                font: '600 13px/1 var(--font-display)',
                letterSpacing: '0.06em',
                padding: '8px 20px',
                borderRadius: 20,
                border: 'none',
                cursor: 'pointer',
                transition: 'all 150ms ease',
                background: isActive ? m.color : 'transparent',
                color: isActive ? '#fff' : '#94a3b8',
                boxShadow: isActive ? `0 0 16px ${m.color}44` : 'none',
              }}
            >
              {m.label}
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {scenarioName && (
          <span style={{ font: '400 13px/1.5 var(--font-body)', color: '#94a3b8' }}>
            Scenario: <strong style={{ color: '#f1f5f9' }}>{scenarioName}</strong>
          </span>
        )}
        {onInjectClick && (
          <button
            onClick={onInjectClick}
            style={{
              font: '600 12px/1 var(--font-display)',
              padding: '7px 14px',
              borderRadius: 6,
              border: '1px solid #fbbf24',
              background: 'rgba(251, 191, 36, 0.12)',
              color: '#fbbf24',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            &#9889; Inject Compound
          </button>
        )}
      </div>
    </header>
  );
}

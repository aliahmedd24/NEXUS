import { type Mode } from '../types/api';
import { useEffect, useRef, useState } from 'react';

const modeColors: Record<Mode, string> = {
  diagnose: '#ef4444',
  staff: '#1e88e5',
  learn: '#a78bfa',
};

interface Props {
  mode: Mode;
  resilience: number;
  criticalCount: number;
  warningCount: number;
  coveredCount: number;
  scenarioName: string;
  calibrated: boolean;
}

export function StatusBar({ mode, resilience, criticalCount, warningCount, coveredCount, scenarioName, calibrated }: Props) {
  const [displayResilience, setDisplayResilience] = useState(resilience);
  const prevResilience = useRef(resilience);

  useEffect(() => {
    const start = prevResilience.current;
    const diff = resilience - start;
    prevResilience.current = resilience;
    if (Math.abs(diff) < 0.001) return;
    const duration = 600;
    const startTime = Date.now();
    let rafId: number;
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayResilience(start + diff * eased);
      if (progress < 1) rafId = requestAnimationFrame(animate);
    };
    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [resilience]);

  return (
    <footer style={{
      height: 36,
      background: 'rgba(17, 24, 39, 0.92)',
      borderTop: '1px solid rgba(255,255,255,0.06)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 24px',
      gap: 24,
      flexShrink: 0,
      font: '500 11px/1 var(--font-body)',
      letterSpacing: '0.04em',
      color: '#94a3b8',
    }}>
      <span style={{ color: '#1e88e5', fontWeight: 600 }}>&#9670; NEXUS v0.1</span>
      <Divider />
      <span>Resilience: <span className="text-mono" style={{
        color: displayResilience >= 0.7 ? '#10b981' : displayResilience >= 0.5 ? '#f59e0b' : '#ef4444',
        fontWeight: 600,
      }}>{displayResilience.toFixed(2)}</span></span>
      <Divider />
      <span style={{ color: '#ef4444' }}>&#11044;{criticalCount} Critical</span>
      <span style={{ color: '#f59e0b' }}>&#11044;{warningCount} Warning</span>
      <span style={{ color: '#10b981' }}>&#11044;{coveredCount} Covered</span>
      <Divider />
      <span>Mode: <span style={{ color: modeColors[mode], fontWeight: 600 }}>{mode.toUpperCase()}</span></span>
      <Divider />
      <span>Scenario: <span style={{ color: '#f1f5f9' }}>{scenarioName || 'None'}</span></span>
      {calibrated && (
        <>
          <Divider />
          <span style={{ color: '#10b981' }}>Calibrated: &#10003;</span>
        </>
      )}
    </footer>
  );
}

function Divider() {
  return <span style={{ color: 'rgba(255,255,255,0.1)' }}>|</span>;
}

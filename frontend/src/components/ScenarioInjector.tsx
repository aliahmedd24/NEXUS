import { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';

interface Props {
  scenarios: { id: string; name: string }[];
  onInjected: (compoundScenario: any) => void;
  onClose: () => void;
}

const agentSteps = [
  'Scenario Architect: compound scenario generated',
  'Vulnerability Scanner: re-scanning leadership roles...',
  'Cascade Modeler: tracing impact chains...',
  'Portfolio Optimizer: recalculating frontiers...',
];

export function ScenarioInjector({ scenarios, onInjected, onClose }: Props) {
  const [step, setStep] = useState<'select' | 'loading' | 'done'>('select');
  const [scenarioA, setScenarioA] = useState(scenarios[0]?.name || '');
  const [scenarioB, setScenarioB] = useState(scenarios[1]?.name || '');
  const [loadingStep, setLoadingStep] = useState(0);

  const inject = async () => {
    setStep('loading');
    setLoadingStep(0);

    const stepInterval = setInterval(() => {
      setLoadingStep(s => Math.min(s + 1, agentSteps.length - 1));
    }, 2000);

    try {
      const compound = await api.createCompound(scenarioA, scenarioB);
      clearInterval(stepInterval);
      onInjected(compound);
    } catch (e) {
      clearInterval(stepInterval);
      setStep('select');
    }
  };

  if (step === 'loading') {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        style={{
          position: 'fixed', inset: 0, zIndex: 1000,
          background: 'rgba(10, 15, 26, 0.92)',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center', gap: 32,
        }}
      >
        {/* Hexagonal loading animation */}
        <div style={{ position: 'relative', width: 120, height: 120 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <motion.div
              key={i}
              animate={{
                opacity: [0.2, 1, 0.2],
                scale: [0.8, 1.1, 0.8],
              }}
              transition={{
                duration: 1.5,
                delay: i * 0.2,
                repeat: Infinity,
              }}
              style={{
                position: 'absolute',
                width: 16, height: 16,
                background: '#1e88e5',
                borderRadius: 3,
                transform: `rotate(45deg)`,
                left: 52 + Math.cos((i * Math.PI) / 3) * 40,
                top: 52 + Math.sin((i * Math.PI) / 3) * 40,
              }}
            />
          ))}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
            style={{
              position: 'absolute',
              width: 20, height: 20,
              background: '#fbbf24',
              borderRadius: 4,
              transform: 'rotate(45deg)',
              left: 50, top: 50,
            }}
          />
        </div>

        <div style={{ textAlign: 'center' }}>
          <div className="text-heading" style={{ color: '#f1f5f9', marginBottom: 16 }}>
            Re-analyzing organizational resilience...
          </div>
          <motion.div
            key={loadingStep}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-mono"
            style={{ color: '#22d3ee' }}
          >
            {agentSteps[loadingStep]}
          </motion.div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(10, 15, 26, 0.85)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        onClick={e => e.stopPropagation()}
        className="nexus-panel"
        style={{ padding: 32, width: 480, maxWidth: '90vw' }}
      >
        <div className="text-display-md" style={{ color: '#f1f5f9', marginBottom: 8 }}>
          Compound Scenario Injection
        </div>
        <p className="text-body-sm" style={{ color: '#94a3b8', marginBottom: 24 }}>
          Combine two simultaneous crises to stress-test organizational resilience under extreme conditions.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
          <label style={{ font: '500 11px/1 var(--font-body)', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b' }}>
            Scenario A
          </label>
          <select
            value={scenarioA}
            onChange={e => setScenarioA(e.target.value)}
            style={selectStyle}
          >
            {scenarios.map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
          </select>

          <label style={{ font: '500 11px/1 var(--font-body)', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748b', marginTop: 8 }}>
            Scenario B
          </label>
          <select
            value={scenarioB}
            onChange={e => setScenarioB(e.target.value)}
            style={selectStyle}
          >
            {scenarios.map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button onClick={onClose} style={cancelBtnStyle}>Cancel</button>
          <button onClick={inject} style={injectBtnStyle}>&#9889; Inject</button>
        </div>
      </motion.div>
    </motion.div>
  );
}

const selectStyle: React.CSSProperties = {
  font: '400 14px/1.5 var(--font-body)',
  padding: '10px 12px',
  borderRadius: 6,
  border: '1px solid rgba(255,255,255,0.1)',
  background: '#1a2236',
  color: '#f1f5f9',
  outline: 'none',
  width: '100%',
};

const cancelBtnStyle: React.CSSProperties = {
  font: '500 13px/1 var(--font-body)',
  padding: '10px 20px',
  borderRadius: 6,
  border: '1px solid rgba(255,255,255,0.1)',
  background: 'transparent',
  color: '#94a3b8',
  cursor: 'pointer',
};

const injectBtnStyle: React.CSSProperties = {
  font: '600 13px/1 var(--font-display)',
  padding: '10px 20px',
  borderRadius: 6,
  border: '1px solid #fbbf24',
  background: 'rgba(251, 191, 36, 0.15)',
  color: '#fbbf24',
  cursor: 'pointer',
};

import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import {
  type Mode, type DiagnoseResult, type CascadeReport,
  type CandidateFit, type LeaderGenome, type TeamChemistry, type StaffingPlan,
  type HistoricalDecision, type BiasPattern, type DecisionReplay,
} from './types/api';
import { api } from './lib/api';
import { useArtifacts } from './hooks/useArtifacts';
import { TopBar } from './components/TopBar';
import { StatusBar } from './components/StatusBar';
import { ChatPanel } from './components/ChatPanel';
import { ArtifactsPanel } from './components/ArtifactsPanel';
import { ScenarioInjector } from './components/ScenarioInjector';
import { DiagnosePage } from './pages/DiagnosePage';
import { StaffPage } from './pages/StaffPage';
import { LearnPage } from './pages/LearnPage';

function App() {
  const [mode, setMode] = useState<Mode>('diagnose');
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [showInjector, setShowInjector] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [compoundScenario, setCompoundScenario] = useState<any>(null);

  // Artifact collection
  const { groups: artifactGroups, startGroup, addItem, finalizeGroup, removeGroup, clearAll: clearArtifacts } = useArtifacts();

  // Status bar state
  const [resilience, setResilience] = useState(1.0);
  const [criticalCount, setCriticalCount] = useState(0);
  const [warningCount, setWarningCount] = useState(0);
  const [coveredCount, setCoveredCount] = useState(0);
  const [scenarioName, setScenarioName] = useState('');
  const [calibrated, setCalibrated] = useState(false);

  // Injected visualization data from chat agent (mechanical tool data)
  const [vizDiagnoseResult, setVizDiagnoseResult] = useState<DiagnoseResult | null>(null);
  const [vizCascade, setVizCascade] = useState<CascadeReport | null>(null);
  const [vizRanking, setVizRanking] = useState<CandidateFit[] | null>(null);
  const [vizGenome, setVizGenome] = useState<LeaderGenome | null>(null);
  const [vizChemistry, setVizChemistry] = useState<TeamChemistry | null>(null);
  const [vizPlan, setVizPlan] = useState<StaffingPlan | null>(null);
  const [vizDecisions, setVizDecisions] = useState<HistoricalDecision[] | null>(null);
  const [vizBiases, setVizBiases] = useState<BiasPattern | null>(null);
  const [vizReplay, setVizReplay] = useState<DecisionReplay | null>(null);

  // LLM-reasoned analysis overlays (dynamic — may differ from mechanical)
  const [llmDiagnose, setLlmDiagnose] = useState<Record<string, unknown> | null>(null);
  const [llmCascade, setLlmCascade] = useState<Record<string, unknown> | null>(null);
  const [llmRanking, setLlmRanking] = useState<Record<string, unknown> | null>(null);
  const [llmChemistry, setLlmChemistry] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [scenarioData] = await Promise.all([
        api.getScenarios(),
      ]);
      setScenarios(scenarioData || []);

      // Load roles via candidates endpoint
      try {
        await api.getCandidates();
      } catch {}

      // Check calibration state
      try {
        const cal = await api.getCalibration();
        setCalibrated(Object.keys(cal).length > 0);
      } catch {}
    } catch (e) {
      console.error('Initial data load failed:', e);
    }
  };

  const handleDiagnoseResult = useCallback((result: DiagnoseResult) => {
    setResilience(result.aggregate_resilience_score);
    setCriticalCount(result.critical_count);
    setWarningCount(result.warning_count);
    setCoveredCount(result.covered_count);
    setScenarioName(result.scenario_name);
  }, []);

  const handleStreamStart = useCallback((query: string) => {
    startGroup(mode, query);
  }, [mode, startGroup]);

  const handleCompoundInjected = (compound: any) => {
    setShowInjector(false);
    setCompoundScenario(compound);
    setScenarioName(compound.name);
    setMode('diagnose');
  };

  const handleVisualization = useCallback((type: string, data: unknown, toolName?: string) => {
    console.log('[NEXUS App] visualization received:', type);
    addItem(type, toolName || type, data);
    const d = data as Record<string, unknown>;

    switch (type) {
      // DIAGNOSE
      case 'diagnose_heatmap':
        setVizDiagnoseResult(d as unknown as DiagnoseResult);
        setMode('diagnose');
        break;
      case 'diagnose_cascade':
        setVizCascade(d as unknown as CascadeReport);
        setMode('diagnose');
        break;
      case 'diagnose_spof':
        // SPOF results map to heatmap with filtered critical cells
        break;

      // STAFF
      case 'staff_ranking': {
        // rank_candidates returns {org_unit_id, role_type, candidates: [...]}
        const candidates = (d as { candidates?: CandidateFit[] }).candidates
          || (d as { ranking?: CandidateFit[] }).ranking
          || (Array.isArray(d) ? d as unknown as CandidateFit[] : []);
        if (candidates.length > 0) {
          setVizRanking(candidates);
          // Auto-load genome for the top candidate
          setVizGenome(null);
        }
        setMode('staff');
        break;
      }
      case 'staff_genome':
        setVizGenome(d as unknown as LeaderGenome);
        setMode('staff');
        break;
      case 'staff_chemistry':
        setVizChemistry(d as unknown as TeamChemistry);
        setMode('staff');
        break;
      case 'staff_plan':
        setVizPlan(d as unknown as StaffingPlan);
        setMode('staff');
        break;
      case 'staff_fit':
        // Individual fit — could update ranking if present
        break;

      // LEARN
      case 'learn_decisions':
        setVizDecisions(d as unknown as HistoricalDecision[]);
        setMode('learn');
        break;
      case 'learn_biases':
        setVizBiases(d as unknown as BiasPattern);
        setMode('learn');
        break;
      case 'learn_replay':
        setVizReplay(d as unknown as DecisionReplay);
        setMode('learn');
        break;
      case 'learn_outcomes':
      case 'learn_counterfactual':
      case 'learn_calibration':
      case 'learn_calibration_updated':
        // These are informational — agent text explains them
        break;

      // LLM-reasoned analysis overlays
      case 'diagnose_heatmap_llm':
        setLlmDiagnose(d);
        break;
      case 'diagnose_cascade_llm':
        setLlmCascade(d);
        break;
      case 'staff_ranking_llm':
        setLlmRanking(d);
        break;
      case 'staff_chemistry_llm':
        setLlmChemistry(d);
        break;
    }
  }, [addItem]);

  // JD template role_types — must match jd_templates.role_type in DB exactly
  const knownRoles = [
    { id: 'head-ev-battery', title: 'Head of EV Battery Systems' },
    { id: 'plant-director', title: 'Plant Director' },
    { id: 'cto', title: 'Chief Technology Officer' },
    { id: 'svp-mfg', title: 'SVP Manufacturing' },
    { id: 'vp-supply', title: 'VP Supply Chain' },
    { id: 'vp-quality', title: 'VP Quality' },
    { id: 'vp-it', title: 'VP IT & Digital' },
    { id: 'head-rd', title: 'Head of R&D' },
  ];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      width: '100vw',
      overflow: 'hidden',
      background: '#0a0f1a',
    }}>
      <TopBar
        activeMode={mode}
        onModeChange={setMode}
        scenarioName={scenarioName}
        onInjectClick={() => setShowInjector(true)}
      />

      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
        {mode === 'diagnose' && (
          <DiagnosePage
            scenarios={scenarios}
            onResultReady={handleDiagnoseResult}
            compoundScenario={compoundScenario}
            injectedResult={vizDiagnoseResult}
            injectedCascade={vizCascade}
            llmAnalysis={llmDiagnose}
            llmCascade={llmCascade}
          />
        )}
        {mode === 'staff' && (
          <StaffPage
            scenarios={scenarios}
            roles={knownRoles}
            injectedRanking={vizRanking}
            injectedGenome={vizGenome}
            injectedChemistry={vizChemistry}
            injectedPlan={vizPlan}
            llmRanking={llmRanking}
            llmChemistry={llmChemistry}
          />
        )}
        {mode === 'learn' && (
          <LearnPage
            injectedDecisions={vizDecisions}
            injectedBiases={vizBiases}
            injectedReplay={vizReplay}
          />
        )}
      </div>

      <StatusBar
        mode={mode}
        resilience={resilience}
        criticalCount={criticalCount}
        warningCount={warningCount}
        coveredCount={coveredCount}
        scenarioName={scenarioName}
        calibrated={calibrated}
      />

      {/* Artifacts Panel — left side */}
      <ArtifactsPanel
        open={showArtifacts}
        onToggle={() => setShowArtifacts(prev => !prev)}
        groups={artifactGroups}
        onRemoveGroup={removeGroup}
        onClearAll={clearArtifacts}
      />

      {/* Chat Panel — right side */}
      <ChatPanel
        mode={mode}
        open={showChat}
        onToggle={() => setShowChat(prev => !prev)}
        onVisualization={handleVisualization}
        onStreamStart={handleStreamStart}
        onStreamDone={finalizeGroup}
      />

      {/* Scenario Injector Modal */}
      <AnimatePresence>
        {showInjector && scenarios.length > 0 && (
          <ScenarioInjector
            scenarios={scenarios}
            onInjected={handleCompoundInjected}
            onClose={() => setShowInjector(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

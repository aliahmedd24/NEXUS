/**
 * Word report generator — produces .docx blobs from artifact groups.
 * Lazy-loaded via dynamic import() to keep initial bundle small.
 */
import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, WidthType, BorderStyle, ShadingType,
} from 'docx';
import { type ArtifactGroup, type ArtifactItem } from '../../types/artifacts';
import {
  formatScore, formatScoreRaw, scoreToStatus, formatEUR, formatDate,
  formatDimension, WORD_COLORS,
} from './common';

// ── Helpers ──────────────────────────────────────────────────────────

function findItem(items: ArtifactItem[], vizType: string): unknown | null {
  return items.find(i => i.vizType === vizType)?.data ?? null;
}

function heading(text: string, level: (typeof HeadingLevel)[keyof typeof HeadingLevel] = HeadingLevel.HEADING_2): Paragraph {
  return new Paragraph({ heading: level, spacing: { before: 300, after: 120 }, children: [
    new TextRun({ text, color: WORD_COLORS.brandBlue, bold: true }),
  ]});
}

function bodyText(text: string, opts?: { bold?: boolean; color?: string }): Paragraph {
  return new Paragraph({ spacing: { after: 80 }, children: [
    new TextRun({ text, bold: opts?.bold, color: opts?.color || WORD_COLORS.textDark, size: 22 }),
  ]});
}

function metaLine(label: string, value: string): Paragraph {
  return new Paragraph({ spacing: { after: 40 }, children: [
    new TextRun({ text: `${label}: `, bold: true, color: WORD_COLORS.textMuted, size: 20 }),
    new TextRun({ text: value, color: WORD_COLORS.textDark, size: 20 }),
  ]});
}

const thinBorder = { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' };
const cellBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

function headerCell(text: string): TableCell {
  return new TableCell({
    borders: cellBorders,
    shading: { type: ShadingType.SOLID, color: WORD_COLORS.brandBlue },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text, bold: true, color: 'FFFFFF', size: 20 }),
    ]})],
  });
}

function dataCell(text: string, opts?: { color?: string; bold?: boolean }): TableCell {
  return new TableCell({
    borders: cellBorders,
    children: [new Paragraph({ children: [
      new TextRun({ text, color: opts?.color || WORD_COLORS.textDark, bold: opts?.bold, size: 20 }),
    ]})],
  });
}

// ── Main entry ───────────────────────────────────────────────────────

export async function generateWordReport(group: ArtifactGroup): Promise<Blob> {
  const sections: Paragraph[] = [];
  const tables: (Paragraph | Table)[] = [];

  // Title
  sections.push(new Paragraph({
    heading: HeadingLevel.TITLE,
    spacing: { after: 100 },
    children: [new TextRun({ text: `NEXUS ${group.mode.toUpperCase()} Analysis Report`, color: WORD_COLORS.brandBlue, bold: true, size: 48 })],
  }));

  // Meta
  sections.push(metaLine('Pipeline', group.mode.toUpperCase()));
  sections.push(metaLine('Agent', group.agentName || 'NEXUS'));
  sections.push(metaLine('Query', group.userQuery));
  sections.push(metaLine('Generated', formatDate(group.completedAt || group.createdAt)));
  sections.push(new Paragraph({ spacing: { after: 200 }, children: [] }));

  // Executive Summary
  sections.push(heading('Executive Summary', HeadingLevel.HEADING_1));
  sections.push(bodyText(generateExecutiveSummary(group)));
  sections.push(new Paragraph({ spacing: { after: 200 }, children: [] }));

  // Pipeline-specific sections
  switch (group.mode) {
    case 'diagnose':
      tables.push(...buildDiagnoseSections(group.items));
      break;
    case 'staff':
      tables.push(...buildStaffSections(group.items));
      break;
    case 'learn':
      tables.push(...buildLearnSections(group.items));
      break;
  }

  // Recommendations
  sections.push(heading('Recommendations', HeadingLevel.HEADING_1));
  for (const rec of generateRecommendations(group)) {
    sections.push(bodyText(`\u2022 ${rec}`));
  }

  const doc = new Document({
    sections: [{
      children: [...sections, ...tables],
    }],
  });

  return await Packer.toBlob(doc);
}

// ── Executive Summary Generator ──────────────────────────────────────

function generateExecutiveSummary(group: ArtifactGroup): string {
  const items = group.items;

  if (group.mode === 'diagnose') {
    const heatmap = findItem(items, 'diagnose_heatmap') as Record<string, unknown> | null;
    if (heatmap) {
      const resilience = Number(heatmap.aggregate_resilience_score ?? 0);
      const critical = Number(heatmap.critical_count ?? 0);
      const scenario = (heatmap.scenario_name as string) || 'the selected scenario';
      return `Analysis of ${scenario} reveals an aggregate organizational resilience score of ${formatScore(resilience)}. ${critical} critical vulnerability${critical !== 1 ? 'ies were' : 'y was'} identified, requiring immediate attention to prevent cascading operational failures. The following report details the vulnerability heatmap across all leadership positions and traces the potential cascade impact through the organizational dependency graph.`;
    }
  }

  if (group.mode === 'staff') {
    const ranking = findItem(items, 'staff_ranking') as Record<string, unknown> | null;
    if (ranking) {
      const candidates = ((ranking as { candidates?: unknown[] }).candidates || []) as Record<string, unknown>[];
      const topCandidate = candidates[0];
      const roleType = (ranking as { role_type?: string }).role_type || 'the target role';
      if (topCandidate) {
        return `Talent analysis for ${roleType} evaluated ${candidates.length} candidates. The top-ranked candidate is ${topCandidate.full_name} with an overall fit score of ${formatScoreRaw(Number(topCandidate.overall_fit_score ?? 0))}. ${topCandidate.calibration_applied ? 'Bias calibration was applied to correct for historical overweighting patterns.' : ''} The following report provides the full ranking, genome profiles, team chemistry analysis, and staffing plan with ROI projections.`;
      }
    }
  }

  if (group.mode === 'learn') {
    const biases = findItem(items, 'learn_biases') as Record<string, number> | null;
    if (biases) {
      const entries = Object.entries(biases).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
      const topBias = entries[0];
      if (topBias) {
        const dir = topBias[1] >= 0 ? 'overweighted' : 'underweighted';
        return `Historical decision analysis reveals systematic biases in leadership hiring. The most significant pattern is ${formatDimension(topBias[0])}, which has been ${dir} by ${Math.abs(topBias[1] * 100).toFixed(1)}%. The following report provides the full bias mirror, decision replay with counterfactual analysis, and updated calibration coefficients to correct future hiring decisions.`;
      }
    }
  }

  return `This report summarizes the findings from the NEXUS ${group.mode.toUpperCase()} pipeline analysis containing ${group.items.length} data artifacts. Detailed findings follow below.`;
}

// ── Recommendations Generator ────────────────────────────────────────

function generateRecommendations(group: ArtifactGroup): string[] {
  const recs: string[] = [];
  const items = group.items;

  if (group.mode === 'diagnose') {
    const heatmap = findItem(items, 'diagnose_heatmap') as Record<string, unknown> | null;
    if (heatmap) {
      const critical = Number(heatmap.critical_count ?? 0);
      if (critical > 0) recs.push(`Address ${critical} critical leadership gap${critical !== 1 ? 's' : ''} within the next 90 days to prevent operational cascades.`);
      const resilience = Number(heatmap.aggregate_resilience_score ?? 0);
      if (resilience < 0.6) recs.push(`Aggregate resilience (${formatScore(resilience)}) is below the 60% threshold. Consider accelerating succession planning.`);
    }
    const cascade = findItem(items, 'diagnose_cascade') as Record<string, unknown> | null;
    if (cascade) {
      const totalCost = Number((cascade as { total_impact_eur?: number }).total_impact_eur ?? 0);
      if (totalCost > 0) recs.push(`Total cascade exposure of ${formatEUR(totalCost)} identified. Prioritize the optimal intervention point to block downstream propagation.`);
    }
  }

  if (group.mode === 'staff') {
    const ranking = findItem(items, 'staff_ranking') as Record<string, unknown> | null;
    if (ranking) {
      const candidates = ((ranking as { candidates?: unknown[] }).candidates || []) as Record<string, unknown>[];
      if (candidates.length > 0) {
        const top = candidates[0];
        recs.push(`Proceed with ${top.full_name} (fit: ${formatScoreRaw(Number(top.overall_fit_score ?? 0))}) as the primary candidate. Prepare a structured onboarding plan focused on identified gap dimensions.`);
      }
      if (candidates.length > 1) {
        recs.push(`Maintain ${candidates[1].full_name} as an active backup candidate in case the primary declines.`);
      }
    }
    const chemistry = findItem(items, 'staff_chemistry') as Record<string, unknown> | null;
    if (chemistry) {
      const avgSynergy = Number((chemistry as { average_synergy?: number }).average_synergy ?? 0);
      if (avgSynergy < 0) recs.push(`Team chemistry analysis flags negative average synergy (${formatScoreRaw(avgSynergy)}). Plan targeted team integration activities for the first 90 days.`);
    }
  }

  if (group.mode === 'learn') {
    const biases = findItem(items, 'learn_biases') as Record<string, number> | null;
    if (biases) {
      const overweighted = Object.entries(biases).filter(([, v]) => v > 0.1).sort((a, b) => b[1] - a[1]);
      const underweighted = Object.entries(biases).filter(([, v]) => v < -0.1).sort((a, b) => a[1] - b[1]);
      if (overweighted.length > 0) recs.push(`Reduce emphasis on ${overweighted.map(([d]) => formatDimension(d)).join(', ')} in interview scoring rubrics — historical data shows systematic overweighting.`);
      if (underweighted.length > 0) recs.push(`Increase weight on ${underweighted.map(([d]) => formatDimension(d)).join(', ')} — these dimensions predict success but are currently undervalued.`);
    }
    recs.push('Apply the updated calibration coefficients to the STAFF pipeline to improve future hiring accuracy.');
  }

  if (recs.length === 0) recs.push('Review the detailed findings above and consult with the leadership team before taking action.');
  return recs;
}

// ── DIAGNOSE Sections ────────────────────────────────────────────────

function buildDiagnoseSections(items: ArtifactItem[]): (Paragraph | Table)[] {
  const result: (Paragraph | Table)[] = [];
  const heatmapData = findItem(items, 'diagnose_heatmap') as Record<string, unknown> | null;

  if (heatmapData) {
    result.push(heading('Vulnerability Heatmap'));
    const heatmap = ((heatmapData as { heatmap?: unknown[] }).heatmap || []) as Record<string, unknown>[];

    if (heatmap.length > 0) {
      const rows = [
        new TableRow({ children: [
          headerCell('Role'), headerCell('Leader'), headerCell('Gap Score'), headerCell('Status'),
        ]}),
        ...heatmap.map(cell => {
          const status = scoreToStatus(Number(cell.gap_score ?? 0));
          const statusColor = status === 'CRITICAL' ? WORD_COLORS.critical : status === 'WARNING' ? WORD_COLORS.warning : WORD_COLORS.success;
          return new TableRow({ children: [
            dataCell(String(cell.role_title || '')),
            dataCell(String(cell.leader_name || 'VACANT')),
            dataCell(formatScoreRaw(Number(cell.gap_score ?? 0))),
            dataCell(status, { color: statusColor, bold: true }),
          ]});
        }),
      ];

      result.push(new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows,
      }));
    }
  }

  const cascadeData = findItem(items, 'diagnose_cascade') as Record<string, unknown> | null;
  if (cascadeData) {
    result.push(heading('Cascade Impact Analysis'));
    const trigger = (cascadeData as { role_title?: string }).role_title || '';
    const totalImpact = Number((cascadeData as { total_impact_eur?: number }).total_impact_eur ?? 0);
    result.push(bodyText(`Trigger: ${trigger}  |  Total Exposure: ${formatEUR(totalImpact)}`, { bold: true }));

    const chain = ((cascadeData as { cascade_chain?: unknown[] }).cascade_chain || []) as Record<string, unknown>[];
    if (chain.length > 0) {
      result.push(new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            headerCell('Org Unit'), headerCell('Impact'), headerCell('Cost'), headerCell('Delay'),
          ]}),
          ...chain.map(node => new TableRow({ children: [
            dataCell(String(node.org_unit_name || '')),
            dataCell(formatScoreRaw(Number(node.impact_score ?? 0))),
            dataCell(formatEUR(Number(node.estimated_cost_eur ?? 0))),
            dataCell(`${node.estimated_delay_days ?? 0} days`),
          ]})),
        ],
      }));
    }
  }

  return result;
}

// ── STAFF Sections ───────────────────────────────────────────────────

function buildStaffSections(items: ArtifactItem[]): (Paragraph | Table)[] {
  const result: (Paragraph | Table)[] = [];

  const rankingData = findItem(items, 'staff_ranking') as Record<string, unknown> | null;
  if (rankingData) {
    result.push(heading('Candidate Ranking'));
    const candidates = ((rankingData as { candidates?: unknown[] }).candidates
      || (rankingData as { ranking?: unknown[] }).ranking
      || []) as Record<string, unknown>[];

    if (candidates.length > 0) {
      result.push(new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            headerCell('#'), headerCell('Name'), headerCell('Type'), headerCell('Fit Score'),
          ]}),
          ...candidates.map((c, i) => {
            const fit = Number(c.overall_fit_score ?? 0);
            const fitColor = fit >= 0.7 ? WORD_COLORS.success : fit >= 0.5 ? WORD_COLORS.warning : WORD_COLORS.critical;
            return new TableRow({ children: [
              dataCell(String(i + 1)),
              dataCell(String(c.full_name || '')),
              dataCell(String(c.leader_type || '').replace(/_/g, ' ')),
              dataCell(formatScoreRaw(fit), { color: fitColor, bold: true }),
            ]});
          }),
        ],
      }));
    }
  }

  const genomeData = findItem(items, 'staff_genome') as Record<string, unknown> | null;
  if (genomeData) {
    result.push(heading('Leadership Genome'));
    const dims = ((genomeData as { dimensions?: unknown[] }).dimensions || []) as Record<string, unknown>[];
    result.push(bodyText(`${(genomeData as { full_name?: string }).full_name || 'Leader'} — ${dims.length} dimensions profiled`, { bold: true }));

    if (dims.length > 0) {
      result.push(new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            headerCell('Dimension'), headerCell('Raw'), headerCell('Corrected'), headerCell('Sources'),
          ]}),
          ...dims.map(d => new TableRow({ children: [
            dataCell(formatDimension(String(d.dimension || ''))),
            dataCell(formatScoreRaw(Number(d.raw_score ?? 0))),
            dataCell(formatScoreRaw(Number(d.corrected_score ?? 0))),
            dataCell(String(d.source_count ?? 0)),
          ]})),
        ],
      }));
    }
  }

  const chemistryData = findItem(items, 'staff_chemistry') as Record<string, unknown> | null;
  if (chemistryData) {
    result.push(heading('Team Chemistry'));
    const assessments = ((chemistryData as { pairwise_assessments?: unknown[] }).pairwise_assessments || []) as Record<string, unknown>[];
    result.push(bodyText(`Average synergy: ${formatScoreRaw(Number((chemistryData as { average_synergy?: number }).average_synergy ?? 0))}`, { bold: true }));

    if (assessments.length > 0) {
      result.push(new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            headerCell('Team Member'), headerCell('Synergy'), headerCell('Key Dynamics'),
          ]}),
          ...assessments.map(a => {
            const sv = Number(a.synergy_score ?? 0);
            const color = sv >= 0.3 ? WORD_COLORS.success : sv < 0 ? WORD_COLORS.critical : WORD_COLORS.textMuted;
            const synergyDims = (a.synergy_dimensions as string[]) || [];
            const frictionDims = (a.friction_dimensions as string[]) || [];
            const dynamics = [
              ...synergyDims.map(d => `+${formatDimension(d)}`),
              ...frictionDims.map(d => `-${formatDimension(d)}`),
            ].join(', ');
            return new TableRow({ children: [
              dataCell(String(a.team_member_name || '')),
              dataCell(formatScoreRaw(sv), { color, bold: true }),
              dataCell(dynamics),
            ]});
          }),
        ],
      }));
    }
  }

  return result;
}

// ── LEARN Sections ───────────────────────────────────────────────────

function buildLearnSections(items: ArtifactItem[]): (Paragraph | Table)[] {
  const result: (Paragraph | Table)[] = [];

  const biasData = findItem(items, 'learn_biases') as Record<string, number> | null;
  if (biasData && typeof biasData === 'object' && !Array.isArray(biasData)) {
    result.push(heading('Bias Mirror'));
    const sorted = Object.entries(biasData).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

    result.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        new TableRow({ children: [
          headerCell('Dimension'), headerCell('Magnitude'), headerCell('Direction'),
        ]}),
        ...sorted.map(([dim, val]) => {
          const dir = val >= 0 ? 'Overweighted' : 'Underweighted';
          const color = val >= 0 ? WORD_COLORS.critical : '22D3EE';
          return new TableRow({ children: [
            dataCell(formatDimension(dim)),
            dataCell(`${val >= 0 ? '+' : ''}${(val * 100).toFixed(1)}%`, { bold: true }),
            dataCell(dir, { color }),
          ]});
        }),
      ],
    }));
  }

  const decisionsData = findItem(items, 'learn_decisions');
  if (decisionsData && Array.isArray(decisionsData)) {
    result.push(heading('Historical Decisions'));
    const decisions = decisionsData as Record<string, unknown>[];

    result.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        new TableRow({ children: [
          headerCell('Date'), headerCell('Role'), headerCell('Selected'), headerCell('Outcome'),
        ]}),
        ...decisions.map(d => {
          const outcomes = (d.outcomes || []) as Record<string, unknown>[];
          const latest = outcomes.length > 0
            ? outcomes.reduce((a, b) => Number(a.months_elapsed ?? 0) > Number(b.months_elapsed ?? 0) ? a : b)
            : null;
          const cat = String(latest?.outcome_category || 'pending');
          const catColor = cat === 'optimal' || cat === 'success' ? WORD_COLORS.success
            : cat === 'suboptimal' || cat === 'misstep' ? WORD_COLORS.warning
            : WORD_COLORS.critical;
          return new TableRow({ children: [
            dataCell(String(d.decision_date || '').slice(0, 10)),
            dataCell(String(d.role_title || '')),
            dataCell(String(d.selected_name || '')),
            dataCell(cat.toUpperCase(), { color: catColor, bold: true }),
          ]});
        }),
      ],
    }));
  }

  const replayData = findItem(items, 'learn_replay') as Record<string, unknown> | null;
  if (replayData) {
    result.push(heading('Decision Replay'));
    result.push(bodyText(`Selected: ${replayData.selected_candidate_name || 'N/A'}`, { bold: true }));
    result.push(bodyText(`Runner-Up: ${replayData.runner_up_candidate_name || 'N/A'}`));
    result.push(bodyText(`Rationale: ${replayData.decision_rationale || 'Not recorded'}`));
  }

  return result;
}

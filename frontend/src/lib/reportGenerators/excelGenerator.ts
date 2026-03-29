/**
 * Excel report generator — produces .xlsx blobs from artifact groups.
 * Lazy-loaded via dynamic import() to keep initial bundle small.
 */
import ExcelJS from 'exceljs';
import { type ArtifactGroup, type ArtifactItem } from '../../types/artifacts';
import {
  formatScore, formatScoreRaw, scoreToStatus, formatEUR, formatDate,
  formatDimension, HEADER_FILL, HEADER_FONT, HEADER_ALIGNMENT, statusFill,
} from './common';

// ── Helpers ──────────────────────────────────────────────────────────

function applyHeaderRow(sheet: ExcelJS.Worksheet) {
  const row = sheet.getRow(1);
  row.eachCell(cell => {
    cell.fill = HEADER_FILL as ExcelJS.FillPattern;
    cell.font = HEADER_FONT;
    cell.alignment = HEADER_ALIGNMENT;
  });
  row.height = 28;
}

function autoWidth(sheet: ExcelJS.Worksheet) {
  sheet.columns.forEach(col => {
    let max = 12;
    col.eachCell?.({ includeEmpty: false }, cell => {
      const len = String(cell.value ?? '').length;
      if (len > max) max = len;
    });
    col.width = Math.min(max + 4, 45);
  });
}

function findItem(items: ArtifactItem[], vizType: string): unknown | null {
  const item = items.find(i => i.vizType === vizType);
  return item?.data ?? null;
}

// ── Main entry point ─────────────────────────────────────────────────

export async function generateExcelReport(group: ArtifactGroup): Promise<Blob> {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'NEXUS Decision Intelligence';
  wb.created = new Date();

  // Add cover/summary sheet
  addCoverSheet(wb, group);

  // Dispatch to pipeline-specific sheets
  switch (group.mode) {
    case 'diagnose':
      addDiagnoseSheets(wb, group.items);
      break;
    case 'staff':
      addStaffSheets(wb, group.items);
      break;
    case 'learn':
      addLearnSheets(wb, group.items);
      break;
  }

  const buffer = await wb.xlsx.writeBuffer();
  return new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}

// ── Cover Sheet ──────────────────────────────────────────────────────

function addCoverSheet(wb: ExcelJS.Workbook, group: ArtifactGroup) {
  const sheet = wb.addWorksheet('Summary');

  sheet.mergeCells('A1:D1');
  const title = sheet.getCell('A1');
  title.value = `NEXUS ${group.mode.toUpperCase()} Report`;
  title.font = { bold: true, size: 18, color: { argb: 'FF0D47A1' } };
  title.alignment = { horizontal: 'left' };

  const meta: [string, string][] = [
    ['Pipeline', group.mode.toUpperCase()],
    ['Agent', group.agentName || 'NEXUS'],
    ['User Query', group.userQuery],
    ['Generated', formatDate(group.completedAt || group.createdAt)],
    ['Artifacts', `${group.items.length} data items collected`],
  ];

  meta.forEach(([label, value], i) => {
    const row = i + 3;
    sheet.getCell(`A${row}`).value = label;
    sheet.getCell(`A${row}`).font = { bold: true, color: { argb: 'FF64748B' } };
    sheet.getCell(`B${row}`).value = value;
  });

  // List artifact items
  const startRow = meta.length + 4;
  sheet.getCell(`A${startRow}`).value = 'Collected Data';
  sheet.getCell(`A${startRow}`).font = { bold: true, size: 13, color: { argb: 'FF0D47A1' } };

  group.items.forEach((item, i) => {
    const row = startRow + 1 + i;
    sheet.getCell(`A${row}`).value = item.label;
    sheet.getCell(`B${row}`).value = item.toolName;
    sheet.getCell(`B${row}`).font = { color: { argb: 'FF64748B' } };
  });

  sheet.getColumn('A').width = 25;
  sheet.getColumn('B').width = 60;
}

// ── DIAGNOSE Sheets ──────────────────────────────────────────────────

function addDiagnoseSheets(wb: ExcelJS.Workbook, items: ArtifactItem[]) {
  const heatmapData = findItem(items, 'diagnose_heatmap') as Record<string, unknown> | null;
  const cascadeData = findItem(items, 'diagnose_cascade') as Record<string, unknown> | null;

  if (heatmapData) {
    const sheet = wb.addWorksheet('Vulnerability Heatmap');
    const heatmap = (heatmapData as { heatmap?: unknown[] }).heatmap || [];
    const scenarioName = (heatmapData as { scenario_name?: string }).scenario_name || '';
    const resilience = (heatmapData as { aggregate_resilience_score?: number }).aggregate_resilience_score;
    const critCount = (heatmapData as { critical_count?: number }).critical_count ?? 0;
    const warnCount = (heatmapData as { warning_count?: number }).warning_count ?? 0;
    const covCount = (heatmapData as { covered_count?: number }).covered_count ?? 0;

    // Summary row
    sheet.getCell('A1').value = 'Scenario';
    sheet.getCell('B1').value = scenarioName;
    sheet.getCell('C1').value = 'Resilience';
    sheet.getCell('D1').value = resilience != null ? formatScore(resilience) : 'N/A';
    sheet.getCell('E1').value = `Critical: ${critCount}  |  Warning: ${warnCount}  |  Covered: ${covCount}`;
    sheet.getRow(1).font = { bold: true };

    // Heatmap table
    sheet.addRow([]);
    const headers = ['Role', 'Leader', 'Gap Score', 'Status'];

    // Add dimension columns if present
    const firstCell = heatmap[0] as Record<string, unknown> | undefined;
    const gapDims = firstCell?.gap_dimensions as Record<string, number> | undefined;
    const dimNames = gapDims ? Object.keys(gapDims) : [];
    dimNames.forEach(d => headers.push(formatDimension(d)));

    sheet.addRow(headers);
    applyHeaderRow(sheet); // applies to row 1, but we want row 3
    const headerRow = sheet.getRow(3);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const raw of heatmap) {
      const cell = raw as Record<string, unknown>;
      const rowData: (string | number)[] = [
        (cell.role_title as string) || '',
        (cell.leader_name as string) || 'VACANT',
        Number(cell.gap_score ?? 0),
        scoreToStatus(Number(cell.gap_score ?? 0)),
      ];

      const dims = (cell.gap_dimensions || {}) as Record<string, number>;
      dimNames.forEach(d => rowData.push(Number(dims[d] ?? 0)));

      const row = sheet.addRow(rowData);

      // Color the status cell
      const statusCell = row.getCell(4);
      statusCell.fill = statusFill(String(cell.status || '')) as ExcelJS.FillPattern;
      statusCell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    }

    autoWidth(sheet);
  }

  if (cascadeData) {
    const sheet = wb.addWorksheet('Cascade Impact');
    const chain = (cascadeData as { cascade_chain?: unknown[] }).cascade_chain || [];
    const totalImpact = (cascadeData as { mechanical_total_eur?: number }).mechanical_total_eur;
    const trigger = (cascadeData as { role_title?: string }).role_title || '';

    sheet.getCell('A1').value = 'Trigger Role';
    sheet.getCell('B1').value = trigger;
    sheet.getCell('C1').value = 'Total Exposure';
    sheet.getCell('D1').value = totalImpact != null ? formatEUR(totalImpact) : 'N/A';
    sheet.getRow(1).font = { bold: true };

    sheet.addRow([]);
    const headerRow = sheet.addRow([
      'Org Unit', 'Depth', 'Impact Score', 'Dependency Type',
      'Coupling Strength', 'Est. Cost (EUR)', 'Est. Delay (days)',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const raw of chain) {
      const node = raw as Record<string, unknown>;
      sheet.addRow([
        node.org_unit_name || '',
        node.depth ?? 0,
        Number(node.impact_score ?? 0).toFixed(3),
        node.dependency_type || '',
        Number(node.coupling_strength ?? 0).toFixed(2),
        formatEUR(Number(node.mechanical_cost_eur ?? 0)),
        node.estimated_delay_days ?? 0,
      ]);
    }

    autoWidth(sheet);
  }
}

// ── STAFF Sheets ─────────────────────────────────────────────────────

function addStaffSheets(wb: ExcelJS.Workbook, items: ArtifactItem[]) {
  const rankingData = findItem(items, 'staff_ranking');
  const genomeData = findItem(items, 'staff_genome');
  const chemistryData = findItem(items, 'staff_chemistry');
  const planData = findItem(items, 'staff_plan');

  // Ranking sheet
  if (rankingData) {
    const sheet = wb.addWorksheet('Candidate Ranking');
    const raw = rankingData as Record<string, unknown>;
    const candidates = (raw.candidates || raw.ranking || (Array.isArray(raw) ? raw : [])) as Record<string, unknown>[];

    const headerRow = sheet.addRow([
      'Rank', 'Name', 'Type', 'Overall Fit', 'Calibrated',
      'Top Strength', 'Top Gap',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    candidates.forEach((c, i) => {
      const strengths = (c.strengths as { dimension: string }[]) || [];
      const gaps = (c.gaps as { dimension: string }[]) || [];
      const row = sheet.addRow([
        i + 1,
        c.full_name || '',
        c.leader_type || '',
        formatScoreRaw(Number(c.mechanical_fit_score ?? 0)),
        c.calibration_applied ? 'Yes' : 'No',
        strengths[0]?.dimension ? formatDimension(strengths[0].dimension) : '',
        gaps[0]?.dimension ? formatDimension(gaps[0].dimension) : '',
      ]);

      // Color fit score
      const fitCell = row.getCell(4);
      const fitVal = Number(c.mechanical_fit_score ?? 0);
      if (fitVal >= 0.7) fitCell.font = { color: { argb: 'FF10B981' }, bold: true };
      else if (fitVal >= 0.5) fitCell.font = { color: { argb: 'FFF59E0B' }, bold: true };
      else fitCell.font = { color: { argb: 'FFEF4444' }, bold: true };
    });

    autoWidth(sheet);
  }

  // Genome sheet
  if (genomeData) {
    const sheet = wb.addWorksheet('Leadership Genome');
    const genome = genomeData as Record<string, unknown>;
    const dims = (genome.dimensions || []) as Record<string, unknown>[];

    sheet.getCell('A1').value = 'Leader';
    sheet.getCell('B1').value = (genome.full_name as string) || '';
    sheet.getCell('C1').value = 'Type';
    sheet.getCell('D1').value = (genome.leader_type as string) || '';
    sheet.getCell('E1').value = 'Overall Strength';
    sheet.getCell('F1').value = formatScoreRaw(Number(genome.overall_strength ?? 0));
    sheet.getRow(1).font = { bold: true };

    sheet.addRow([]);
    const headerRow = sheet.addRow([
      'Dimension', 'Raw Score', 'Corrected Score', 'CI Low', 'CI High', 'Sources',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const d of dims) {
      const ci = (d.confidence_interval || [0, 0]) as number[];
      sheet.addRow([
        formatDimension(String(d.dimension || '')),
        formatScoreRaw(Number(d.raw_score ?? 0)),
        formatScoreRaw(Number(d.corrected_score ?? 0)),
        formatScoreRaw(ci[0] ?? 0),
        formatScoreRaw(ci[1] ?? 0),
        d.source_count ?? 0,
      ]);
    }

    autoWidth(sheet);
  }

  // Chemistry sheet
  if (chemistryData) {
    const sheet = wb.addWorksheet('Team Chemistry');
    const chem = chemistryData as Record<string, unknown>;
    const assessments = (chem.pairwise_assessments || []) as Record<string, unknown>[];

    sheet.getCell('A1').value = 'Candidate';
    sheet.getCell('B1').value = (chem.candidate_name as string) || '';
    sheet.getCell('C1').value = 'Avg Synergy';
    sheet.getCell('D1').value = formatScoreRaw(Number(chem.average_synergy ?? 0));
    sheet.getRow(1).font = { bold: true };

    sheet.addRow([]);
    const headerRow = sheet.addRow([
      'Team Member', 'Role', 'Synergy Score', 'Synergy Dims', 'Friction Dims',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const a of assessments) {
      const synergyDims = (a.synergy_dimensions as string[]) || [];
      const frictionDims = (a.friction_dimensions as string[]) || [];
      const row = sheet.addRow([
        a.team_member_name || '',
        a.role_title || '',
        formatScoreRaw(Number(a.mechanical_synergy_score ?? 0)),
        synergyDims.map(formatDimension).join(', '),
        frictionDims.map(formatDimension).join(', '),
      ]);

      const scoreCell = row.getCell(3);
      const sv = Number(a.mechanical_synergy_score ?? 0);
      if (sv >= 0.3) scoreCell.font = { color: { argb: 'FF10B981' }, bold: true };
      else if (sv >= 0) scoreCell.font = { color: { argb: 'FF64748B' } };
      else scoreCell.font = { color: { argb: 'FFEF4444' }, bold: true };
    }

    autoWidth(sheet);
  }

  // Staffing Plan sheet
  if (planData) {
    const sheet = wb.addWorksheet('Staffing Plan');
    const plan = planData as Record<string, unknown>;
    const planItems = (plan.plan_items || []) as Record<string, unknown>[];

    sheet.getCell('A1').value = 'Total Cost';
    sheet.getCell('B1').value = formatEUR(Number(plan.total_cost_eur ?? 0));
    sheet.getCell('C1').value = 'Budget';
    sheet.getCell('D1').value = formatEUR(Number(plan.budget_eur ?? 0));
    sheet.getCell('E1').value = 'Within Budget';
    sheet.getCell('F1').value = plan.within_budget ? 'Yes' : 'No';
    sheet.getRow(1).font = { bold: true };

    sheet.addRow([]);
    const headerRow = sheet.addRow([
      'Role', 'Candidate', 'Strategy', 'Fit Score', 'Est. Cost',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const item of planItems) {
      sheet.addRow([
        item.role_title || '',
        item.recommended_candidate || '',
        String(item.sourcing_strategy || '').replace(/_/g, ' '),
        formatScoreRaw(Number(item.fit_score ?? 0)),
        formatEUR(Number(item.mechanical_cost_eur ?? item.estimated_cost_eur ?? 0)),
      ]);
    }

    autoWidth(sheet);
  }
}

// ── LEARN Sheets ─────────────────────────────────────────────────────

function addLearnSheets(wb: ExcelJS.Workbook, items: ArtifactItem[]) {
  const decisionsData = findItem(items, 'learn_decisions');
  const biasData = findItem(items, 'learn_biases');
  const replayData = findItem(items, 'learn_replay');

  // Decisions Timeline
  if (decisionsData) {
    const sheet = wb.addWorksheet('Decisions Timeline');
    const decisions = (Array.isArray(decisionsData) ? decisionsData : []) as Record<string, unknown>[];

    const headerRow = sheet.addRow([
      'Date', 'Role', 'Selected Candidate', 'Outcome', 'Rationale',
    ]);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    for (const d of decisions) {
      const outcomes = (d.outcomes || []) as Record<string, unknown>[];
      const latest = outcomes.length > 0
        ? outcomes.reduce((a, b) => Number(a.months_elapsed ?? 0) > Number(b.months_elapsed ?? 0) ? a : b)
        : null;
      sheet.addRow([
        String(d.decision_date || '').slice(0, 10),
        d.role_title || '',
        d.selected_name || '',
        latest?.outcome_category || 'pending',
        String(d.decision_rationale || '').slice(0, 100),
      ]);
    }

    autoWidth(sheet);
  }

  // Bias Analysis
  if (biasData && typeof biasData === 'object' && !Array.isArray(biasData)) {
    const sheet = wb.addWorksheet('Bias Analysis');
    const biases = biasData as Record<string, number>;

    const headerRow = sheet.addRow(['Dimension', 'Bias Magnitude (%)', 'Direction']);
    headerRow.eachCell(cell => {
      cell.fill = HEADER_FILL as ExcelJS.FillPattern;
      cell.font = HEADER_FONT;
      cell.alignment = HEADER_ALIGNMENT;
    });
    headerRow.height = 28;

    const sorted = Object.entries(biases)
      .map(([dim, val]) => ({ dim, val }))
      .sort((a, b) => Math.abs(b.val) - Math.abs(a.val));

    for (const { dim, val } of sorted) {
      const row = sheet.addRow([
        formatDimension(dim),
        `${val >= 0 ? '+' : ''}${(val * 100).toFixed(1)}%`,
        val >= 0 ? 'Overweighted' : 'Underweighted',
      ]);
      const dirCell = row.getCell(3);
      dirCell.font = { color: { argb: val >= 0 ? 'FFEF4444' : 'FF22D3EE' }, bold: true };
    }

    autoWidth(sheet);
  }

  // Decision Replay
  if (replayData) {
    const sheet = wb.addWorksheet('Decision Replay');
    const replay = replayData as Record<string, unknown>;

    sheet.getCell('A1').value = 'Selected';
    sheet.getCell('B1').value = (replay.selected_candidate_name as string) || '';
    sheet.getCell('C1').value = 'Runner-Up';
    sheet.getCell('D1').value = (replay.runner_up_candidate_name as string) || 'N/A';
    sheet.getRow(1).font = { bold: true };

    sheet.getCell('A2').value = 'Rationale';
    sheet.getCell('B2').value = (replay.decision_rationale as string) || '';
    sheet.mergeCells('B2:D2');

    // Genome comparison if both exist
    const selGenome = (replay.selected_candidate_genome || {}) as Record<string, number>;
    const runGenome = (replay.runner_up_candidate_genome || {}) as Record<string, number>;
    const allDims = [...new Set([...Object.keys(selGenome), ...Object.keys(runGenome)])].sort();

    if (allDims.length > 0) {
      sheet.addRow([]);
      const headerRow = sheet.addRow(['Dimension', 'Selected Score', 'Runner-Up Score', 'Delta']);
      headerRow.eachCell(cell => {
        cell.fill = HEADER_FILL as ExcelJS.FillPattern;
        cell.font = HEADER_FONT;
        cell.alignment = HEADER_ALIGNMENT;
      });
      headerRow.height = 28;

      for (const dim of allDims) {
        const sel = selGenome[dim] ?? 0;
        const run = runGenome[dim] ?? 0;
        sheet.addRow([
          formatDimension(dim),
          formatScoreRaw(sel),
          formatScoreRaw(run),
          `${(sel - run) >= 0 ? '+' : ''}${formatScoreRaw(sel - run)}`,
        ]);
      }
    }

    autoWidth(sheet);
  }
}

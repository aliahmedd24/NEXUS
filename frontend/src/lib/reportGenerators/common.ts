/** Shared helpers for Excel and Word report generators. */

export function formatScore(n: number): string {
  return (n * 100).toFixed(1) + '%';
}

export function formatScoreRaw(n: number): string {
  return n.toFixed(3);
}

export function scoreToStatus(gap: number): 'CRITICAL' | 'WARNING' | 'COVERED' {
  if (gap >= 0.35) return 'CRITICAL';
  if (gap >= 0.15) return 'WARNING';
  return 'COVERED';
}

export function formatEUR(n: number): string {
  if (n >= 1_000_000) return `\u20AC${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `\u20AC${(n / 1_000).toFixed(0)}K`;
  return `\u20AC${n.toFixed(0)}`;
}

export function formatDate(ts: number): string {
  return new Date(ts).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDimension(d: string): string {
  return d.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// ── Excel style presets ──────────────────────────────────────────────

/** BMW brand blue for headers. */
export const BRAND_BLUE = '0D47A1';
export const HEADER_FILL = { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FF0D47A1' } };
export const HEADER_FONT = { bold: true, color: { argb: 'FFFFFFFF' }, size: 11 };
export const HEADER_ALIGNMENT = { horizontal: 'center' as const, vertical: 'middle' as const };

export const RED_FILL = { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FFEF4444' } };
export const YELLOW_FILL = { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FFF59E0B' } };
export const GREEN_FILL = { type: 'pattern' as const, pattern: 'solid' as const, fgColor: { argb: 'FF10B981' } };

export function statusFill(status: string) {
  if (status === 'red' || status === 'CRITICAL') return RED_FILL;
  if (status === 'yellow' || status === 'WARNING') return YELLOW_FILL;
  return GREEN_FILL;
}

// ── Word style presets ───────────────────────────────────────────────

export const WORD_COLORS = {
  brandBlue: '0D47A1',
  critical: 'EF4444',
  warning: 'F59E0B',
  success: '10B981',
  textDark: '1A1A2E',
  textMuted: '64748B',
} as const;

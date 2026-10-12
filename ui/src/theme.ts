// ============================================================
// ui/src/theme.ts
// Design tokens for TalentScope.
// ============================================================

export const PRIMARY = '#4F46E5';
export const PRIMARY_DARK = '#4338CA';
export const PRIMARY_LIGHT = '#EEF2FF';
export const VIOLET = '#7C3AED';
export const VIOLET_LIGHT = '#F5F3FF';

export const SUCCESS = '#10B981';
export const SUCCESS_LIGHT = '#ECFDF5';
export const WARNING = '#F59E0B';
export const WARNING_LIGHT = '#FFFBEB';
export const DANGER = '#EF4444';
export const DANGER_LIGHT = '#FEF2F2';
export const INFO = '#3B82F6';
export const INFO_LIGHT = '#EFF6FF';

export const BG = '#F8FAFC';
export const SURFACE = '#FFFFFF';
export const SURFACE_ALT = '#F1F5F9';
export const INK = '#111827';
export const TEXT_PRIMARY = '#0F172A';
export const TEXT_SECONDARY = '#475569';
export const TEXT_MUTED = '#64748B';
export const BORDER = '#E2E8F0';
export const BORDER_STRONG = '#CBD5E1';

export const RADIUS = {
  sm: '10px',
  md: '14px',
  lg: '18px',
  xl: '24px',
} as const;

export const MOTION = {
  fast: '160ms',
  base: '220ms',
  slow: '520ms',
  ease: 'cubic-bezier(0.22, 1, 0.36, 1)',
} as const;

export const LEVEL_COLORS: Record<string, string> = {
  excellent: '#15803D',
  good: '#16A34A',
  average: '#F59E0B',
  below_average: '#EA580C',
  weak: '#DC2626',
};

export const LEVEL_LABELS: Record<string, string> = {
  excellent: 'Excellent',
  good: 'Good',
  average: 'Average',
  below_average: 'Below Average',
  weak: 'Weak',
};

export function levelColor(level: string): string {
  return LEVEL_COLORS[level] ?? TEXT_MUTED;
}

export function scoreLevel(score: number): string {
  if (score >= 90) return 'excellent';
  if (score >= 75) return 'good';
  if (score >= 60) return 'average';
  if (score >= 40) return 'below_average';
  return 'weak';
}

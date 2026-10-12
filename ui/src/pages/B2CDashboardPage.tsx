import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { b2cApi, type AnalysisHistoryItem } from '@/lib/api';
import { BORDER, PRIMARY, TEXT_MUTED, TEXT_PRIMARY, VIOLET } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

function formatDate(value: string | null) {
  if (!value) return 'Date unavailable';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
}

export default function B2CDashboardPage() {
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<AnalysisHistoryItem[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const data = await b2cApi.history(100);
        if (active) {
          setAnalyses(data);
          setLoadState('ready');
        }
      } catch {
        if (active) setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [refreshKey]);

  const thisMonthCount = useMemo(() => {
    const now = new Date();
    return analyses.filter((a) => {
      if (!a.created_at) return false;
      const d = new Date(a.created_at);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    }).length;
  }, [analyses]);

  const scored = analyses.filter((a) => typeof a.ats_score === 'number');
  const avgScore = scored.length
    ? Math.round(scored.reduce((s, a) => s + (a.ats_score ?? 0), 0) / scored.length)
    : null;

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Overview</p>
        <h1 className="text-4xl font-bold tracking-tight text-ink-900">
          Welcome back, {user?.email?.split('@')[0] ?? 'there'}
        </h1>
        <p className="text-ink-600">Your resume analysis workspace.</p>
      </div>

      {/* CTA */}
      <div className="relative overflow-hidden rounded-[26px] p-8 text-white animate-fade-in-up" style={{ background: `linear-gradient(135deg, ${PRIMARY} 0%, #312E81 100%)` }}>
        <div aria-hidden className="absolute -right-16 -top-24 h-72 w-72 rounded-full border border-white/15" />
        <div aria-hidden className="absolute -right-4 -top-12 h-52 w-52 rounded-full border border-white/10" />
        <div className="max-w-lg space-y-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">Next best action</p>
          <h2 className="text-2xl font-bold">Analyze a Resume</h2>
          <p className="text-sm text-white/85">Upload a resume and get an AI-powered ATS analysis in seconds.</p>
          <Link to="/analyze" className="inline-flex mt-2 h-11 items-center rounded-xl bg-white px-6 text-sm font-semibold text-brand-700 hover:bg-white/90 transition hover-lift">
            Start Analysis
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Analyses" value={loadState === 'loading' ? '…' : analyses.length} caption="Recorded in history" />
        <Stat label="This month" value={loadState === 'loading' ? '…' : thisMonthCount} caption="From available history" />
        <Stat label="Average score" value={loadState === 'loading' ? '…' : avgScore === null ? '—' : `${avgScore}`} caption="Across scored analyses" />
        <Stat label="Status" value="Active" caption="Account is enabled" color={VIOLET} />
      </div>

      {/* Recent activity */}
      <div className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Your workspace</p>
            <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink-900">Recent activity</h2>
          </div>
          <Link to="/history" className="text-sm font-medium text-brand-600 hover:text-brand-700">View history →</Link>
        </div>

        <div className="rounded-2xl border bg-white" style={{ borderColor: BORDER }}>
          {loadState === 'loading' && (
            <div className="space-y-3 p-6">{[1, 2, 3].map((i) => <div key={i} className="h-12 skeleton" />)}</div>
          )}

          {loadState === 'error' && (
            <div className="py-12 text-center text-sm text-ink-500">
              <p>Unable to load your activity.</p>
              <button type="button" onClick={() => setRefreshKey((value) => value + 1)} className="mt-3 text-sm font-semibold text-brand-600 hover:text-brand-700">Try again</button>
            </div>
          )}

          {loadState === 'ready' && analyses.length === 0 && (
            <div className="py-14 text-center">
              <div className="mx-auto h-12 w-12 rounded-xl bg-brand-50 grid place-items-center text-2xl">📄</div>
              <h3 className="mt-4 text-base font-semibold text-ink-900">No analyses yet</h3>
              <p className="mt-1 text-sm text-ink-500">Upload your first resume to see your results here.</p>
              <Link to="/analyze" className="mt-4 inline-flex text-sm font-semibold text-brand-600 hover:text-brand-700">
                Analyze your first resume →
              </Link>
            </div>
          )}

          {loadState === 'ready' && analyses.length > 0 && (
            <div className="divide-y" style={{ borderColor: BORDER }}>
              {analyses.slice(0, 5).map((a) => (
                <div key={a.id} className="flex items-center justify-between gap-4 px-6 py-4 hover:bg-brand-50/40 transition-colors">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="h-10 w-10 rounded-xl bg-brand-50 grid place-items-center text-sm font-semibold text-brand-700">CV</span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-ink-900">Analysis · {a.id.slice(0, 8)}</p>
                      <p className="text-xs text-ink-500">{formatDate(a.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 shrink-0">
                    <span className="badge badge-success">Completed</span>
                    <span className="text-sm font-semibold text-ink-900 tabular-nums">
                      {typeof a.ats_score === 'number' ? `${Math.round(a.ats_score)}%` : '—'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, caption, color }: { label: string; value: string | number; caption: string; color?: string }) {
  return (
    <div className="rounded-[20px] border bg-white p-5 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-medium" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-3 text-3xl font-bold tracking-tight tabular-nums" style={{ color: color ?? TEXT_PRIMARY }}>{value}</p>
      <p className="mt-1 text-xs" style={{ color: TEXT_MUTED }}>{caption}</p>
    </div>
  );
}

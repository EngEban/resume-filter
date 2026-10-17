import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, type TenantOverview } from '@/lib/api';
import { DANGER, LEVEL_COLORS, PRIMARY, SUCCESS, TEXT_MUTED, TEXT_PRIMARY, WARNING } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

export default function B2BAnalyticsOverviewPage() {
  const [overview, setOverview] = useState<TenantOverview | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const data = await b2bApi.getOverview();
        if (!active) return;
        setOverview(data);
        setLoadState('ready');
      } catch {
        if (active) setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [refreshKey]);

  const distTotal = overview
    ? Object.values(overview.score_distribution).reduce((s, v) => s + v, 0)
    : 0;
  const strongestBand = overview ? getStrongestBand(overview.score_distribution) : '—';

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Organization insights</p>
          <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900">Analytics Overview</h1>
          <p className="text-ink-600">Company-wide hiring insights across all batches.</p>
        </div>

        {loadState === 'loading' && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => <div key={i} className="h-32 skeleton" />)}
          </div>
        )}

        {loadState === 'error' && (
          <div className="rounded-2xl border border-ink-100 bg-white p-8 text-center shadow-soft-md">
            <p className="text-sm" style={{ color: DANGER }}>Unable to load analytics.</p>
            <button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="btn btn-primary mt-4">
              Try Again
            </button>
          </div>
        )}

        {loadState === 'ready' && overview && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Stat label="Total batches" value={overview.total_batches} />
              <Stat label="Total resumes" value={overview.total_resumes} />
              <Stat label="Completed" value={overview.total_completed} color={SUCCESS} />
              <Stat label="Failed" value={overview.total_failed} color={overview.total_failed > 0 ? DANGER : undefined} />
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <Stat
                label="Average ATS score"
                value={overview.avg_ats_score === null ? '—' : Math.round(overview.avg_ats_score)}
                color={PRIMARY}
              />
              <Stat
                label="Strongest band"
                value={strongestBand}
                color={WARNING}
              />
              <Stat
                label="Completion rate"
                value={
                  overview.total_resumes > 0
                    ? `${Math.round((overview.total_completed / overview.total_resumes) * 100)}%`
                    : '—'
                }
                color={SUCCESS}
              />
            </div>

            {distTotal > 0 && (
                <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Quality signal</p>
                <h2 className="mt-1 text-xl font-bold text-ink-900">Score distribution (all time)</h2>
                <div className="mt-6 space-y-4">
                  {[
                    { key: 'excellent' as const, label: 'Excellent (90-100)', color: LEVEL_COLORS.excellent },
                    { key: 'good' as const, label: 'Good (75-89)', color: LEVEL_COLORS.good },
                    { key: 'average' as const, label: 'Average (60-74)', color: LEVEL_COLORS.average },
                    { key: 'below_average' as const, label: 'Below avg (40-59)', color: LEVEL_COLORS.below_average },
                    { key: 'weak' as const, label: 'Weak (0-39)', color: LEVEL_COLORS.weak },
                  ].map((row) => {
                    const count = overview.score_distribution[row.key] ?? 0;
                    const pct = Math.round((count / distTotal) * 100);
                    return (
                      <div key={row.key}>
                        <div className="flex justify-between text-xs">
                          <span className="text-ink-700">{row.label}</span>
                          <span style={{ color: TEXT_MUTED }}>{count} · {pct}%</span>
                        </div>
                        <div className="mt-2 h-1.5 rounded-full bg-ink-100 overflow-hidden transition-all duration-700">
                          <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: row.color }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {overview.top_missing_keywords.length > 0 && (
              <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Pattern signals</p>
                <h2 className="mt-1 text-xl font-bold text-ink-900">Top missing keywords</h2>
                <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {overview.top_missing_keywords.slice(0, 12).map((k) => (
                    <div key={k.keyword} className="flex items-center justify-between gap-3 rounded-xl border border-ink-100 px-3 py-2.5">
                      <span className="truncate text-sm text-ink-700">{k.keyword}</span>
                      <span className="shrink-0 text-xs font-bold text-brand-600 tabular-nums">{k.count}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {overview.recent_batches.length > 0 && (
              <section className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Activity</p>
                    <h2 className="mt-1 text-xl font-bold text-ink-900">Recent batches</h2>
                  </div>
                  <Link to="/b2b/batches" className="text-sm font-medium text-brand-600 hover:text-brand-700">View all <i className="fa-solid fa-arrow-right" /></Link>
                </div>
                <div className="overflow-hidden rounded-3xl border border-ink-100 bg-white shadow-soft-lg">
                  <div className="divide-y divide-ink-100">
                    {overview.recent_batches.slice(0, 5).map((b) => (
                      <Link key={b.id} to={`/b2b/batches/${b.id}`} className="block px-6 py-4 hover:bg-brand-50/40 transition-colors">
                        <div className="flex items-center justify-between gap-4">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-ink-900">{b.job_title}</p>
                            <p className="text-xs mt-0.5" style={{ color: TEXT_MUTED }}>{b.total_resumes} resumes</p>
                          </div>
                          <span className={`badge ${b.status === 'completed' ? 'badge-success' : 'badge-info'}`}>{b.status}</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </B2BShell>
  );
}

function Stat({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="rounded-2xl border border-ink-100 bg-white p-5 shadow-soft-md transition-all hover:-translate-y-1">
      <p className="text-xs font-medium text-ink-500">{label}</p>
      <p className="mt-3 font-display text-3xl font-bold tracking-tight tabular-nums" style={{ color: color ?? TEXT_PRIMARY }}>{value}</p>
    </div>
  );
}

function getStrongestBand(distribution: TenantOverview['score_distribution']) {
  if ((distribution.excellent ?? 0) > 0) return '90–100';
  if ((distribution.good ?? 0) > 0) return '75–89';
  if ((distribution.average ?? 0) > 0) return '60–74';
  if ((distribution.below_average ?? 0) > 0) return '40–59';
  if ((distribution.weak ?? 0) > 0) return '0–39';
  return '—';
}

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { useAuth } from '@/contexts/AuthContext';
import { b2bApi, type TenantOverview } from '@/lib/api';
import { BORDER, DANGER, PRIMARY, SUCCESS, TEXT_MUTED } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

export default function B2BDashboardPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<TenantOverview | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');

  useEffect(() => {
    let active = true;
    async function load() {
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
  }, []);

  const distTotal = overview
    ? Object.values(overview.score_distribution).reduce((s, v) => s + v, 0)
    : 0;

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        {/* Header */}
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Organization workspace</p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">
            Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}
          </h1>
          <p className="text-ink-600">Your recruiting intelligence workspace.</p>
        </div>

        {/* Primary CTA */}
        <div className="relative overflow-hidden rounded-[26px] p-8 text-white animate-fade-in-up" style={{ background: `linear-gradient(135deg, ${PRIMARY} 0%, #312E81 100%)` }}>
          <div aria-hidden className="absolute -right-20 -top-24 h-80 w-80 rounded-full border border-white/15" />
          <div aria-hidden className="absolute right-8 top-8 h-44 w-44 rounded-full border border-white/10" />
          <div className="max-w-lg space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">Next best action</p>
            <h2 className="text-2xl font-bold">Create a resume batch</h2>
            <p className="text-sm text-white/85">
              Upload resumes for a job and get a ranked shortlist with ATS scores.
            </p>
            <Link to="/b2b/batches" className="inline-flex mt-2 h-11 items-center rounded-xl bg-white px-6 text-sm font-semibold text-brand-700 hover:bg-white/90 transition">
              Go to Batches
            </Link>
          </div>
        </div>

        {/* Stats */}
        {loadState === 'loading' && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => <div key={i} className="h-32 skeleton" />)}
          </div>
        )}

        {loadState === 'error' && (
          <div className="rounded-2xl border bg-white p-6 text-center" style={{ borderColor: BORDER }}>
            <p className="text-sm" style={{ color: DANGER }}>Unable to load overview.</p>
          </div>
        )}

        {loadState === 'ready' && overview && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Stat label="Total batches" value={overview.total_batches} />
              <Stat label="Total resumes" value={overview.total_resumes} />
              <Stat label="Completed" value={overview.total_completed} color={SUCCESS} />
              <Stat
                label="Average score"
                value={overview.avg_ats_score === null ? '—' : Math.round(overview.avg_ats_score)}
                color={PRIMARY}
              />
            </div>

            {/* Quick actions */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 stagger">
              <ActionCard
                icon="📦"
                title="Batches"
                description="View and manage all resume batches."
                target="/b2b/batches"
              />
              <ActionCard
                icon="👥"
                title="Candidates"
                description="Browse all candidates across batches."
                target="/b2b/candidates"
              />
              <ActionCard
                icon="📊"
                title="Analytics"
                description="See company-wide hiring insights."
                target="/b2b/analytics"
              />
              <ActionCard
                icon="📥"
                title="Exports"
                description="Download reports in Excel or PDF."
                target="/b2b/exports"
              />
              <ActionCard
                icon="⚙️"
                title="AI Settings"
                description="Connect your own LLM provider."
                target="/b2b/settings"
              />
              <ActionCard
                icon="➕"
                title="New Batch"
                description="Upload resumes for screening."
                target="/b2b/batches"
              />
            </div>

            {/* Recent batches */}
            {overview.recent_batches.length > 0 && (
              <section className="space-y-4">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Recent activity</p>
                    <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink-900">Latest batches</h2>
                  </div>
                  <Link to="/b2b/batches" className="text-sm font-medium text-brand-600 hover:text-brand-700">
                    View all →
                  </Link>
                </div>

                <div className="rounded-2xl border bg-white overflow-hidden" style={{ borderColor: BORDER }}>
                  <div className="divide-y" style={{ borderColor: BORDER }}>
                    {overview.recent_batches.slice(0, 5).map((b) => (
                      <Link
                        key={b.id}
                        to={`/b2b/batches/${b.id}`}
                        className="block px-6 py-4 hover:bg-brand-50/40 transition-colors"
                      >
                        <div className="flex items-center justify-between gap-4">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-ink-900">{b.job_title}</p>
                            <p className="mt-1 text-xs" style={{ color: TEXT_MUTED }}>
                              {b.total_resumes} resumes · {b.id.slice(0, 8)}
                            </p>
                          </div>
                          <div className="flex items-center gap-4 shrink-0">
                            <span className={`badge ${b.status === 'completed' ? 'badge-success' : b.status === 'failed' ? 'badge-danger' : 'badge-info'}`}>
                              {b.status}
                            </span>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              </section>
            )}

            {/* Distribution */}
            {distTotal > 0 && (
              <section className="rounded-2xl border bg-white p-6" style={{ borderColor: BORDER }}>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Quality signal</p>
                <h2 className="mt-1 text-xl font-bold text-ink-900">Company-wide score distribution</h2>
                <div className="mt-6 space-y-4">
                  {[
                    { key: 'excellent' as const, label: 'Excellent (90-100)', color: '#15803D' },
                    { key: 'good' as const, label: 'Good (75-89)', color: '#16A34A' },
                    { key: 'average' as const, label: 'Average (60-74)', color: '#F59E0B' },
                    { key: 'below_average' as const, label: 'Below avg (40-59)', color: '#EA580C' },
                    { key: 'weak' as const, label: 'Weak (0-39)', color: '#DC2626' },
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
          </>
        )}
      </div>
    </B2BShell>
  );
}

function Stat({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="rounded-[20px] border bg-white p-5 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-medium" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-3 text-3xl font-bold tracking-tight tabular-nums" style={{ color: color ?? '#0F172A' }}>{value}</p>
    </div>
  );
}

function ActionCard({ icon, title, description, target }: { icon: string; title: string; description: string; target: string }) {
  return (
    <Link
      to={target}
      className="block rounded-2xl border bg-white p-5 card-interactive hover-lift"
      style={{ borderColor: BORDER }}
    >
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-brand-50 text-lg">{icon}</div>
      <p className="mt-3 text-sm font-semibold text-ink-900">{title}</p>
      <p className="mt-1 text-xs" style={{ color: TEXT_MUTED }}>{description}</p>
      <p className="mt-3 text-xs font-semibold text-brand-600">Open →</p>
    </Link>
  );
}

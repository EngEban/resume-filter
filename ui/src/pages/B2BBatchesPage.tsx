import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, type Batch } from '@/lib/api';
import { BORDER, DANGER, PRIMARY, SUCCESS, TEXT_MUTED, WARNING } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

function formatDate(value: string | null) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit',
  }).format(d);
}

function formatStatus(status: string) {
  return status.replace(/[_-]+/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

function statusClass(status: string): string {
  switch (status.toLowerCase()) {
    case 'completed': return 'badge-success';
    case 'processing': return 'badge-info';
    case 'failed': return 'badge-danger';
    default: return 'badge-neutral';
  }
}

function processingCount(b: Batch) {
  return Math.max(b.total_resumes - b.completed - b.failed, 0);
}

export default function B2BBatchesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [refreshKey, setRefreshKey] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const data = await b2bApi.listBatches({
          search: search.trim() || undefined,
          status: statusFilter || undefined,
          limit: 100,
        });
        if (!active) return;
        setBatches(data);
        setLoadState('ready');
      } catch {
        if (active) setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [refreshKey, search, statusFilter]);

  const metrics = useMemo(
    () =>
      batches.reduce(
        (s, b) => {
          s.resumes += b.total_resumes;
          s.processing += processingCount(b);
          s.completed += b.completed;
          return s;
        },
        { resumes: 0, processing: 0, completed: 0 },
      ),
    [batches],
  );

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Organization workspace</p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900">Resume Batches</h1>
            <p className="text-ink-600">Manage your organization's resume screening workflows.</p>
          </div>
          <Link to="/b2b/batches/new" className="btn btn-primary">
            + New Batch
          </Link>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Total batches" value={loadState === 'loading' ? '…' : batches.length} caption="Batches in view" />
          <Metric label="Resumes processed" value={loadState === 'loading' ? '…' : metrics.resumes} caption="Across returned batches" />
          <Metric label="Processing" value={loadState === 'loading' ? '…' : metrics.processing} caption="Awaiting completion" color={WARNING} />
          <Metric label="Completed" value={loadState === 'loading' ? '…' : metrics.completed} caption="Resumes with results" color={SUCCESS} />
        </div>

        <section className="space-y-4">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Screening workflows</p>
              <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink-900">All batches</h2>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search job titles"
                className="input sm:w-56"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input sm:w-40"
              >
                <option value="">All statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          <div className="overflow-hidden rounded-[24px] border bg-white shadow-card" style={{ borderColor: BORDER }}>
            {loadState === 'loading' && (
              <div className="space-y-3 p-5">
                {[1, 2, 3].map((i) => <div key={i} className="h-24 skeleton" />)}
              </div>
            )}

            {loadState === 'error' && (
              <div className="py-14 text-center">
                <p className="text-sm" style={{ color: DANGER }}>Unable to load batches.</p>
                <button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="mt-4 text-sm font-semibold text-brand-600 hover:text-brand-700">Try Again</button>
              </div>
            )}

            {loadState === 'ready' && batches.length === 0 && (
              <div className="py-16 text-center">
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-brand-50 text-2xl">📦</div>
                <h3 className="mt-4 text-base font-semibold text-ink-900">
                  {search || statusFilter ? 'No matching batches' : 'No batches yet'}
                </h3>
                <p className="mt-1 text-sm text-ink-500">
                  {search || statusFilter ? 'Try different filters.' : 'Create your first batch to get started.'}
                </p>
                {!search && !statusFilter && (
                  <Link to="/b2b/batches/new" className="mt-4 inline-block text-sm font-semibold text-brand-600 hover:text-brand-700">
                    Create First Batch
                  </Link>
                )}
              </div>
            )}

            {loadState === 'ready' && batches.length > 0 && (
              <div className="divide-y" style={{ borderColor: BORDER }}>
                {batches.map((b) => {
                  const proc = processingCount(b);
                  const pct = b.total_resumes > 0 ? Math.min(100, Math.round((b.completed / b.total_resumes) * 100)) : 0;
                  return (
                    <Link key={b.id} to={`/b2b/batches/${b.id}`} className="block px-6 py-5 transition-colors duration-150 hover:border-l-2 hover:border-l-brand-500 hover:bg-brand-50/40">
                      <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[1fr_100px_100px_180px_120px] lg:items-center lg:gap-6">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-ink-900">{b.job_title}</p>
                          <p className="mt-1 text-xs" style={{ color: TEXT_MUTED }}>
                            {formatDate(b.created_at)} · {b.id.slice(0, 8)}
                          </p>
                        </div>
                        <div className="text-sm">
                          <p className="text-xs lg:hidden" style={{ color: TEXT_MUTED }}>Resumes</p>
                          <p className="font-medium text-ink-900">{b.total_resumes}</p>
                        </div>
                        <div className="text-sm">
                          <p className="text-xs lg:hidden" style={{ color: TEXT_MUTED }}>Completed</p>
                          <p className="font-medium text-ink-900">{b.completed}</p>
                        </div>
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span style={{ color: TEXT_MUTED }}>{b.completed}/{b.total_resumes}</span>
                            <span className="font-medium text-ink-700">{pct}%</span>
                          </div>
                          <div className="h-1.5 overflow-hidden rounded-full bg-ink-100 transition-all duration-700">
                            <div className="h-full rounded-full" style={{ width: `${pct}%`, background: PRIMARY }} />
                          </div>
                          <p className="text-[11px]" style={{ color: TEXT_MUTED }}>{proc} processing · {b.failed} failed</p>
                        </div>
                        <div className="flex lg:justify-end">
                          <span className={`badge ${statusClass(b.status)}`}>{formatStatus(b.status)}</span>
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      </div>
    </B2BShell>
  );
}

function Metric({ label, value, caption, color }: { label: string; value: string | number; caption: string; color?: string }) {
  return (
    <div className="rounded-2xl border bg-white p-5 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-medium" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-3 text-3xl font-bold tracking-tight tabular-nums" style={{ color: color ?? '#0F172A' }}>{value}</p>
      <p className="mt-1 text-xs" style={{ color: TEXT_MUTED }}>{caption}</p>
    </div>
  );
}

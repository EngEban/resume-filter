import { useEffect, useMemo, useState, type ChangeEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, APIError, type Batch, type Resume } from '@/lib/api';
import { BORDER, DANGER, PRIMARY, SUCCESS, TEXT_MUTED, WARNING, scoreLevel, levelColor } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';
type ExportType = 'xlsx' | 'pdf';

function formatDate(v: string | null) {
  if (!v) return '—';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(d);
}

function statusClass(s: string) {
  switch (s.toLowerCase()) {
    case 'completed': return 'badge-success';
    case 'processing': return 'badge-info';
    case 'failed': return 'badge-danger';
    default: return 'badge-neutral';
  }
}

export default function B2BBatchDetailsPage() {
  const { batchId = '' } = useParams<{ batchId: string }>();
  const [batch, setBatch] = useState<Batch | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [notFound, setNotFound] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [minScore, setMinScore] = useState('');
  const [sort, setSort] = useState('score_desc');
  const [exporting, setExporting] = useState<ExportType | null>(null);
  const [reprocessing, setReprocessing] = useState(false);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      setNotFound(false);
      try {
        const b = await b2bApi.getBatch(batchId);
        const r = await b2bApi.listResumes(batchId, {
          search: search.trim() || undefined,
          status: statusFilter || undefined,
          min_score: minScore !== '' ? Number(minScore) : undefined,
          sort,
        });
        if (!active) return;
        setBatch(b);
        setResumes(r);
        setLoadState('ready');
      } catch (err) {
        if (!active) return;
        if (err instanceof APIError && (err.status === 404 || err.status === 403)) {
          setNotFound(true);
          setLoadState('ready');
          return;
        }
        setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [batchId, search, statusFilter, minScore, sort, refreshKey]);

  // Auto-refresh while processing
  useEffect(() => {
    if (batch?.status !== 'pending' && batch?.status !== 'processing') return;
    const t = setInterval(() => setRefreshKey((v) => v + 1), 5000);
    return () => clearInterval(t);
  }, [batch?.status]);

  const summary = useMemo(() => {
    const scores = resumes.flatMap((r) => (typeof r.ats_score === 'number' ? [r.ats_score] : []));
    return {
      processing: batch ? Math.max(batch.total_resumes - batch.completed - batch.failed, 0) : 0,
      avg: scores.length ? Math.round(scores.reduce((a, s) => a + s, 0) / scores.length) : null,
    };
  }, [batch, resumes]);

  const progress = batch && batch.total_resumes > 0
    ? Math.min(100, Math.round(((batch.completed + batch.failed) / batch.total_resumes) * 100))
    : 0;

  async function exportBatch(type: ExportType) {
    if (!batch) return;
    setExporting(type);
    try {
      const { blob, filename } = type === 'xlsx'
        ? await b2bApi.exportBatchExcel(batch.id)
        : await b2bApi.exportBatchPdf(batch.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch {
      /* ignore */
    } finally {
      setExporting(null);
    }
  }

  async function reprocess() {
    if (!batch || reprocessing) return;
    if (!window.confirm('Reprocess failed resumes?')) return;
    setReprocessing(true);
    try {
      const updated = await b2bApi.reprocessBatch(batch.id);
      setBatch(updated);
      setRefreshKey((v) => v + 1);
    } catch {
      /* ignore */
    } finally {
      setReprocessing(false);
    }
  }

  function handleMinScore(e: ChangeEvent<HTMLInputElement>) {
    const v = e.target.value;
    if (v === '' || (Number(v) >= 0 && Number(v) <= 100)) setMinScore(v);
  }

  if (loadState === 'loading') {
    return <B2BShell><div className="space-y-4"><div className="h-8 w-64 skeleton" /><div className="h-32 skeleton" /><div className="h-96 skeleton" /></div></B2BShell>;
  }

  if (loadState === 'error') {
    return (
      <B2BShell>
        <div className="py-24 text-center">
          <h1 className="text-2xl font-bold text-ink-900">Unable to load batch</h1>
          <button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="btn btn-primary mt-6">Try Again</button>
        </div>
      </B2BShell>
    );
  }

  if (notFound || !batch) {
    return (
      <B2BShell>
        <div className="py-24 text-center">
          <h1 className="text-2xl font-bold text-ink-900">Batch not found</h1>
          <Link to="/b2b/batches" className="btn btn-primary mt-6 inline-flex">Back to Batches</Link>
        </div>
      </B2BShell>
    );
  }

  const failed = batch.failed > 0;

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        {/* Breadcrumb */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Link to="/b2b/batches" className="font-medium text-brand-600 hover:text-brand-700">Batches</Link>
          <span style={{ color: TEXT_MUTED }}>/</span>
          <span className="truncate max-w-xs" style={{ color: TEXT_MUTED }}>{batch.job_title}</span>
        </div>

        {/* Header */}
        <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-end">
          <div className="min-w-0 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Batch details</p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900 break-words">{batch.job_title}</h1>
            <p className="text-sm" style={{ color: TEXT_MUTED }}>
              Created {formatDate(batch.created_at)} · {batch.total_resumes} resumes · {batch.id.slice(0, 8)}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`badge ${statusClass(batch.status)}`}>{batch.status}</span>
            {failed && (
              <button type="button" onClick={() => void reprocess()} disabled={reprocessing} className="btn btn-secondary hover-lift">
                {reprocessing ? 'Reprocessing…' : 'Reprocess Failed'}
              </button>
            )}
            <Link to={`/b2b/batches/${batch.id}/analytics`} className="btn btn-secondary hover-lift">Analytics</Link>
            <Link to={`/b2b/batches/${batch.id}/compare`} className="btn btn-secondary hover-lift">Compare</Link>
            <button type="button" onClick={() => void exportBatch('xlsx')} disabled={Boolean(exporting)} className="btn btn-secondary hover-lift">
              {exporting === 'xlsx' ? 'Exporting…' : 'Excel'}
            </button>
            <button type="button" onClick={() => void exportBatch('pdf')} disabled={Boolean(exporting)} className="btn btn-secondary hover-lift">
              {exporting === 'pdf' ? 'Exporting…' : 'PDF'}
            </button>
          </div>
        </div>

        {/* Summary */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <Metric label="Total" value={batch.total_resumes} />
          <Metric label="Completed" value={batch.completed} color={SUCCESS} />
          <Metric label="Processing" value={summary.processing} color={WARNING} />
          <Metric label="Failed" value={batch.failed} color={failed ? DANGER : undefined} />
          <Metric label="Avg Score" value={summary.avg === null ? '—' : summary.avg} color={PRIMARY} />
        </div>

        {/* Progress */}
        <div className="signal-ring rounded-[24px] border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Processing progress</p>
              <p className="mt-2 text-sm text-ink-700">
                <strong className="text-ink-900">{batch.completed + batch.failed}</strong> of {batch.total_resumes} processed
              </p>
            </div>
            <span className="text-2xl font-bold text-brand-600 tabular-nums">{progress}%</span>
          </div>
          <div className="mt-4 h-2 rounded-full bg-ink-100 overflow-hidden">
            <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progress}%`, background: `linear-gradient(90deg, ${PRIMARY}, #7C3AED)` }} />
          </div>
        </div>

        {/* Resumes */}
        <section className="space-y-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Candidate results</p>
            <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink-900">Resumes in this batch</h2>
          </div>

          {/* Filters */}
          <div className="flex flex-col gap-2 rounded-2xl border bg-white p-3 sm:flex-row sm:items-center" style={{ borderColor: BORDER }}>
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search resumes…" className="input flex-1" />
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input sm:w-40">
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
            <input type="number" min={0} max={100} value={minScore} onChange={handleMinScore} placeholder="Min score" className="input sm:w-32" />
            <select value={sort} onChange={(e) => setSort(e.target.value)} className="input sm:w-44">
              <option value="score_desc">Highest score</option>
              <option value="score_asc">Lowest score</option>
              <option value="name_asc">Name A→Z</option>
              <option value="recent">Recent</option>
            </select>
          </div>

          <div className="overflow-hidden rounded-[24px] border bg-white shadow-card" style={{ borderColor: BORDER }}>
            {resumes.length === 0 ? (
              <div className="py-16 text-center">
                <p className="text-sm text-ink-500">No resumes match the filters.</p>
              </div>
            ) : (
              <div className="divide-y" style={{ borderColor: BORDER }}>
                <div className="hidden lg:grid grid-cols-[1.6fr_120px_140px_140px] gap-4 px-6 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: TEXT_MUTED, borderBottom: `1px solid ${BORDER}` }}>
                  <span>Candidate / File</span>
                  <span>Score</span>
                  <span>Status</span>
                  <span className="text-right">Added</span>
                </div>
                {resumes.map((r) => {
                  const hasScore = typeof r.ats_score === 'number';
                  const level = hasScore ? scoreLevel(r.ats_score as number) : 'weak';
                  return (
                    <Link key={r.id} to={`/b2b/resumes/${r.id}`} className="block px-6 py-5 hover:bg-brand-50/40 hover:border-l-2 hover:border-l-brand-500 transition-colors duration-150 hover:translate-x-0.5">
                      <div className="flex flex-col gap-3 lg:grid lg:grid-cols-[1.6fr_120px_140px_140px] lg:items-center lg:gap-4">
                        <div className="flex items-center gap-3 min-w-0">
                          <span className="h-10 w-10 shrink-0 rounded-xl bg-brand-50 grid place-items-center text-xs font-bold text-brand-700">CV</span>
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-ink-900">{r.candidate_name || 'Unnamed candidate'}</p>
                            <p className="truncate text-xs" style={{ color: TEXT_MUTED }}>{r.file_name}</p>
                            {r.candidate_email && <p className="truncate text-xs" style={{ color: TEXT_MUTED }}>{r.candidate_email}</p>}
                          </div>
                        </div>
                        <div>
                          <p className="lg:hidden text-xs" style={{ color: TEXT_MUTED }}>Score</p>
                          <p className="text-xl font-bold tabular-nums" style={{ color: hasScore ? levelColor(level) : TEXT_MUTED }}>
                            {hasScore ? Math.round(r.ats_score as number) : '—'}
                            {hasScore && <span className="text-xs font-normal ml-1" style={{ color: TEXT_MUTED }}>/100</span>}
                          </p>
                        </div>
                        <div>
                          <span className={`badge ${statusClass(r.status)}`}>{r.status}</span>
                        </div>
                        <div className="lg:text-right text-xs" style={{ color: TEXT_MUTED }}>{formatDate(r.created_at)}</div>
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

function Metric({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="rounded-2xl border bg-white p-5 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-medium" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-3 text-2xl font-bold tracking-tight tabular-nums" style={{ color: color ?? '#0F172A' }}>{value}</p>
    </div>
  );
}

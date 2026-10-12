import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, APIError, type BatchAnalytics, type Batch } from '@/lib/api';
import { BORDER, DANGER, PRIMARY, SUCCESS, TEXT_MUTED, WARNING } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';
type ExportType = 'xlsx';

function formatDate(v: string | null) {
  if (!v) return '—';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(d);
}

export default function B2BAnalyticsPage() {
  const { batchId = '' } = useParams<{ batchId: string }>();
  const [batch, setBatch] = useState<Batch | null>(null);
  const [analytics, setAnalytics] = useState<BatchAnalytics | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [notFound, setNotFound] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [exporting, setExporting] = useState<ExportType | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const [b, a] = await Promise.all([
          b2bApi.getBatch(batchId),
          b2bApi.getAnalytics(batchId),
        ]);
        if (!active) return;
        setBatch(b);
        setAnalytics(a);
        setLoadState('ready');
      } catch (err) {
        if (!active) return;
        if (err instanceof APIError && (err.status === 403 || err.status === 404)) {
          setNotFound(true); setLoadState('ready'); return;
        }
        setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [batchId, refreshKey]);

  const distribution = analytics?.score_distribution ?? null;
  const distTotal = useMemo(
    () => (distribution ? Object.values(distribution).reduce((s, v) => s + v, 0) : 0),
    [distribution],
  );
  const hasData = distTotal > 0;

  async function exportBatch() {
    if (!batch) return;
    setExporting('xlsx');
    try {
      const { blob, filename } = await b2bApi.exportBatchExcel(batch.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ } finally { setExporting(null); }
  }

  if (loadState === 'loading') {
    return <B2BShell><div className="space-y-4"><div className="h-10 w-56 skeleton" /><div className="h-40 skeleton" /><div className="h-96 skeleton" /></div></B2BShell>;
  }

  if (loadState === 'error') {
    return <B2BShell><div className="py-24 text-center"><h1 className="text-2xl font-bold text-ink-900">Unable to load analytics</h1><button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="btn btn-primary mt-6">Try Again</button></div></B2BShell>;
  }

  if (notFound || !batch || !analytics) {
    return <B2BShell><div className="py-24 text-center"><h1 className="text-2xl font-bold text-ink-900">Batch not found</h1><Link to="/b2b/batches" className="btn btn-primary mt-6 inline-flex">Back to Batches</Link></div></B2BShell>;
  }

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Link to="/b2b/batches" className="font-medium text-brand-600 hover:text-brand-700">Batches</Link>
          <span style={{ color: TEXT_MUTED }}>/</span>
          <Link to={`/b2b/batches/${batch.id}`} className="truncate max-w-xs font-medium text-brand-600 hover:text-brand-700">{batch.job_title}</Link>
          <span style={{ color: TEXT_MUTED }}>/</span>
          <span style={{ color: TEXT_MUTED }}>Analytics</span>
        </div>

        <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-end">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Batch Intelligence</p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900">Analytics</h1>
            <p className="text-ink-600">Understand the results and performance of this resume batch.</p>
            <p className="text-sm" style={{ color: TEXT_MUTED }}>{batch.job_title} · {formatDate(batch.created_at)}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link to={`/b2b/batches/${batch.id}`} className="btn btn-secondary">View Batch</Link>
            <Link to={`/b2b/batches/${batch.id}/compare`} className="btn btn-secondary">Compare</Link>
            <button type="button" onClick={() => void exportBatch()} disabled={Boolean(exporting)} className="btn btn-primary">
              {exporting ? 'Exporting…' : 'Export Results'}
            </button>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <Metric label="Total" value={analytics.total_resumes} />
          <Metric label="Completed" value={analytics.completed} color={SUCCESS} />
          <Metric label="Average" value={analytics.avg_score === null ? '—' : Math.round(analytics.avg_score)} color={PRIMARY} />
          <Metric label="Top score" value={analytics.max_score === null ? '—' : Math.round(analytics.max_score)} />
          <Metric label="Pending" value={analytics.pending} color={WARNING} />
          <Metric label="Failed" value={analytics.failed} color={analytics.failed > 0 ? DANGER : undefined} />
        </div>

        <div className="grid gap-5 xl:grid-cols-2">
          <ProcessingOverview analytics={analytics} />
          <DistributionCard distribution={distribution} total={distTotal} />
        </div>

        {!hasData && (
          <div className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Quality signal</p>
            <h2 className="mt-2 text-xl font-bold text-ink-900">Analytics not available yet</h2>
            <p className="mt-2 text-sm text-ink-500">Analytics will appear once resume analyses complete.</p>
            <Link to={`/b2b/batches/${batch.id}`} className="mt-4 inline-flex text-sm font-semibold text-brand-600 hover:text-brand-700">View Batch →</Link>
          </div>
        )}

        <section className="rounded-[24px] border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
          <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Pattern signals</p>
          <h2 className="mt-2 text-xl font-bold text-ink-900">Top missing keywords</h2>
          {analytics.top_missing_keywords.length > 0 ? (
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {analytics.top_missing_keywords.slice(0, 9).map((k) => (
                <div key={k.keyword} className="flex items-center justify-between gap-3 rounded-xl border px-3 py-2.5 hover-scale" style={{ borderColor: BORDER }}>
                  <span className="truncate text-sm text-ink-700">{k.keyword}</span>
                  <span className="shrink-0 text-xs font-bold text-brand-600 tabular-nums">{k.count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-4 text-sm text-ink-500">Not enough data yet.</p>
          )}
        </section>
      </div>
    </B2BShell>
  );
}

function Metric({ label, value, color }: { label: string; value: number | string; color?: string }) {
  return (
    <div className="rounded-[20px] border bg-white p-4 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-medium" style={{ color: TEXT_MUTED }}>{label}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight tabular-nums" style={{ color: color ?? '#0F172A' }}>{value}</p>
    </div>
  );
}

function ProcessingOverview({ analytics }: { analytics: BatchAnalytics }) {
  const total = analytics.total_resumes || 1;
  const segments = [
    { label: 'Completed', value: analytics.completed, color: PRIMARY },
    { label: 'Pending', value: analytics.pending, color: '#94A3B8' },
    { label: 'Failed', value: analytics.failed, color: DANGER },
  ];
  return (
    <div className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Operational view</p>
      <h2 className="mt-2 text-xl font-bold text-ink-900">Processing overview</h2>
      <div className="mt-6 flex h-3 overflow-hidden rounded-full bg-ink-100">
        {segments.map((s) => (
          <div key={s.label} style={{ width: `${(s.value / total) * 100}%`, background: s.color }} />
        ))}
      </div>
      <div className="mt-6 grid grid-cols-3 gap-3">
        {segments.map((s) => (
          <div key={s.label} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
            <div>
              <p className="text-xs" style={{ color: TEXT_MUTED }}>{s.label}</p>
              <p className="text-lg font-bold text-ink-900 tabular-nums">{s.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DistributionCard({ distribution, total }: { distribution: BatchAnalytics['score_distribution'] | null; total: number }) {
  const rows: Array<{ key: keyof NonNullable<BatchAnalytics['score_distribution']>; label: string; color: string }> = [
    { key: 'excellent', label: 'Excellent (90-100)', color: '#15803D' },
    { key: 'good', label: 'Good (75-89)', color: '#16A34A' },
    { key: 'average', label: 'Average (60-74)', color: '#F59E0B' },
    { key: 'below_average', label: 'Below avg (40-59)', color: '#EA580C' },
    { key: 'weak', label: 'Weak (0-39)', color: '#DC2626' },
  ];
  return (
    <div className="rounded-2xl border bg-white p-6 hover-lift" style={{ borderColor: BORDER }}>
      <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Quality signal</p>
      <h2 className="mt-2 text-xl font-bold text-ink-900">Score distribution</h2>
      {distribution && total > 0 ? (
        <div className="mt-6 space-y-4">
            {rows.map((row) => {
            const count = distribution[row.key] ?? 0;
            const pct = Math.round((count / total) * 100);
            return (
              <div key={row.key}>
                <div className="flex justify-between text-xs">
                  <span className="text-ink-700">{row.label}</span>
                  <span style={{ color: TEXT_MUTED }}>{count} · {pct}%</span>
                </div>
                <div className="mt-2 h-1.5 rounded-full bg-ink-100 overflow-hidden transition-all duration-700">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, background: row.color }} />
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="mt-6 text-sm text-ink-500">Not enough data yet.</p>
      )}
    </div>
  );
}

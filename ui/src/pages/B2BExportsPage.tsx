import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, type Batch } from '@/lib/api';
import { BORDER, DANGER, PRIMARY, TEXT_MUTED } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

function formatDate(v: string | null) {
  if (!v) return '—';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(d);
}

export default function B2BExportsPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const data = await b2bApi.listBatches({ limit: 100 });
        if (!active) return;
        setBatches(data);
        setLoadState('ready');
      } catch {
        if (active) setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, []);

  async function download(batchId: string, type: 'xlsx' | 'pdf') {
    const key = `${batchId}-${type}`;
    setDownloading(key);
    try {
      const { blob, filename } = type === 'xlsx'
        ? await b2bApi.exportBatchExcel(batchId)
        : await b2bApi.exportBatchPdf(batchId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ } finally {
      setDownloading(null);
    }
  }

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Data center</p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Exports</h1>
          <p className="text-ink-600">Download your batch results in Excel or PDF format.</p>
        </div>

        {loadState === 'loading' && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-20 skeleton" />)}
          </div>
        )}

        {loadState === 'error' && (
          <div className="rounded-2xl border bg-white p-8 text-center" style={{ borderColor: BORDER }}>
            <p className="text-sm" style={{ color: DANGER }}>Unable to load batches.</p>
          </div>
        )}

        {loadState === 'ready' && batches.length === 0 && (
          <div className="rounded-2xl border bg-white py-16 text-center" style={{ borderColor: BORDER }}>
            <div className="mx-auto h-12 w-12 rounded-xl bg-brand-50 grid place-items-center text-2xl"><i className="fa-solid fa-download" /></div>
            <h3 className="mt-4 text-base font-semibold text-ink-900">No batches to export</h3>
            <p className="mt-1 text-sm text-ink-500">Create a batch first to enable exports.</p>
            <Link to="/b2b/batches" className="mt-4 inline-flex text-sm font-semibold text-brand-600 hover:text-brand-700">
              Go to Batches <i className="fa-solid fa-arrow-right" />
            </Link>
          </div>
        )}

        {loadState === 'ready' && batches.length > 0 && (
          <div className="overflow-hidden rounded-[24px] border bg-white shadow-card" style={{ borderColor: BORDER }}>
            <div className="divide-y" style={{ borderColor: BORDER }}>
              <div className="hidden lg:grid grid-cols-[1.5fr_120px_120px_280px] gap-4 px-6 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: TEXT_MUTED, borderBottom: `1px solid ${BORDER}` }}>
                <span>Batch</span>
                <span>Resumes</span>
                <span>Date</span>
                <span className="text-right">Download</span>
              </div>
              {batches.map((b) => (
                <div key={b.id} className="px-6 py-4 hover:bg-brand-50/40 transition-colors">
                  <div className="flex flex-col gap-3 lg:grid lg:grid-cols-[1.5fr_120px_120px_280px] lg:items-center lg:gap-4">
                    <div className="min-w-0">
                      <Link to={`/b2b/batches/${b.id}`} className="block truncate text-sm font-medium text-ink-900 hover:text-brand-600">
                        {b.job_title}
                      </Link>
                      <p className="text-xs mt-0.5" style={{ color: TEXT_MUTED }}>{b.id.slice(0, 8)}</p>
                    </div>
                    <div className="text-sm text-ink-700">{b.total_resumes}</div>
                    <div className="text-xs" style={{ color: TEXT_MUTED }}>{formatDate(b.created_at)}</div>
                    <div className="flex lg:justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => void download(b.id, 'xlsx')}
                        disabled={downloading === `${b.id}-xlsx`}
                        className="btn btn-secondary btn-sm hover-lift"
                      >
                        {downloading === `${b.id}-xlsx` ? '…' : <><i className="fa-solid fa-chart-pie" /> Excel</>}
                      </button>
                      <button
                        type="button"
                        onClick={() => void download(b.id, 'pdf')}
                        disabled={downloading === `${b.id}-pdf`}
                        className="btn btn-secondary btn-sm hover-lift"
                      >
                        {downloading === `${b.id}-pdf` ? '…' : <><i className="fa-solid fa-file-lines" /> PDF</>}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="rounded-2xl border bg-blue-50/40 p-5" style={{ borderColor: '#DBEAFE' }}>
          <p className="text-sm font-semibold" style={{ color: PRIMARY }}><i className="fa-solid fa-lightbulb" /> About exports</p>
          <ul className="mt-2 text-sm text-ink-600 space-y-1 list-disc list-inside">
            <li><strong>Excel</strong>: ranked list of all candidates with scores and matched/missing keywords.</li>
            <li><strong>PDF</strong>: full report with summary statistics and top candidates.</li>
          </ul>
        </div>
      </div>
    </B2BShell>
  );
}

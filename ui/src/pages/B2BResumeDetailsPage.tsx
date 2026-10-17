import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, APIError, type Resume } from '@/lib/api';
import { DANGER, PRIMARY, SUCCESS, TEXT_MUTED, WARNING, levelColor, scoreLevel } from '@/theme';

type LoadState = 'loading' | 'ready' | 'error';

function formatDate(v: string | null) {
  if (!v) return '—';
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return '—';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }).format(d);
}

function formatLabel(v: string) {
  return v.replace(/[_-]/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

export default function B2BResumeDetailsPage() {
  const { resumeId = '' } = useParams<{ resumeId: string }>();
  const [report, setReport] = useState<Resume | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [notFound, setNotFound] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const data = await b2bApi.getResume(resumeId);
        if (!active) return;
        setReport(data);
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
  }, [resumeId, refreshKey]);

  async function exportPdf() {
    if (!report) return;
    setExporting(true);
    try {
      const { blob, filename } = await b2bApi.exportResumePdf(report.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ } finally { setExporting(false); }
  }

  if (loadState === 'loading') {
    return <B2BShell><div className="space-y-4"><div className="h-12 w-96 skeleton" /><div className="h-64 skeleton" /></div></B2BShell>;
  }

  if (loadState === 'error') {
    return <B2BShell><div className="page-enter py-24 text-center"><h1 className="font-display text-2xl font-bold text-ink-900">Unable to load resume</h1><button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="btn btn-primary mt-6">Try Again</button></div></B2BShell>;
  }

  if (notFound || !report) {
    return <B2BShell><div className="page-enter py-24 text-center"><h1 className="font-display text-2xl font-bold text-ink-900">Resume not found</h1><Link to="/b2b/batches" className="btn btn-primary mt-6 inline-flex">Back to Batches</Link></div></B2BShell>;
  }

  const hasScore = typeof report.ats_score === 'number';
  const level = hasScore ? scoreLevel(report.ats_score as number) : 'weak';
  const breakdown = report.score_breakdown ?? {};
  const entries = Object.entries(breakdown).filter(([, v]) => typeof v === 'number');
  const missing = report.missing_keywords ?? [];
  const suggestions = report.suggestions ?? [];

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <Link to="/b2b/batches" className="font-medium text-brand-600 hover:text-brand-700">Batches</Link>
          <span style={{ color: TEXT_MUTED }}>/</span>
          <span style={{ color: TEXT_MUTED }}>Resume</span>
        </div>

        <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-end">
          <div className="min-w-0 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Candidate report</p>
            <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900 break-words">{report.candidate_name || 'Unnamed candidate'}</h1>
            <p className="text-sm" style={{ color: TEXT_MUTED }}>{report.file_name} · {formatDate(report.created_at)}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`badge ${report.status === 'completed' ? 'badge-success' : report.status === 'failed' ? 'badge-danger' : 'badge-info'}`}>{report.status}</span>
            {hasScore && <span className="text-3xl font-bold tabular-nums" style={{ color: levelColor(level) }}>{Math.round(report.ats_score as number)}</span>}
            <button type="button" onClick={() => void exportPdf()} disabled={exporting} className="btn btn-primary">
              {exporting ? 'Exporting…' : 'Export PDF'}
            </button>
          </div>
        </div>

        {report.status === 'failed' && (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 shadow-soft-sm">
            <p className="text-sm font-semibold" style={{ color: DANGER }}>This analysis did not complete.</p>
            {report.error_message && <p className="mt-1 text-xs text-red-700">{report.error_message}</p>}
          </div>
        )}

        <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
          <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Candidate information</p>
            <h2 className="mt-2 text-xl font-bold text-ink-900">Resume overview</h2>
            <dl className="mt-6 divide-y divide-ink-100">
              <Row label="Email" value={report.candidate_email ?? '—'} />
              <Row label="Phone" value={report.candidate_phone ?? '—'} />
              <Row label="Status" value={report.status} />
              <Row label="File" value={report.file_name} />
            </dl>
          </section>

          <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Analysis signal</p>
            <h2 className="mt-2 text-xl font-bold text-ink-900">Score breakdown</h2>
            {entries.length > 0 ? (
              <div className="mt-6 space-y-4">
                {entries.map(([key, value]) => {
                  const pct = Math.max(0, Math.min(100, Number(value)));
                  return (
                    <div key={key}>
                      <div className="flex justify-between text-sm">
                        <span className="text-ink-700">{formatLabel(key)}</span>
                        <span className="font-semibold text-ink-900 tabular-nums">{pct.toFixed(1)}</span>
                      </div>
                      <div className="mt-2 h-1.5 rounded-full bg-ink-100 overflow-hidden transition-all duration-700">
                        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: PRIMARY }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="mt-6 text-sm text-ink-500">Score breakdown not available.</p>
            )}
          </section>
        </div>

        <div className="grid gap-5 xl:grid-cols-2">
          <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Improvement signal</p>
            <h2 className="mt-2 text-xl font-bold text-ink-900">Missing keywords</h2>
            {missing.length > 0 ? (
              <div className="mt-5 flex flex-wrap gap-2">
                {missing.map((k) => (
                  <span key={k} className="rounded-lg bg-red-50 px-2.5 py-1.5 text-xs font-medium text-red-700">{k}</span>
                ))}
              </div>
            ) : (
              <p className="mt-5 text-sm text-ink-500">No missing keywords.</p>
            )}
          </section>

          <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-soft-md hover-lift">
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Next signals</p>
            <h2 className="mt-2 text-xl font-bold text-ink-900">Suggestions</h2>
            {suggestions.length > 0 ? (
              <div className="mt-5 space-y-3">
                {suggestions.map((s, i) => {
                  const obj = s as Record<string, unknown>;
                  const desc = typeof obj.description === 'string' ? obj.description : '';
                  const type = typeof obj.type === 'string' ? obj.type : '';
                  const priority = typeof obj.priority === 'string' ? obj.priority : '';
                  const color = priority === 'high' ? DANGER : priority === 'low' ? SUCCESS : WARNING;
                  return (
                    <div key={i} className="border-l-2 pl-3" style={{ borderColor: color }}>
                      {type && <p className="text-xs font-semibold uppercase tracking-wider" style={{ color }}>{type}</p>}
                      <p className="mt-1 text-sm text-ink-700">{desc}</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="mt-5 text-sm text-ink-500">No suggestions.</p>
            )}
          </section>
        </div>
      </div>
    </B2BShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:justify-between">
      <dt className="text-xs" style={{ color: TEXT_MUTED }}>{label}</dt>
      <dd className="text-sm font-medium text-ink-900 break-all sm:max-w-[60%] sm:text-right">{value}</dd>
    </div>
  );
}

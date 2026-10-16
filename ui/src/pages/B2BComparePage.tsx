import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, APIError } from '@/lib/api';
import { BORDER, DANGER, TEXT_MUTED, levelColor, scoreLevel } from '@/theme';

type Candidate = {
  id: string;
  name?: string;
  candidate_name?: string | null;
  email?: string | null;
  candidate_email?: string | null;
  phone?: string | null;
  candidate_phone?: string | null;
  ats_score: number | null;
  score_breakdown?: Record<string, number>;
  missing_keywords?: string[];
  status: string;
};

type LoadState = 'loading' | 'ready' | 'error';


export default function B2BComparePage() {
  const { batchId = '' } = useParams<{ batchId: string }>();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [limit, setLimit] = useState('5');
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [notFound, setNotFound] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const res = await b2bApi.compare(batchId, Number(limit));
        if (!active) return;
        setCandidates(res.candidates as Candidate[]);
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
  }, [batchId, limit]);

  async function exportComparison() {
    setExporting(true);
    try {
      const { blob, filename } = await b2bApi.exportComparison(batchId, Number(limit));
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch { /* ignore */ } finally { setExporting(false); }
  }

  if (loadState === 'loading') {
    return <B2BShell><div className="grid gap-4 md:grid-cols-3">{[1, 2, 3].map((i) => <div key={i} className="h-72 skeleton" />)}</div></B2BShell>;
  }

  if (loadState === 'error') {
    return <B2BShell><div className="py-24 text-center"><h1 className="text-2xl font-bold text-ink-900">Unable to load comparison</h1></div></B2BShell>;
  }

  if (notFound) {
    return <B2BShell><div className="py-24 text-center"><h1 className="text-2xl font-bold text-ink-900">Batch not found</h1><Link to="/b2b/batches" className="btn btn-primary mt-6 inline-flex">Back to Batches</Link></div></B2BShell>;
  }

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-end">
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Candidate review</p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900">Compare candidates</h1>
            <p className="text-ink-600">Review candidates side by side.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link to={`/b2b/batches/${batchId}`} className="btn btn-secondary">View Batch</Link>
            <button type="button" onClick={() => void exportComparison()} disabled={exporting || candidates.length === 0} className="btn btn-primary">
              {exporting ? 'Exporting…' : 'Export Comparison'}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 rounded-2xl border bg-white p-4" style={{ borderColor: BORDER }}>
          <p className="text-sm text-ink-600">Compare top candidates side by side.</p>
          <select value={limit} onChange={(e) => setLimit(e.target.value)} className="input w-44">
            <option value="3">3 candidates</option>
            <option value="5">5 candidates</option>
            <option value="10">10 candidates</option>
          </select>
        </div>

        {candidates.length === 0 ? (
          <div className="rounded-2xl border bg-white py-16 text-center" style={{ borderColor: BORDER }}>
            <h3 className="text-base font-semibold text-ink-900">No candidates to compare</h3>
            <p className="mt-1 text-sm text-ink-500">Results appear once this batch has scored resumes.</p>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3 stagger">
            {candidates.map((c, idx) => {
              const score = c.ats_score;
              const hasScore = typeof score === 'number';
              const level = hasScore ? scoreLevel(score) : 'weak';
              const name = c.candidate_name ?? c.name ?? 'Unnamed candidate';
              const email = c.candidate_email ?? c.email;
              const phone = c.candidate_phone ?? c.phone;
              return (
                <div key={c.id} className="rounded-[24px] border bg-white p-6 space-y-4 card-interactive hover-lift animate-scale-in" style={{ borderColor: BORDER }}>
                  <div className="flex items-start justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-brand-600">#{idx + 1}</span>
                    <span className="text-3xl font-bold tabular-nums animate-pulse-soft" style={{ color: hasScore ? levelColor(level) : TEXT_MUTED }}>
                      {hasScore ? Math.round(score) : '—'}
                      {hasScore && <span className="text-xs font-normal ml-1" style={{ color: TEXT_MUTED }}>/100</span>}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="h-10 w-10 rounded-xl bg-brand-50 grid place-items-center text-xs font-bold text-brand-700">CV</span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink-900">{name}</p>
                      {email && <p className="truncate text-xs" style={{ color: TEXT_MUTED }}>{email}</p>}
                      {phone && <p className="truncate text-xs" style={{ color: TEXT_MUTED }}>{phone}</p>}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t" style={{ borderColor: BORDER }}>
                    <span className={`badge ${c.status === 'completed' ? 'badge-success' : c.status === 'failed' ? 'badge-danger' : 'badge-info'}`}>{c.status}</span>
                    <Link to={`/b2b/resumes/${c.id}`} className="text-xs font-semibold text-brand-600 hover:text-brand-700">View Resume <i className="fa-solid fa-arrow-right" /></Link>
                  </div>

                  {c.missing_keywords && c.missing_keywords.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: TEXT_MUTED }}>Missing keywords</p>
                      <div className="flex flex-wrap gap-1.5">
                        {c.missing_keywords.slice(0, 8).map((k) => (
                          <span key={k} className="px-2 py-1 rounded-lg text-[11px] font-medium" style={{ background: '#FEF2F2', color: DANGER }}>{k}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </B2BShell>
  );
}

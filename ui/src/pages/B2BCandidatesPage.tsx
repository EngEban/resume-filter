import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import B2BShell from '../components/B2BShell';
import { b2bApi, type Batch, type Resume } from '@/lib/api';
import { BORDER, DANGER, TEXT_MUTED, levelColor, scoreLevel } from '@/theme';

type CandidateRow = Resume & { batch_id: string; batch_title: string };
type LoadState = 'loading' | 'ready' | 'error';

export default function B2BCandidatesPage() {
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [minScore, setMinScore] = useState('');
  const [sort, setSort] = useState('score_desc');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
      try {
        const batches: Batch[] = await b2bApi.listBatches({ limit: 100 });
        const results = await Promise.all(
          batches.map(async (b) => {
            try {
              const resumes = await b2bApi.listResumes(b.id, { sort: 'score_desc' });
              return resumes.map((r) => ({
                ...r,
                batch_id: b.id,
                batch_title: b.job_title,
              })) as CandidateRow[];
            } catch {
              return [];
            }
          }),
        );
        if (!active) return;
        setCandidates(results.flat());
        setLoadState('ready');
      } catch {
        if (active) setLoadState('error');
      }
    }
    void load();
    return () => { active = false; };
  }, [refreshKey]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const min = minScore !== '' ? Number(minScore) : null;
    let rows = candidates.filter((c) => {
      const name = (c.candidate_name ?? '').toLowerCase();
      const email = (c.candidate_email ?? '').toLowerCase();
      const file = (c.file_name ?? '').toLowerCase();
      const matchesSearch = !q || name.includes(q) || email.includes(q) || file.includes(q);
      const matchesStatus = !statusFilter || c.status === statusFilter;
      const score = typeof c.ats_score === 'number' ? c.ats_score : null;
      const matchesScore = min === null || (score !== null && score >= min);
      return matchesSearch && matchesStatus && matchesScore;
    });

    rows = rows.slice().sort((a, b) => {
      if (sort === 'score_asc') return (a.ats_score ?? -1) - (b.ats_score ?? -1);
      if (sort === 'name_asc') return (a.candidate_name ?? '').localeCompare(b.candidate_name ?? '');
      if (sort === 'recent') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      return (b.ats_score ?? -1) - (a.ats_score ?? -1);
    });

    return rows;
  }, [candidates, search, statusFilter, minScore, sort]);

  return (
    <B2BShell>
      <div className="space-y-8 page-enter">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Organization workspace</p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Candidates</h1>
          <p className="text-ink-600">All candidates across your batches.</p>
        </div>

        <div className="flex flex-col gap-2 rounded-2xl border bg-white p-3 sm:flex-row sm:items-center" style={{ borderColor: BORDER }}>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, email, or file…"
            className="input flex-1"
          />
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input sm:w-40">
            <option value="">All statuses</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <input
            type="number"
            min={0}
            max={100}
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            placeholder="Min score"
            className="input sm:w-32"
          />
          <select value={sort} onChange={(e) => setSort(e.target.value)} className="input sm:w-44">
            <option value="score_desc">Highest score</option>
            <option value="score_asc">Lowest score</option>
            <option value="name_asc">Name A→Z</option>
            <option value="recent">Most recent</option>
          </select>
        </div>

        <div className="overflow-hidden rounded-[24px] border bg-white shadow-card" style={{ borderColor: BORDER }}>
          {loadState === 'loading' && (
            <div className="space-y-3 p-5">
              {[1, 2, 3, 4, 5].map((i) => <div key={i} className="h-16 skeleton" />)}
            </div>
          )}

          {loadState === 'error' && (
            <div className="py-16 text-center">
              <p className="text-sm" style={{ color: DANGER }}>Unable to load candidates.</p>
              <button type="button" onClick={() => setRefreshKey((v) => v + 1)} className="mt-4 text-sm font-semibold text-brand-600 hover:text-brand-700">
                Try Again
              </button>
            </div>
          )}

          {loadState === 'ready' && filtered.length === 0 && (
            <div className="py-16 text-center">
              <div className="mx-auto h-12 w-12 rounded-xl bg-brand-50 grid place-items-center text-2xl"><i className="fa-solid fa-users" /></div>
              <h3 className="mt-4 text-base font-semibold text-ink-900">
                {candidates.length === 0 ? 'No candidates yet' : 'No matching candidates'}
              </h3>
              <p className="mt-1 text-sm text-ink-500">
                {candidates.length === 0
                  ? 'Create a batch and upload resumes to see candidates here.'
                  : 'Try different filters.'}
              </p>
            </div>
          )}

          {loadState === 'ready' && filtered.length > 0 && (
            <div className="divide-y" style={{ borderColor: BORDER }}>
              <div className="hidden lg:grid grid-cols-[1.5fr_1.2fr_100px_120px_160px] gap-4 px-6 py-3 text-xs font-semibold uppercase tracking-wider" style={{ color: TEXT_MUTED, borderBottom: `1px solid ${BORDER}` }}>
                <span>Candidate</span>
                <span>Email</span>
                <span>Score</span>
                <span>Status</span>
                <span>Batch</span>
              </div>
              {filtered.map((c) => {
                const hasScore = typeof c.ats_score === 'number';
                const level = hasScore ? scoreLevel(c.ats_score as number) : 'weak';
                return (
                  <Link
                    key={c.id}
                    to={`/b2b/resumes/${c.id}`}
                    className="block px-6 py-4 hover:bg-brand-50/40 hover:border-l-2 hover:border-l-brand-500 transition-colors duration-150"
                  >
                    <div className="flex flex-col gap-3 lg:grid lg:grid-cols-[1.5fr_1.2fr_100px_120px_160px] lg:items-center lg:gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="h-9 w-9 shrink-0 rounded-xl bg-brand-50 grid place-items-center text-xs font-bold text-brand-700">CV</span>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-ink-900">{c.candidate_name || 'Unnamed candidate'}</p>
                          <p className="truncate text-xs" style={{ color: TEXT_MUTED }}>{c.file_name}</p>
                        </div>
                      </div>
                      <div className="text-xs truncate" style={{ color: TEXT_MUTED }}>{c.candidate_email || '—'}</div>
                      <div>
                        <p className="lg:hidden text-xs" style={{ color: TEXT_MUTED }}>Score</p>
                        <p className="text-lg font-bold tabular-nums" style={{ color: hasScore ? levelColor(level) : TEXT_MUTED }}>
                          {hasScore ? Math.round(c.ats_score as number) : '—'}
                        </p>
                      </div>
                      <div>
                        <span className={`badge ${c.status === 'completed' ? 'badge-success' : c.status === 'failed' ? 'badge-danger' : 'badge-info'}`}>
                          {c.status}
                        </span>
                      </div>
                      <div className="text-xs truncate" style={{ color: TEXT_MUTED }}>{c.batch_title}</div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {loadState === 'ready' && filtered.length > 0 && (
          <p className="text-xs text-center" style={{ color: TEXT_MUTED }}>
            Showing {filtered.length} of {candidates.length} candidates
          </p>
        )}
      </div>
    </B2BShell>
  );
}

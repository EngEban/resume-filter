import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { b2cApi, type AnalysisHistoryItem } from '@/lib/api';
import { BORDER, DANGER, TEXT_MUTED, levelColor, scoreLevel } from '@/theme';

type HistoryStatus = 'completed' | 'pending';
type LoadState = 'loading' | 'ready' | 'error';

function formatDate(value: string | null) {
  if (!value) return 'Date unavailable';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const target = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const days = Math.round((today.getTime() - target.getTime()) / 86400000);

  if (days === 0) return `Today, ${new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(date)}`;
  if (days === 1) return `Yesterday, ${new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(date)}`;
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
}

function getStatus(item: AnalysisHistoryItem): HistoryStatus {
  return typeof item.ats_score === 'number' ? 'completed' : 'pending';
}

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisHistoryItem[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | HistoryStatus>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoadState('loading');
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

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return analyses.filter((a) => {
      const matchSearch = !q || a.id.toLowerCase().includes(q);
      const matchStatus = statusFilter === 'all' || getStatus(a) === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [analyses, search, statusFilter]);

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">Your workspace</p>
          <h1 className="text-4xl font-bold tracking-tight text-ink-900">Analysis History</h1>
          <p className="text-ink-600">Review your previous resume analyses and results.</p>
        </div>
        <Link to="/analyze" className="btn btn-primary">Analyze New Resume</Link>
      </div>

      {/* Filters */}
      <section className="rounded-2xl border bg-white p-4 sm:p-5" style={{ borderColor: BORDER }}>
        <div className="flex flex-col gap-4 sm:flex-row">
          <div className="flex-1 space-y-1.5">
            <label htmlFor="history-search" className="label">Search analyses</label>
            <input
              id="history-search"
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input"
              placeholder="Search by analysis ID"
            />
          </div>
          <div className="sm:w-48 space-y-1.5">
            <label htmlFor="history-status" className="label">Status</label>
            <select
              id="history-status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as 'all' | HistoryStatus)}
              className="input"
            >
              <option value="all">All statuses</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </section>

      {/* List */}
      <section className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Activity</p>
            <h2 className="mt-1 text-2xl font-bold tracking-tight text-ink-900">All analyses</h2>
          </div>
          {loadState === 'ready' && (
            <span className="text-xs" style={{ color: TEXT_MUTED }}>{visible.length} shown</span>
          )}
        </div>

        <div className="overflow-hidden rounded-[24px] border bg-white shadow-card" style={{ borderColor: BORDER }}>
          {loadState === 'loading' && (
            <div className="space-y-3 p-5">
              {[1, 2, 3, 4].map((i) => <div key={i} className="h-[74px] skeleton" />)}
            </div>
          )}

          {loadState === 'error' && (
            <div className="py-14 text-center">
              <p className="text-sm" style={{ color: DANGER }}>Unable to load your history.</p>
              <button
                type="button"
                onClick={() => setRefreshKey((v) => v + 1)}
                className="mt-4 text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                Try again
              </button>
            </div>
          )}

          {loadState === 'ready' && analyses.length === 0 && (
            <div className="py-16 text-center">
              <div className="mx-auto h-12 w-12 rounded-xl bg-brand-50 grid place-items-center text-2xl">↺</div>
              <h3 className="mt-4 text-base font-semibold text-ink-900">No analyses yet</h3>
              <p className="mt-1 text-sm text-ink-500">Your resume analyses will appear here.</p>
              <Link to="/analyze" className="mt-4 inline-flex text-sm font-semibold text-brand-600 hover:text-brand-700">
                Analyze your first resume →
              </Link>
            </div>
          )}

          {loadState === 'ready' && analyses.length > 0 && visible.length === 0 && (
            <div className="py-14 text-center">
              <h3 className="text-base font-semibold text-ink-900">No matching analyses</h3>
              <p className="mt-1 text-sm text-ink-500">Try a different ID or status.</p>
              <button
                type="button"
                onClick={() => { setSearch(''); setStatusFilter('all'); }}
                className="mt-4 text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                Clear filters
              </button>
            </div>
          )}

          {loadState === 'ready' && visible.length > 0 && (
            <div className="divide-y" style={{ borderColor: BORDER }}>
              {visible.map((item) => {
                const status = getStatus(item);
                const isExpanded = expandedId === item.id;
                const level = typeof item.ats_score === 'number' ? scoreLevel(item.ats_score) : 'weak';
                const breakdown = item.breakdown ?? {};
                const entries = Object.entries(breakdown);

                return (
                  <div key={item.id} className="transition-colors hover:bg-brand-50/40">
                    <div className="flex flex-col gap-4 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
                      <div className="flex items-center gap-4 min-w-0">
                        <span className="h-10 w-10 shrink-0 rounded-xl bg-brand-50 grid place-items-center text-xs font-bold text-brand-700">CV</span>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-ink-900">Resume analysis</p>
                          <p className="mt-1 truncate text-xs" style={{ color: TEXT_MUTED }}>
                            ID · {item.id.slice(0, 12)} · {formatDate(item.created_at)}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-4 pl-14 sm:pl-0">
                        <span className={`badge ${status === 'completed' ? 'badge-success' : 'badge-info'}`}>
                          {status === 'completed' ? 'Completed' : 'Pending'}
                        </span>
                        <div className="min-w-[58px] text-right">
                          <p className="text-[10px] uppercase tracking-wider" style={{ color: TEXT_MUTED }}>Score</p>
                          <p className="mt-0.5 text-sm font-bold tabular-nums" style={{ color: typeof item.ats_score === 'number' ? levelColor(level) : TEXT_MUTED }}>
                            {typeof item.ats_score === 'number' ? `${Math.round(item.ats_score)}/100` : 'Pending'}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => setExpandedId(isExpanded ? null : item.id)}
                          className="text-xs font-semibold text-brand-600 hover:text-brand-700"
                          aria-expanded={isExpanded}
                        >
                          {isExpanded ? 'Hide details' : 'View details'}
                        </button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="border-t bg-ink-50 px-5 py-5 sm:px-6" style={{ borderColor: BORDER }}>
                        <div className="grid gap-5 sm:grid-cols-2">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Analysis details</p>
                            <p className="mt-2 text-sm text-ink-600 leading-6">
                              This analysis is available from your B2C history record.
                            </p>
                          </div>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between gap-4">
                              <span style={{ color: TEXT_MUTED }}>Missing keywords</span>
                              <span className="font-semibold text-ink-900">{item.missing_keywords?.length ?? 0}</span>
                            </div>
                            {entries.slice(0, 6).map(([key, value]) => (
                              <div key={key} className="flex justify-between gap-4">
                                <span className="capitalize" style={{ color: TEXT_MUTED }}>{key.replace(/_/g, ' ')}</span>
                                <span className="font-semibold text-ink-900 tabular-nums">
                                  {typeof value === 'number' ? Math.round(value) : '—'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

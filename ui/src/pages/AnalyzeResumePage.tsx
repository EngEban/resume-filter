import { useRef, useState, type ChangeEvent, type DragEvent, type FormEvent, type KeyboardEvent } from 'react';
import { Link } from 'react-router-dom';
import { b2cApi, APIError, type AnalysisResponse } from '@/lib/api';
import { DANGER, SUCCESS, TEXT_MUTED, levelColor } from '@/theme';

const MAX_MB = 10;
const MAX_BYTES = MAX_MB * 1024 * 1024;

type Status = 'idle' | 'analyzing' | 'success' | 'error';

function ext(name: string) {
  const i = name.lastIndexOf('.');
  return i >= 0 ? name.slice(i).toLowerCase() : '';
}

const TIPS = [
  { iconClass: 'fa-solid fa-bullseye', title: 'Use a real job posting', text: 'Paste the actual job description — the more specific, the better.' },
  { iconClass: 'fa-solid fa-file-lines', title: 'Upload a text-based PDF', text: 'Scanned images may not extract well. Use text-based PDFs.' },
  { iconClass: 'fa-solid fa-chart-pie', title: 'Review your ATS score', text: 'Focus on both matched keywords and missing ones.' },
  { iconClass: 'fa-solid fa-lightbulb', title: 'Act on suggestions', text: 'Apply the top 3 suggestions to boost your score fast.' },
];

export default function AnalyzeResumePage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [drag, setDrag] = useState(false);

  const analyzing = status === 'analyzing';

  function validate(f: File): string {
    if (!['.pdf', '.docx'].includes(ext(f.name))) return 'Please upload a PDF or DOCX file.';
    if (f.size > MAX_BYTES) return `File must be under ${MAX_MB} MB.`;
    if (f.size === 0) return 'File is empty.';
    return '';
  }

  function pick(f: File) {
    const err = validate(f);
    if (err) { setStatus('error'); setMessage(err); return; }
    setFile(f); setResult(null); setStatus('idle'); setMessage('');
  }

  function onFile(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) pick(f);
    e.target.value = '';
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault(); setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) pick(f);
  }

  function onKey(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inputRef.current?.click(); }
  }

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setMessage('');
    if (!file) { setStatus('error'); setMessage('Choose a resume.'); return; }
    if (jobDescription.trim().length < 20) { setStatus('error'); setMessage('Job description must be at least 20 characters.'); return; }

    setStatus('analyzing');
    try {
      const data = await b2cApi.analyze(file, jobDescription.trim());
      setResult(data); setStatus('success'); setMessage('Analysis ready.');
    } catch (err) {
      setStatus('error');
      setMessage(err instanceof APIError ? err.message : 'Analysis failed.');
    }
  }

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">B2C Workspace</p>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900">Analyze Resume</h1>
        <p className="text-ink-600">Upload a resume and get an AI-powered analysis in seconds.</p>
      </div>

      {/* Two-column layout */}
      <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        {/* Left: Form */}
        <form onSubmit={submit} className="space-y-6" noValidate>
          {/* Upload card */}
          <section className="rounded-2xl border border-ink-100 bg-white/80 p-6 shadow-soft-md backdrop-blur-sm lg:p-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Step 1</p>
                <h2 className="mt-2 font-display text-xl font-bold text-ink-900">Upload your resume</h2>
              </div>
              <span className="badge badge-info">PDF / DOCX</span>
            </div>

            <input ref={inputRef} type="file" accept=".pdf,.docx" className="hidden" onChange={onFile} />

            {!file ? (
              <div
                onClick={() => inputRef.current?.click()}
                onKeyDown={onKey}
                onDragEnter={(e) => { e.preventDefault(); setDrag(true); }}
                onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
                onDragLeave={(e) => { if (e.currentTarget === e.target) setDrag(false); }}
                onDrop={onDrop}
                role="button"
                tabIndex={0}
                className={`mt-6 flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-200 ${drag ? 'scale-[1.02] border-brand-500 bg-brand-50 shadow-soft-lg' : 'border-ink-200 bg-ink-50/50'}`}
              >
                <div
                  className={`mb-4 grid h-14 w-14 place-items-center rounded-2xl text-2xl text-brand-600 transition-all animate-pulse-soft ${drag ? 'bg-brand-100' : 'bg-brand-50'}`}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <p className="text-base font-semibold text-ink-900">Drag & drop your resume here</p>
                <p className="mt-1 text-sm text-ink-500">
                  or <span className="font-medium text-brand-600">browse files</span>
                </p>
                <p className="mt-4 text-xs" style={{ color: TEXT_MUTED }}>
                  PDF or DOCX · Max {MAX_MB} MB
                </p>
              </div>
            ) : (
              <div className="mt-6 rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-white p-5 shadow-soft-sm animate-fade-in">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="h-12 w-12 rounded-xl bg-emerald-100 grid place-items-center text-sm font-bold text-emerald-700">
                      {ext(file.name).replace('.', '').toUpperCase()}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink-900">{file.name}</p>
                      <p className="text-xs" style={{ color: TEXT_MUTED }}>
                        {(file.size / (1024 * 1024)).toFixed(2)} MB · Ready
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setFile(null); setResult(null); setStatus('idle'); }}
                    className="text-sm font-medium text-ink-500 hover:text-red-600 transition"
                  >
                    Remove
                  </button>
                </div>
              </div>
            )}
          </section>

          {/* Job description card */}
          <section className="rounded-2xl border border-ink-100 bg-white/80 p-6 shadow-soft-md backdrop-blur-sm lg:p-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-600">Step 2</p>
              <h2 className="mt-2 font-display text-xl font-bold text-ink-900">Job Description</h2>
            </div>

            <div className="mt-5 space-y-2">
              <textarea
                value={jobDescription}
                onChange={(e) => { setJobDescription(e.target.value); if (status === 'error') setMessage(''); }}
                className="input min-h-[180px] resize-y"
                placeholder="Paste the full job description here. Include requirements, responsibilities, and qualifications."
              />
              <div className="flex items-center justify-between text-xs">
                <span style={{ color: TEXT_MUTED }}>At least 20 characters</span>
                <span
                  style={{
                    color: jobDescription.length >= 20 ? SUCCESS : TEXT_MUTED,
                    fontWeight: 500,
                  }}
                >
                  {jobDescription.length} chars
                </span>
              </div>
            </div>
          </section>

          {/* Action bar */}
          <div className="flex flex-col gap-3 rounded-2xl border border-ink-100 bg-white/80 p-5 shadow-soft-md backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm" style={{ color: status === 'error' ? DANGER : status === 'success' ? SUCCESS : TEXT_MUTED }}>
              {message || (file && jobDescription.trim().length >= 20 ? <><i className="fa-solid fa-circle-check" />{' '}Ready to analyze.</> : 'Add a resume and a job description.')}
            </p>
            <button
              type="submit"
              disabled={analyzing || !file || jobDescription.trim().length < 20}
              className="btn btn-primary btn-lg hover-lift glow-pulse"
            >
              {analyzing ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                  Analyzing…
                </>
              ) : (
                <>
                  Analyze Resume
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Right: Tips + Result */}
        <div className="space-y-6">
          {/* Tips card */}
          <div className="rounded-2xl border border-brand-100 bg-gradient-to-br from-brand-50 to-white p-6 shadow-soft-md">
            <div className="flex items-center gap-2">
              <span className="text-xl"><i className="fa-solid fa-lightbulb" /></span>
              <h3 className="font-display text-base font-bold text-ink-900">Tips for better results</h3>
            </div>
            <ul className="mt-5 space-y-4 stagger">
              {TIPS.map((tip) => (
                <li key={tip.title} className="flex gap-3 items-start">
                  <span className="text-lg shrink-0"><i className={tip.iconClass} /></span>
                  <div>
                    <p className="text-sm font-semibold text-ink-900">{tip.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: TEXT_MUTED }}>{tip.text}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Loading state */}
          {analyzing && (
            <div className="rounded-2xl border border-brand-100 bg-white p-6 shadow-soft-md animate-fade-in">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-brand-50 grid place-items-center">
                  <span className="h-5 w-5 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-ink-900">Analyzing…</p>
                  <p className="text-xs" style={{ color: TEXT_MUTED }}>AI is reviewing your resume.</p>
                </div>
              </div>
              <div className="mt-5 space-y-2">
                <div className="h-2 rounded-full skeleton" />
                <div className="h-2 rounded-full skeleton w-3/4" />
                <div className="h-2 rounded-full skeleton w-1/2" />
              </div>
            </div>
          )}

          {/* Result */}
          {status === 'success' && result && (
            <div className="signal-ring rounded-2xl border border-emerald-200 bg-white p-6 shadow-soft-md animate-fade-in-up">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Result ready</p>
                  <h3 className="mt-1 font-display text-lg font-bold text-ink-900">ATS Score</h3>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold tabular-nums" style={{ color: levelColor(result.level) }}>
                    {Math.round(result.ats_score)}
                  </p>
                  <p className="text-xs font-medium" style={{ color: levelColor(result.level) }}>
                    {result.level_label}
                  </p>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-ink-50 p-3">
                  <p className="text-xs" style={{ color: TEXT_MUTED }}>Matched</p>
                  <p className="text-lg font-bold text-emerald-600">{result.matched_keywords.length}</p>
                </div>
                <div className="rounded-xl bg-ink-50 p-3">
                  <p className="text-xs" style={{ color: TEXT_MUTED }}>Missing</p>
                  <p className="text-lg font-bold text-red-500">{result.missing_keywords.length}</p>
                </div>
                <div className="rounded-xl bg-ink-50 p-3">
                  <p className="text-xs" style={{ color: TEXT_MUTED }}>Tips</p>
                  <p className="text-lg font-bold text-brand-600">{result.suggestions.length}</p>
                </div>
              </div>

              <div className="mt-4 border-t border-ink-100 pt-4">
                <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: TEXT_MUTED }}>
                  Score breakdown
                </p>
                <div className="space-y-2">
                  {Object.entries(result.breakdown).slice(0, 6).map(([key, value]) => {
                    const pct = Math.max(0, Math.min(100, Number(value)));
                    return (
                      <div key={key}>
                        <div className="flex justify-between text-xs">
                          <span className="capitalize text-ink-700">{key.replace(/_/g, ' ')}</span>
                          <span className="font-semibold tabular-nums text-ink-900">{Math.round(pct)}</span>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-ink-100 overflow-hidden">
                          <div
                            className="h-full rounded-full gradient-primary transition-all duration-700"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <Link to="/history" className="btn btn-secondary btn-sm hover-lift">
                  View history
                </Link>
                <Link to="/dashboard" className="btn btn-ghost btn-sm">
                  Dashboard
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// src/components/DeveloperCard.tsx
// Hoverable developer business card.
// ============================================================
import { useState } from 'react';
import { BORDER } from '@/theme';

export function DeveloperCard() {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      {/* Trigger */}
      <button
        type="button"
        className="flex items-center gap-2.5 rounded-xl border bg-white px-3 py-2 transition-all hover:border-brand-300 hover:bg-brand-50/30"
        style={{ borderColor: BORDER }}
        aria-expanded={open}
      >
        <span className="h-8 w-8 shrink-0 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 grid place-items-center text-xs font-bold text-white">
          EB
        </span>
        <div className="text-left">
          <p className="text-xs font-semibold text-ink-900 leading-tight">Eban</p>
          <p className="text-[10px] text-ink-500 leading-tight">Full-Stack Engineer</p>
        </div>
      </button>

      {/* Hover card */}
      <div
        className={`absolute bottom-full left-0 mb-3 w-72 rounded-2xl border bg-white p-5 shadow-2xl transition-all duration-200 ${
          open
            ? 'pointer-events-auto translate-y-0 opacity-100'
            : 'pointer-events-none translate-y-1 opacity-0'
        }`}
        style={{ borderColor: BORDER }}
        role="dialog"
      >
        <div className="flex items-start gap-3">
          <span className="h-12 w-12 shrink-0 rounded-full bg-gradient-to-br from-brand-500 to-brand-700 grid place-items-center text-base font-bold text-white">
            EB
          </span>
          <div className="min-w-0">
            <p className="text-sm font-bold text-ink-900">Eng. Eban</p>
            <p className="text-xs text-brand-600">Software Engineer</p>
          </div>
        </div>

        <p className="mt-3 text-xs text-ink-600 leading-relaxed">
          Built TalentScope end-to-end: FastAPI, PostgreSQL with RLS, Celery,
          LiteLLM, and a React + TypeScript frontend.
        </p>

        <div className="mt-4 flex flex-wrap gap-1.5">
          {['Python', 'FastAPI', 'React', 'TypeScript', 'PostgreSQL', 'Docker'].map((tag) => (
            <span
              key={tag}
              className="rounded-md px-1.5 py-0.5 text-[10px] font-medium"
              style={{ background: '#EEF2FF', color: '#4F46E5' }}
            >
              {tag}
            </span>
          ))}
        </div>

        <div className="mt-4 pt-3 border-t flex items-center gap-2" style={{ borderColor: BORDER }}>
          <a
            href="https://github.com/EngEban"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border bg-white py-1.5 text-xs font-semibold text-ink-700 hover:border-brand-300 hover:text-brand-600 transition"
            style={{ borderColor: BORDER }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.34-5.47-5.96 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 3-.4c1.02 0 2.04.14 3 .4 2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.63-2.8 5.65-5.48 5.95.43.37.82 1.1.82 2.22v3.29c0 .32.22.7.83.58A12 12 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub
          </a>
          <a
            href="https://github.com/EngEban/resume-filter"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border bg-white py-1.5 text-xs font-semibold text-ink-700 hover:border-brand-300 hover:text-brand-600 transition"
            style={{ borderColor: BORDER }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
            Project
          </a>
        </div>
      </div>
    </div>
  );
}
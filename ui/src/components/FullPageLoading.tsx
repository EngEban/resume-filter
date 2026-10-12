// ============================================================
// src/components/FullPageLoading.tsx
// ============================================================
export function FullPageLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-950">
      <div className="flex flex-col items-center gap-4 text-white">
        <div className="signal-ring grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-brand-400 to-brand-700 shadow-brand">
          <span className="h-5 w-5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
        </div>
        <p className="text-sm font-medium text-slate-300">Bringing your workspace into focus…</p>
      </div>
    </div>
  );
}

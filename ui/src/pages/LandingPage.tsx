import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function LandingPage() {
  const { isAuthenticated, user } = useAuth();
  const dashboardPath = user?.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';

  return (
    <div className="overflow-hidden">
      {/* ==================== HERO ==================== */}
      <section className="relative overflow-hidden bg-[radial-gradient(circle_at_75%_12%,rgba(129,140,248,0.18),transparent_28rem)]">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-b from-brand-50/70 via-ink-50/70 to-ink-50" />
        <div aria-hidden className="absolute inset-x-0 top-0 h-[520px] opacity-40 [background-image:linear-gradient(rgba(79,70,229,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(79,70,229,0.06)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:linear-gradient(to_bottom,black,transparent)]" />
        <div aria-hidden className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-brand-200/40 blur-3xl animate-pulse-soft" />
        <div aria-hidden className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-accent-200/30 blur-3xl" />

        <div className="relative mx-auto max-w-7xl px-5 pb-24 pt-16 sm:px-6 lg:px-8 lg:pb-32 lg:pt-28">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left */}
            <div className="space-y-8 animate-fade-in-up">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 border border-brand-200">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-500 animate-pulse-soft" />
                <span className="text-xs font-semibold text-brand-700">
                  AI-Powered Resume Intelligence
                </span>
              </div>

              <h1 className="max-w-2xl text-5xl font-bold leading-[1.02] tracking-[-0.045em] text-ink-950 sm:text-6xl lg:text-7xl">
                Find the signal in
                <br />
                <span className="bg-gradient-to-r from-brand-600 to-accent-500 bg-clip-text text-transparent">
                  every resume.
                </span>
              </h1>

              <p className="text-lg text-ink-600 leading-relaxed max-w-xl">
                Analyze your resume against any job description, identify
                keyword gaps, and get practical suggestions. For individuals
                and organizations.
              </p>

              <div className="flex flex-wrap items-center gap-3">
                {isAuthenticated ? (
                  <>
                    <Link to={dashboardPath} className="btn btn-primary btn-lg hover-lift glow-pulse">
                      Go to Dashboard
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                    </Link>
                    <Link to={user?.account_type === 'b2b' ? '/b2b/batches' : '/analyze'} className="btn btn-secondary btn-lg">
                      {user?.account_type === 'b2b' ? 'New Batch' : 'Analyze Resume'}
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/register?type=b2c" className="btn btn-primary btn-lg hover-lift glow-pulse">
                      Analyze My Resume
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                    </Link>
                    <Link to="/register?type=b2b" className="btn btn-secondary btn-lg">
                      For Organizations
                    </Link>
                  </>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-x-6 gap-y-3 pt-4 text-sm text-ink-500">
                <div className="flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  <span>No credit card</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  <span>Free to try</span>
                </div>
              </div>
            </div>

            {/* Right */}
            <div className="relative animate-fade-in-up">
              <ProductPreview />
            </div>
          </div>
        </div>
      </section>

      {/* ==================== FEATURES ==================== */}
      <section id="features" className="border-y border-ink-100 bg-white/80 py-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-600">Features</p>
            <h2 className="text-4xl font-bold tracking-tight text-ink-900">Everything you need to stand out.</h2>
            <p className="text-lg text-ink-600">From transparent ATS scoring to detailed keyword analysis.</p>
          </div>

          <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-4 gap-6 stagger">
            <FeatureCard icon={<IconTarget />} title="ATS Score" description="Transparent 6-factor scoring engine." accent="brand" />
            <FeatureCard icon={<IconSearch />} title="Keyword Gaps" description="See exactly which keywords are missing." accent="accent" />
            <FeatureCard icon={<IconSparkle />} title="Smart Suggestions" description="Prioritized, actionable recommendations." accent="emerald" />
            <FeatureCard icon={<IconBuilding />} title="Batch Processing" description="Screen hundreds of resumes in minutes." accent="violet" />
          </div>
        </div>
      </section>

      {/* ==================== HOW ==================== */}
      <section id="how" className="py-24 bg-ink-50">
        <div className="max-w-5xl mx-auto px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-600">How it works</p>
            <h2 className="text-4xl font-bold tracking-tight text-ink-900">Three simple steps.</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Step number={1} title="Upload your resume" description="PDF or DOCX. Takes seconds." accent="brand" />
            <Step number={2} title="Paste the job description" description="Any format, any length." accent="accent" />
            <Step number={3} title="Review your analysis" description="Score, keywords, suggestions." accent="emerald" />
          </div>
        </div>
      </section>

      {/* ==================== CTA ==================== */}
      <section className="py-24 bg-white">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-4xl font-bold tracking-tight text-ink-900">
            {isAuthenticated ? 'Ready for your next analysis?' : 'Ready to improve your resume?'}
          </h2>
          <p className="text-lg text-ink-600">
            {isAuthenticated
              ? 'Jump back into your workspace and continue where you left off.'
              : 'Start your first analysis in under a minute. No credit card required.'}
          </p>
          <div className="pt-4">
            <Link
              to={isAuthenticated ? dashboardPath : '/register?type=b2c'}
              className="btn btn-primary btn-lg hover-lift glow-pulse"
            >
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started Free'}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

// ============================================================
function ProductPreview() {
  return (
    <div className="card signal-ring relative overflow-hidden rounded-[28px] border-white/80 bg-white/90 p-0 shadow-elevated backdrop-blur hover-lift animate-float-slow">
      <div className="flex items-center gap-2 px-4 py-3 bg-ink-50 border-b border-ink-200">
        <span className="h-3 w-3 rounded-full bg-red-400" />
        <span className="h-3 w-3 rounded-full bg-amber-400" />
        <span className="h-3 w-3 rounded-full bg-emerald-400" />
        <span className="ml-3 text-xs font-medium text-ink-500">Analysis result</span>
      </div>

      <div className="space-y-5 p-6 sm:p-7">
        <div className="flex items-center gap-5">
          <div className="signal-ring relative h-20 w-20 shrink-0">
            <svg viewBox="0 0 100 100" className="h-20 w-20 -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#E2E8F0" strokeWidth="8" />
              <circle cx="50" cy="50" r="42" fill="none" stroke="#10B981" strokeWidth="8" strokeDasharray="264" strokeDashoffset="42" strokeLinecap="round" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xl font-bold text-emerald-600">84</span>
            </div>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-ink-500">Signal score</p>
            <p className="text-lg font-semibold text-emerald-600">Good match</p>
            <p className="mt-1 text-xs text-ink-500">4 strong signals found</p>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-xs font-semibold text-ink-700 mb-1.5">Matched</p>
            <div className="flex flex-wrap gap-1.5">
              {['Python', 'FastAPI', 'PostgreSQL', 'Docker'].map((kw) => (
                <span key={kw} className="badge badge-success">{kw}</span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold text-ink-700 mb-1.5">Missing</p>
            <div className="flex flex-wrap gap-1.5">
              {['Kubernetes', 'Redis'].map((kw) => (
                <span key={kw} className="badge badge-danger">{kw}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-brand-50 p-3 flex items-start gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0">
            <path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
          </svg>
          <p className="text-xs text-brand-900 leading-relaxed">
            Add <strong>Kubernetes</strong> to your skills if you have experience.
          </p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description, accent }: { icon: React.ReactNode; title: string; description: string; accent: 'brand' | 'accent' | 'emerald' | 'violet' }) {
  const accentMap = {
    brand: 'bg-brand-50 text-brand-600',
    accent: 'bg-accent-50 text-accent-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    violet: 'bg-violet-50 text-violet-600',
  };
  return (
    <div className="card card-interactive hover-lift">
      <div className={`h-11 w-11 rounded-xl grid place-items-center ${accentMap[accent]}`}>{icon}</div>
      <h3 className="mt-4 text-base font-semibold text-ink-900">{title}</h3>
      <p className="mt-2 text-sm text-ink-600 leading-relaxed">{description}</p>
    </div>
  );
}

function Step({ number, title, description, accent }: { number: number; title: string; description: string; accent: 'brand' | 'accent' | 'emerald' }) {
  const accentMap = { brand: 'bg-brand-600', accent: 'bg-accent-500', emerald: 'bg-emerald-500' };
  return (
    <div className="text-center space-y-3">
      <div className={`mx-auto h-12 w-12 rounded-full ${accentMap[accent]} grid place-items-center text-white text-xl font-bold shadow-md hover-scale hover-glow`}>
        {number}
      </div>
      <h3 className="text-base font-semibold text-ink-900">{title}</h3>
      <p className="text-sm text-ink-600">{description}</p>
    </div>
  );
}

function IconTarget() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
    </svg>
  );
}
function IconSparkle() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4" />
    </svg>
  );
}
function IconBuilding() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="2" width="16" height="20" rx="2" />
      <path d="M9 22v-4h6v4M9 6h.01M15 6h.01M9 10h.01M15 10h.01M9 14h.01M15 14h.01" />
    </svg>
  );
}

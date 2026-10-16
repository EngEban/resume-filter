import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function LandingPage() {
  const { isAuthenticated, user } = useAuth();
  const dashboardPath = user?.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';

  return (
    <div className="overflow-hidden">
      {/* ==================== HERO ==================== */}
      <section className="relative overflow-hidden bg-gradient-to-b from-brand-50/40 via-white to-white">
        {/* Background decoration */}
        <div aria-hidden className="absolute inset-0 bg-[radial-gradient(circle_at_75%_15%,rgba(168,85,247,0.15),transparent_35rem)]" />
        <div aria-hidden className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-brand-300/20 blur-3xl animate-glow-pulse" />
        <div aria-hidden className="absolute -bottom-40 -left-40 h-[400px] w-[400px] rounded-full bg-pink-300/20 blur-3xl" />

        <div className="relative mx-auto max-w-7xl px-5 pb-20 pt-16 sm:px-6 lg:px-8 lg:pb-28 lg:pt-24">
          <div className="grid items-center gap-16 lg:grid-cols-2">
            {/* Left - Text */}
            <div className="space-y-8 animate-fade-in-up">
              <div className="pill-badge">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-600 animate-glow-pulse" />
                <span className="text-brand-700">AI-Powered Resume Intelligence</span>
              </div>

              <h1 className="max-w-2xl font-display text-5xl font-bold leading-[1.02] tracking-[-0.045em] text-ink-950 sm:text-6xl lg:text-7xl">
                The future of
                <br />
                <span className="gradient-text">hiring</span>{' '}
                <span className="text-ink-950">reimagined.</span>
              </h1>

              <p className="max-w-xl text-lg leading-relaxed text-ink-600">
                Analyze resumes against any job description, identify keyword gaps,
                and get practical suggestions — for individuals and organizations.
              </p>

              <div className="flex flex-wrap items-center gap-3">
                {isAuthenticated ? (
                  <>
                    <Link to={dashboardPath} className="btn btn-primary btn-lg hover-lift">
                      Go to Dashboard
                      <i className="fa-solid fa-arrow-right text-xs" />
                    </Link>
                    <Link
                      to={user?.account_type === 'b2b' ? '/b2b/batches' : '/analyze'}
                      className="btn btn-secondary btn-lg"
                    >
                      {user?.account_type === 'b2b' ? 'New Batch' : 'Analyze Resume'}
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/register?type=b2c" className="btn btn-primary btn-lg hover-lift">
                      Analyze My Resume
                      <i className="fa-solid fa-arrow-right text-xs" />
                    </Link>
                    <Link to="/register?type=b2b" className="btn btn-secondary btn-lg">
                      <i className="fa-solid fa-play text-xs" />
                      For Organizations
                    </Link>
                  </>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-x-6 gap-y-3 pt-2 text-sm text-ink-500">
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-check text-emerald-500" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-check text-emerald-500" />
                  <span>Free for individuals</span>
                </div>
              </div>
            </div>

            {/* Right - 3D Shapes */}
            <div className="relative h-[500px] lg:h-[560px]">
              {/* Main shape */}
              <img
                src="/images/hero/01_hero_shape_main_1200x1200.png"
                alt=""
                className="absolute left-1/2 top-1/2 w-full max-w-[480px] -translate-x-1/2 -translate-y-1/2 animate-float"
                style={{ animationDuration: '8s' }}
              />
              {/* Secondary shape */}
              <img
                src="/images/hero/02_hero_shape_secondary_800x800.png"
                alt=""
                className="absolute -right-4 top-0 w-40 animate-float sm:w-52"
                style={{ animationDuration: '7s', animationDelay: '1.2s' }}
              />
              {/* Detail shape */}
              <img
                src="/images/hero/03_hero_shape_detail_400x400.png"
                alt=""
                className="absolute -bottom-4 -left-4 w-28 animate-float sm:w-36"
                style={{ animationDuration: '6s', animationDelay: '2.5s' }}
              />

              {/* Floating info card */}
              <div className="glass-card absolute -left-6 top-1/3 hidden rounded-2xl px-4 py-3 shadow-soft-lg sm:block">
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-check text-emerald-500" />
                  <span className="text-xs font-semibold text-ink-900">ATS Ready</span>
                </div>
              </div>

              {/* Floating stat */}
              <div className="glass-card absolute -right-4 bottom-1/4 hidden rounded-2xl px-4 py-3 shadow-soft-lg sm:block">
                <p className="text-xs text-ink-500">Match score</p>
                <p className="font-display text-xl font-bold text-brand-600">92%</p>
              </div>
            </div>
          </div>
        </div>

        {/* ==================== STATS BAR ==================== */}
        <div className="relative mx-auto max-w-7xl px-5 pb-16 sm:px-6 lg:px-8">
          <div className="grid gap-4 rounded-3xl border border-ink-100 bg-white/90 p-6 shadow-soft-lg backdrop-blur sm:grid-cols-2 lg:grid-cols-4 sm:p-8">
            <Stat icon="fa-solid fa-file-lines" value="10K+" label="Resumes analyzed" />
            <Stat icon="fa-solid fa-bullseye" value="95%" label="Accuracy rate" />
            <Stat icon="fa-solid fa-bolt" value="3s" label="Avg analysis time" />
            <Stat icon="fa-solid fa-layer-group" value="500" label="Max batch size" />
          </div>
        </div>
      </section>

      {/* ==================== FEATURES ==================== */}
      <section id="features" className="relative border-y border-ink-100 bg-white py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl space-y-4 text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-600">
              Features
            </p>
            <h2 className="font-display text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl">
              Everything you need to{' '}
              <span className="gradient-text">stand out.</span>
            </h2>
            <p className="text-lg text-ink-600">
              From transparent ATS scoring to detailed keyword analysis.
            </p>
          </div>

          <div className="mt-16 grid items-center gap-12 lg:grid-cols-2">
            {/* Illustration */}
            <div className="relative order-2 lg:order-1">
              <div aria-hidden className="absolute inset-0 rounded-full bg-gradient-to-tr from-brand-200/40 via-pink-200/30 to-orange-200/30 blur-3xl" />
              <img
                src="/images/hero/04_feature_card_illustration_600x600.png"
                alt="Feature illustration"
                className="relative mx-auto w-full max-w-md animate-float"
                style={{ animationDuration: '9s' }}
              />
            </div>

            {/* Feature list */}
            <div className="order-1 space-y-6 lg:order-2">
              <FeatureRow
                icon="fa-solid fa-bullseye"
                title="Transparent ATS Score"
                description="Six weighted factors you can see and understand. No black box."
                accent="brand"
              />
              <FeatureRow
                icon="fa-solid fa-magnifying-glass"
                title="Keyword Gap Analysis"
                description="See exactly which keywords from the job posting are missing."
                accent="pink"
              />
              <FeatureRow
                icon="fa-solid fa-wand-magic-sparkles"
                title="Smart Suggestions"
                description="Prioritized, actionable recommendations for high-impact improvements."
                accent="orange"
              />
              <FeatureRow
                icon="fa-solid fa-layer-group"
                title="Batch Processing"
                description="Screen hundreds of resumes in parallel with ranked shortlists."
                accent="brand"
              />
            </div>
          </div>
        </div>
      </section>

      {/* ==================== HOW IT WORKS ==================== */}
      <section id="how" className="bg-ink-50 py-24">
        <div className="mx-auto max-w-5xl px-6 lg:px-8">
          <div className="mb-16 space-y-4 text-center">
            <p className="text-xs font-semibold uppercase tracking-widest text-brand-600">
              How it works
            </p>
            <h2 className="font-display text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl">
              Three simple steps.
            </h2>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <Step
              number={1}
              icon="fa-solid fa-cloud-arrow-up"
              title="Upload your resume"
              description="PDF or DOCX. Processed in-memory, never stored."
            />
            <Step
              number={2}
              icon="fa-solid fa-file-lines"
              title="Paste the job description"
              description="Any format, any length. Parsed automatically."
            />
            <Step
              number={3}
              icon="fa-solid fa-chart-line"
              title="Review your analysis"
              description="Score, keywords, and prioritized suggestions."
            />
          </div>
        </div>
      </section>

      {/* ==================== CTA ==================== */}
      <section className="relative overflow-hidden bg-white py-24">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-[32px] p-12 text-white shadow-soft-xl sm:p-16">
            <div
              aria-hidden
              className="absolute inset-0 gradient-hero animate-gradient-shift"
              style={{ backgroundSize: '200% 200%' }}
            />
            <div
              aria-hidden
              className="absolute inset-0 opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.15)_1px,transparent_1px)] [background-size:32px_32px]"
            />

            {/* CTA shape */}
            <img
              src="/images/hero/05_cta_section_shape_800x800.png"
              alt=""
              className="pointer-events-none absolute -right-16 -top-16 w-72 opacity-80 animate-float lg:w-96"
              style={{ animationDuration: '10s' }}
            />

            <div className="relative max-w-2xl space-y-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/80">
                Ready to get started?
              </p>
              <h2 className="font-display text-4xl font-bold leading-tight sm:text-5xl">
                Let's build something{' '}
                <span className="italic">extraordinary</span> together.
              </h2>
              <p className="text-lg text-white/85">
                {isAuthenticated
                  ? 'Jump back into your workspace and continue where you left off.'
                  : 'Start your first analysis in under a minute. No credit card required.'}
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <Link
                  to={isAuthenticated ? dashboardPath : '/register?type=b2c'}
                  className="inline-flex h-12 items-center gap-2 rounded-full bg-white px-7 text-sm font-semibold text-brand-700 shadow-lg transition hover:-translate-y-0.5 hover:bg-white/95"
                >
                  {isAuthenticated ? 'Go to Dashboard' : 'Get Started — It\'s Free'}
                  <i className="fa-solid fa-arrow-right text-xs" />
                </Link>
                <Link
                  to="/register?type=b2b"
                  className="inline-flex h-12 items-center gap-2 rounded-full border border-white/40 px-7 text-sm font-semibold text-white transition hover:bg-white/10"
                >
                  <i className="fa-solid fa-building text-xs" />
                  For Organizations
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

function Stat({ icon, value, label }: { icon: string; value: string; label: string }) {
  return (
    <div className="flex items-center gap-4">
      <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-brand-100 to-pink-100 text-brand-700">
        <i className={`${icon} text-lg`} />
      </div>
      <div>
        <p className="font-display text-2xl font-bold tracking-tight text-ink-900">
          {value}
        </p>
        <p className="text-xs text-ink-500">{label}</p>
      </div>
    </div>
  );
}

function FeatureRow({
  icon,
  title,
  description,
  accent,
}: {
  icon: string;
  title: string;
  description: string;
  accent: 'brand' | 'pink' | 'orange';
}) {
  const accents = {
    brand: 'bg-brand-100 text-brand-700',
    pink: 'bg-pink-100 text-pink-700',
    orange: 'bg-orange-100 text-orange-700',
  } as const;

  return (
    <div className="flex gap-4 rounded-2xl border border-transparent p-4 transition-all hover:border-ink-100 hover:bg-ink-50/50">
      <div className={`grid h-12 w-12 shrink-0 place-items-center rounded-2xl ${accents[accent]}`}>
        <i className={`${icon} text-lg`} />
      </div>
      <div>
        <h3 className="font-display text-base font-semibold text-ink-900">{title}</h3>
        <p className="mt-1 text-sm leading-relaxed text-ink-600">{description}</p>
      </div>
    </div>
  );
}

function Step({
  number,
  icon,
  title,
  description,
}: {
  number: number;
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="group relative rounded-2xl border border-ink-100 bg-white p-6 text-center transition-all hover:-translate-y-1 hover:shadow-soft-lg">
      <div className="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl gradient-primary text-white shadow-soft-md">
        <i className={`${icon} text-lg`} />
      </div>
      <p className="font-display text-xs font-bold uppercase tracking-widest text-brand-600">
        Step {number}
      </p>
      <h3 className="mt-2 font-display text-lg font-semibold text-ink-900">{title}</h3>
      <p className="mt-2 text-sm text-ink-600">{description}</p>
    </div>
  );
}
import { Link } from 'react-router-dom';
import { Logo } from '@/components/Logo';

const SOCIALS = [
  {
    label: 'GitHub',
    href: 'https://github.com/EngEban',
    icon: 'fa-brands fa-github',
    color: 'bg-[#181717] hover:bg-[#333]',
  },
  {
    label: 'LinkedIn',
    href: 'https://www.linkedin.com/in/eban-tbail/',
    icon: 'fa-brands fa-linkedin-in',
    color: 'bg-[#0A66C2] hover:bg-[#0856A8]',
  },
  {
    label: 'Instagram',
    href: 'https://www.instagram.com/smartdev1.ai/',
    icon: 'fa-brands fa-instagram',
    color: 'bg-gradient-to-tr from-[#F58529] via-[#DD2A7B] to-[#8134AF] hover:opacity-90',
  },
  {
    label: 'WhatsApp',
    href: 'https://wa.me/970592630530',
    icon: 'fa-brands fa-whatsapp',
    color: 'bg-[#25D366] hover:bg-[#1EBE5A]',
  },
  {
    label: 'Email',
    href: 'mailto:ebantbaeil2004@gmail.com',
    icon: 'fa-solid fa-envelope',
    color: 'bg-brand-600 hover:bg-brand-700',
  },
];

export default function AboutPage() {
  return (
    <div className="bg-gradient-to-b from-brand-50/30 via-white to-white">
      {/* ==================== HERO ==================== */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-brand-300/20 blur-3xl animate-glow-pulse"
        />
        <div
          aria-hidden
          className="absolute -bottom-40 -left-40 h-[400px] w-[400px] rounded-full bg-pink-300/20 blur-3xl"
        />

        <div className="relative mx-auto max-w-4xl px-6 pt-20 pb-16 text-center lg:px-8 lg:pt-28">
          <div className="pill-badge mx-auto">
            <i className="fa-solid fa-code text-brand-600" />
            <span className="text-brand-700">The developer</span>
          </div>

          <h1 className="mt-6 font-display text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl lg:text-6xl">
            Meet <span className="gradient-text">Eban Tbail</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-600">
            Full-stack engineer and the mind behind Talentscope.
            Passionate about building tools that solve real problems with clean
            design and thoughtful engineering.
          </p>

          {/* Avatar */}
          <div className="mt-10 flex justify-center">
            <div className="relative">
              <div
                aria-hidden
                className="absolute inset-0 rounded-full gradient-primary blur-2xl opacity-40"
              />
              <div className="relative grid h-32 w-32 place-items-center rounded-full gradient-primary text-white shadow-soft-xl">
                <span className="font-display text-5xl font-bold">ET</span>
              </div>
            </div>
          </div>

          {/* Social buttons */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
            {SOCIALS.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={s.label}
                title={s.label}
                className={`group flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold text-white shadow-soft-md transition-all hover:-translate-y-0.5 hover:shadow-lg ${s.color}`}
              >
                <i className={s.icon} />
                <span className="hidden sm:inline">{s.label}</span>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ==================== ABOUT ==================== */}
      <section className="mx-auto max-w-5xl px-6 pb-16 lg:px-8">
        <div className="rounded-3xl border border-ink-100 bg-white p-8 shadow-soft-lg sm:p-12">
          <div className="grid gap-10 md:grid-cols-2">
            {/* Story */}
            <div className="space-y-5">
              <h2 className="font-display text-2xl font-bold text-ink-900">
                About the project
              </h2>
              <p className="text-sm leading-relaxed text-ink-600">
                Talentscope started as a way to make resume screening fair,
                transparent, and fast — for both job seekers and organizations.
                Every factor that goes into scoring is visible. No black boxes,
                no hidden rules.
              </p>
              <p className="text-sm leading-relaxed text-ink-600">
                The platform is built with a focus on:
              </p>
              <ul className="space-y-2.5">
                {[
                  'Transparent ATS scoring (6 visible factors)',
                  'Provider-agnostic LLM layer (100+ providers via LiteLLM)',
                  'Multi-tenant isolation via PostgreSQL RLS',
                  'Modern, accessible UI with real-time feedback',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-ink-700">
                    <i className="fa-solid fa-circle-check mt-0.5 text-emerald-500" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Tech stack */}
            <div className="space-y-5">
              <h2 className="font-display text-2xl font-bold text-ink-900">
                Tech stack
              </h2>
              <div className="flex flex-wrap gap-2">
                {[
                  'Python 3.12',
                  'FastAPI',
                  'PostgreSQL 16',
                  'SQLAlchemy 2.0',
                  'Celery',
                  'Redis',
                  'React 18',
                  'TypeScript',
                  'Vite',
                  'Tailwind CSS',
                  'LiteLLM',
                  'Docker',
                  'Kubernetes',
                ].map((tech) => (
                  <span
                    key={tech}
                    className="rounded-full border border-ink-200 bg-ink-50 px-3 py-1 text-xs font-medium text-ink-700"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== CONTACT CTA ==================== */}
      <section className="mx-auto max-w-4xl px-6 pb-24 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl p-10 text-center text-white shadow-soft-xl sm:p-14">
          <div
            aria-hidden
            className="absolute inset-0 gradient-hero animate-gradient-shift"
            style={{ backgroundSize: '200% 200%' }}
          />
          <div className="relative space-y-5">
            <h2 className="font-display text-3xl font-bold sm:text-4xl">
              Have an idea or a project?
            </h2>
            <p className="mx-auto max-w-lg text-base text-white/85">
              Whether you need help with a project, want to collaborate, or
              just have a question — I'd love to hear from you.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <Link
                to="/contact"
                className="inline-flex h-12 items-center gap-2 rounded-full bg-white px-7 text-sm font-semibold text-brand-700 shadow-lg transition hover:-translate-y-0.5 hover:bg-white/95"
              >
                <i className="fa-solid fa-paper-plane text-xs" />
                Get in touch
              </Link>
              <a
                href="https://github.com/EngEban"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-12 items-center gap-2 rounded-full border border-white/40 px-7 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                <i className="fa-brands fa-github" />
                View GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== BACK ==================== */}
      <section className="mx-auto max-w-7xl px-6 pb-16 text-center lg:px-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-brand-600 hover:text-brand-700"
        >
          <i className="fa-solid fa-arrow-left text-xs" />
          Back to home
        </Link>
      </section>
    </div>
  );
}
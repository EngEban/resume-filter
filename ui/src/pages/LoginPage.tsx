import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { authApi, APIError } from '@/lib/api';
import { Logo } from '@/components/Logo';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login: setSession } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');

    if (!email.trim() || !password) {
      setMessage('Enter your email and password to continue.');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await authApi.login(email.trim(), password);
      const profile = await setSession(result.access_token);
      const target = profile.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';
      navigate(target, { replace: true });
    } catch (error) {
      const detail =
        error instanceof APIError
          ? error.message
          : 'Unable to sign in. Check your details and try again.';
      setMessage(detail);
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-ink-50 page-enter">
      {/* ==================== LEFT: Illustration ==================== */}
      <aside className="relative hidden overflow-hidden bg-ink-950 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div aria-hidden className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(129,140,248,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(129,140,248,0.12)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:linear-gradient(to_bottom,black,transparent)]" />
        <div aria-hidden className="absolute -right-32 top-1/4 h-96 w-96 rounded-full bg-brand-600/30 blur-3xl animate-pulse-soft" />
        {/* Decorative circles */}
        <div aria-hidden className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-white/5 blur-3xl animate-float-slow" />
        <div aria-hidden className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-accent-400/20 blur-3xl animate-float-slow" />

        <div className="relative">
          <Logo size="md" to="/" variant="light" />
        </div>

        <div className="relative space-y-6 max-w-md">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">
            Resume Intelligence
          </p>
          <h1 className="text-5xl font-bold leading-[1.02] tracking-[-0.04em] text-white">
            Find the signal in every resume.
          </h1>
          <p className="text-base leading-7 text-white/80">
            TalentScope turns resume data into a clearer signal, so the right
            candidates come into focus sooner.
          </p>
        </div>

        <div className="relative">
          <p className="text-xs text-white/60">
            Clearer hiring decisions, one resume at a time.
          </p>
        </div>
      </aside>

      {/* ==================== RIGHT: Form ==================== */}
      <main className="flex items-center justify-center p-6 sm:p-10 lg:p-12">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile logo */}
          <div className="lg:hidden">
            <Logo size="md" to="/" />
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              Your workspace
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900">
              Welcome back
            </h1>
            <p className="text-base text-ink-600">
              Sign in to continue reviewing the candidates that matter.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            <div className="space-y-1.5">
              <label htmlFor="email" className="label">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="input"
                placeholder="you@company.com"
                aria-invalid={Boolean(message)}
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="label">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="input"
                placeholder="Enter your password"
                aria-invalid={Boolean(message)}
              />
            </div>

            {message && (
              <p
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700"
              >
                {message}
              </p>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary btn-lg w-full mt-2 hover-lift"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-sm text-ink-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-semibold text-brand-600 hover:text-brand-700"
            >
              Create one
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}

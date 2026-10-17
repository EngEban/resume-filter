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
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resendStatus, setResendStatus] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');
    setNeedsVerification(false);
    setResendStatus('');

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
      if (error instanceof APIError && error.status === 403) {
        setNeedsVerification(true);
      }
      const detail =
        error instanceof APIError
          ? error.message
          : 'Unable to sign in. Check your details and try again.';
      setMessage(detail);
      setIsSubmitting(false);
    }
  }

  async function handleResend() {
    setResendStatus('Sending...');
    try {
      await authApi.resendVerification(email.trim());
      setResendStatus('Verification email sent. Check your inbox.');
    } catch {
      setResendStatus('Could not resend. Try again later.');
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-ink-50 page-enter">
      {/* ==================== LEFT: Illustration ==================== */}
      <aside className="relative hidden overflow-hidden gradient-hero p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div aria-hidden className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(129,140,248,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(129,140,248,0.12)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:linear-gradient(to_bottom,black,transparent)]" />
        <div aria-hidden className="absolute -right-32 top-1/4 h-96 w-96 rounded-full bg-brand-600/30 blur-3xl animate-pulse-soft" />
        <div aria-hidden className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-white/5 blur-3xl animate-float-slow" />
        <div aria-hidden className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-accent-400/20 blur-3xl animate-float-slow" />

        <div className="relative">
          <Logo size="md" to="/" variant="light" />
        </div>

        <div className="relative space-y-6 max-w-md">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/70">
            Resume Intelligence
          </p>
          <h1 className="font-display text-5xl font-bold leading-[1.02] tracking-[-0.04em] text-white">
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
        <div className="w-full max-w-md space-y-8 rounded-3xl border border-ink-100 bg-white/95 p-6 shadow-soft-xl backdrop-blur-sm sm:p-10">
          <div className="lg:hidden">
            <Logo size="md" to="/" />
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              Your workspace
            </p>
            <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900">
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

            {needsVerification && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 space-y-3">
                <p className="text-sm text-amber-800">
                  Please verify your email before logging in.
                </p>
                <button
                  type="button"
                  onClick={handleResend}
                  className="text-sm font-semibold text-brand-600 hover:text-brand-700"
                >
                  Resend verification email
                </button>
                {resendStatus && (
                  <p className="text-xs text-ink-600">{resendStatus}</p>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary btn-lg w-full mt-2 hover-lift"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Google OAuth */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-ink-200" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-white px-3 text-ink-500">
                or continue with
              </span>
            </div>
          </div>

          <a
            href={authApi.googleLoginUrl()}
            className="btn btn-secondary btn-lg w-full flex items-center justify-center gap-3 hover-lift"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </a>

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

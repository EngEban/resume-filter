import { useMemo, useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { authApi, APIError } from '@/lib/api';
import { Logo } from '@/components/Logo';

type AccountType = 'b2c' | 'b2b';

const SLUG_RE = /^[a-z0-9-]+$/;

export default function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login: setSession } = useAuth();

  const initialType: AccountType = useMemo(
    () => (searchParams.get('type') === 'b2b' ? 'b2b' : 'b2c'),
    [searchParams],
  );

  const [accountType, setAccountType] = useState<AccountType>(initialType);
  const [organizationName, setOrganizationName] = useState('');
  const [organizationSlug, setOrganizationSlug] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): string {
    if (!email.trim() || !password) {
      return 'Please fill in all required fields.';
    }
    if (password.length < 8) {
      return 'Password must be at least 8 characters.';
    }
    if (accountType === 'b2b') {
      if (!organizationName.trim() || !organizationSlug.trim()) {
        return 'Organization name and slug are required.';
      }
      if (!SLUG_RE.test(organizationSlug)) {
        return 'Slug must contain only lowercase letters, digits, and hyphens.';
      }
    }
    return '';
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage('');

    const validationError = validate();
    if (validationError) {
      setMessage(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      const result =
        accountType === 'b2c'
          ? await authApi.registerB2C(email.trim(), password)
          : await authApi.registerB2B(
              organizationName.trim(),
              organizationSlug.trim(),
              email.trim(),
              password,
            );

      const profile = await setSession(result.access_token);
      const target = profile.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';
      navigate(target, { replace: true });
    } catch (error) {
      const detail =
        error instanceof APIError
          ? error.message
          : 'Unable to create your account. Try again.';
      setMessage(detail);
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-ink-50 page-enter">
      {/* ==================== LEFT: Illustration ==================== */}
      <aside className="relative hidden overflow-hidden bg-ink-950 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div aria-hidden className="absolute inset-0 opacity-70 [background-image:linear-gradient(rgba(129,140,248,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(129,140,248,0.12)_1px,transparent_1px)] [background-size:48px_48px] [mask-image:linear-gradient(to_bottom,black,transparent)]" />
        <div aria-hidden className="absolute -left-32 bottom-1/4 h-96 w-96 rounded-full bg-brand-600/30 blur-3xl animate-pulse-soft" />
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
            Build your hiring edge.
          </h1>
          <p className="text-base leading-7 text-white/80">
            Create a focused hiring workspace where strong signals are easy to
            see and act on.
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
          <div className="lg:hidden">
            <Logo size="md" to="/" />
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
              Start with ResumeFilter
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-ink-900">
              Create your account
            </h1>
            <p className="text-base text-ink-600">
              Set up your account and begin analyzing resumes with more clarity.
            </p>
          </div>

          {/* Account type toggle */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setAccountType('b2c')}
              className={`flex flex-col items-start gap-1 p-4 rounded-xl border text-left transition-all hover:-translate-y-0.5 ${
                accountType === 'b2c'
                  ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-500/20'
                  : 'border-ink-200 bg-white hover:border-ink-300'
              }`}
            >
              <span className="text-sm font-semibold text-ink-900">
                Individual
              </span>
              <span className="text-xs text-ink-500">Personal workspace</span>
            </button>

            <button
              type="button"
              onClick={() => setAccountType('b2b')}
              className={`flex flex-col items-start gap-1 p-4 rounded-xl border text-left transition-all hover:-translate-y-0.5 ${
                accountType === 'b2b'
                  ? 'border-brand-500 bg-brand-50 ring-2 ring-brand-500/20'
                  : 'border-ink-200 bg-white hover:border-ink-300'
              }`}
            >
              <span className="text-sm font-semibold text-ink-900">
                Organization
              </span>
              <span className="text-xs text-ink-500">Hiring workspace</span>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            {accountType === 'b2b' && (
              <>
                <div className="space-y-1.5">
                  <label htmlFor="org-name" className="label">
                    Organization name
                  </label>
                  <input
                    id="org-name"
                    type="text"
                    value={organizationName}
                    onChange={(event) => setOrganizationName(event.target.value)}
                    className="input"
                    placeholder="Acme Corp"
                  />
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="org-slug" className="label">
                    Organization slug
                  </label>
                  <input
                    id="org-slug"
                    type="text"
                    value={organizationSlug}
                    onChange={(event) =>
                      setOrganizationSlug(
                        event.target.value.toLowerCase().replace(/\s+/g, '-'),
                      )
                    }
                    className="input"
                    placeholder="acme-corp"
                  />
                  <p className="text-xs text-ink-500">
                    Lowercase letters, digits, hyphens only.
                  </p>
                </div>
              </>
            )}

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
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="input"
                placeholder="At least 8 characters"
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
              className="btn btn-primary btn-lg w-full mt-2"
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <p className="text-center text-sm text-ink-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-brand-600 hover:text-brand-700"
            >
              Sign in
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}

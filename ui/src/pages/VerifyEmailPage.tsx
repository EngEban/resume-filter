import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { authApi, APIError } from '@/lib/api';
import { Logo } from '@/components/Logo';

type State = 'loading' | 'success' | 'error';

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const [state, setState] = useState<State>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = params.get('token');
    if (!token) {
      setState('error');
      setMessage('Missing verification token.');
      return;
    }

    let active = true;
    (async () => {
      try {
        const res = await authApi.verifyEmail(token);
        if (!active) return;
        setState('success');
        setMessage(res.message);
      } catch (err) {
        if (!active) return;
        setState('error');
        setMessage(
          err instanceof APIError
            ? err.message
            : 'Verification failed. The link may be expired.',
        );
      }
    })();

    return () => {
      active = false;
    };
  }, [params]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-50 p-6 page-enter">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-ink-200 bg-white p-8 shadow-card">
        <div className="flex justify-center">
          <Logo size="md" to="/" />
        </div>

        {state === 'loading' && (
          <div className="text-center space-y-3">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
            <p className="text-sm text-ink-600">Verifying your email...</p>
          </div>
        )}

        {state === 'success' && (
          <div className="text-center space-y-4">
            <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-green-100 text-3xl">
              <i className="fa-solid fa-circle-check" />
            </div>
            <h1 className="text-2xl font-bold text-ink-900">Email verified</h1>
            <p className="text-sm text-ink-600">{message}</p>
            <Link to="/login" className="btn btn-primary w-full inline-block">
              Go to login
            </Link>
          </div>
        )}

        {state === 'error' && (
          <div className="text-center space-y-4">
            <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-red-100 text-3xl">
              <i className="fa-solid fa-circle-xmark" />
            </div>
            <h1 className="text-2xl font-bold text-ink-900">Verification failed</h1>
            <p className="text-sm text-ink-600">{message}</p>
            <p className="text-xs text-ink-500">
              You can request a new verification email from the login page.
            </p>
            <Link to="/login" className="btn btn-primary w-full inline-block">
              Back to login
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from '@/components/Logo';

export default function AuthCallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const token = params.get('token');
    if (!token) {
      setError('Missing authentication token.');
      setTimeout(() => navigate('/login?error=oauth_failed', { replace: true }), 2000);
      return;
    }

    let active = true;
    (async () => {
      try {
        const profile = await login(token);
        if (!active) return;
        const target =
          profile.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';
        navigate(target, { replace: true });
      } catch {
        if (!active) return;
        setError('Authentication failed.');
        setTimeout(() => navigate('/login?error=oauth_failed', { replace: true }), 2000);
      }
    })();

    return () => {
      active = false;
    };
  }, [params, login, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-50 p-6">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-ink-200 bg-white p-8 shadow-card text-center">
        <div className="flex justify-center">
          <Logo size="md" to="/" />
        </div>

        {!error ? (
          <>
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
            <p className="text-sm text-ink-600">Signing you in with Google...</p>
          </>
        ) : (
          <>
            <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-red-100 text-3xl">
              <i className="fa-solid fa-circle-xmark" />
            </div>
            <p className="text-sm text-red-700">{error}</p>
            <p className="text-xs text-ink-500">Redirecting to login...</p>
          </>
        )}
      </div>
    </div>
  );
}

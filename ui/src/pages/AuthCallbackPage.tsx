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
    <div className="gradient-hero flex min-h-screen items-center justify-center p-6 page-enter">
      <div className="w-full max-w-md space-y-6 rounded-3xl border border-white/30 bg-white/95 p-8 text-center shadow-soft-xl backdrop-blur-sm">
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

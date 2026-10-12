import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from './Logo';

const NAV = [
  { label: 'Features', href: '/#features' },
  { label: 'How it works', href: '/#how' },
  { label: 'For individuals', href: '/register?type=b2c' },
  { label: 'For organizations', href: '/register?type=b2b' },
];

export function PublicHeader() {
  const location = useLocation();
  const { isAuthenticated, user, isLoading } = useAuth();
  const onLanding = location.pathname === '/';
  const [menuOpen, setMenuOpen] = useState(false);

  const dashboardPath = user?.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';

  return (
    <header className="sticky top-0 z-50 border-b border-ink-200/80 bg-white/80 backdrop-blur-xl animate-slide-down">
      <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo size="md" />

        {onLanding && (
          <nav className="hidden items-center gap-8 lg:flex">
            {NAV.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm font-medium text-ink-600 hover:text-ink-900 transition-colors relative group link-animated"
              >
                {item.label}
              </a>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-2">
          {isLoading ? (
            <div className="h-9 w-24 skeleton" aria-hidden />
          ) : isAuthenticated ? (
            <>
              <span className="hidden sm:inline text-sm text-ink-500">
                {user?.email}
              </span>
              <Link to={dashboardPath} className="btn btn-primary btn-sm">
                Dashboard
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost btn-sm hidden sm:inline-flex">
                Sign in
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm hidden sm:inline-flex">
                Get started
              </Link>
              {onLanding && (
                <button
                  type="button"
                  className="grid h-10 w-10 place-items-center rounded-xl text-ink-600 hover:bg-ink-100 hover:text-ink-900 lg:hidden"
                  onClick={() => setMenuOpen((value) => !value)}
                  aria-expanded={menuOpen}
                  aria-controls="public-navigation"
                  aria-label={menuOpen ? 'Close menu' : 'Open menu'}
                >
                  <span className="text-lg">{menuOpen ? '×' : '☰'}</span>
                </button>
              )}
            </>
          )}
        </div>
      </div>
      {onLanding && menuOpen && !isAuthenticated && (
        <nav id="public-navigation" className="border-t border-ink-200/80 bg-white px-4 py-3 shadow-lg lg:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-1">
            {NAV.map((item) => (
              <a key={item.label} href={item.href} onClick={() => setMenuOpen(false)} className="rounded-xl px-3 py-2.5 text-sm font-medium text-ink-700 hover:bg-brand-50 hover:text-brand-700">
                {item.label}
              </a>
            ))}
            <div className="mt-2 grid grid-cols-2 gap-2 border-t border-ink-200 pt-3">
              <Link to="/login" onClick={() => setMenuOpen(false)} className="btn btn-secondary btn-sm">Sign in</Link>
              <Link to="/register" onClick={() => setMenuOpen(false)} className="btn btn-primary btn-sm">Get started</Link>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}

import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from './Logo';
import { UserMenu } from './UserMenu';

const NAV = [
  { label: 'Product', href: '/#features' },
  { label: 'How it works', href: '/#how' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'About', href: '/about' },
];

export function PublicHeader() {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuth();
  const onLanding = location.pathname === '/';
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-ink-200/50 bg-white/70 backdrop-blur-xl">
      <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo size="md" />

        {onLanding && (
          <nav className="hidden items-center gap-1 lg:flex">
            {NAV.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="rounded-full px-4 py-2 text-sm font-medium text-ink-600 transition-colors hover:bg-ink-50 hover:text-ink-900"
              >
                {item.label}
              </a>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-2">
          {isLoading ? (
            <div className="h-10 w-32 skeleton rounded-full" aria-hidden />
          ) : isAuthenticated ? (
            <>
              <UserMenu />
              {onLanding && (
                <button
                  type="button"
                  className="grid h-10 w-10 place-items-center rounded-xl text-ink-600 hover:bg-ink-100 hover:text-ink-900 lg:hidden"
                  onClick={() => setMenuOpen((v) => !v)}
                  aria-expanded={menuOpen}
                  aria-controls="public-navigation"
                  aria-label={menuOpen ? 'Close menu' : 'Open menu'}
                >
                  <i className={menuOpen ? 'fa-solid fa-xmark text-lg' : 'fa-solid fa-bars text-lg'} />
                </button>
              )}
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="hidden rounded-full px-4 py-2 text-sm font-medium text-ink-600 transition hover:bg-ink-50 hover:text-ink-900 sm:inline-flex"
              >
                Log in
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm hidden sm:inline-flex">
                Get started
                <i className="fa-solid fa-arrow-right text-xs" />
              </Link>
              {onLanding && (
                <button
                  type="button"
                  className="grid h-10 w-10 place-items-center rounded-xl text-ink-600 hover:bg-ink-100 hover:text-ink-900 lg:hidden"
                  onClick={() => setMenuOpen((v) => !v)}
                  aria-expanded={menuOpen}
                  aria-controls="public-navigation"
                  aria-label={menuOpen ? 'Close menu' : 'Open menu'}
                >
                  <i className={menuOpen ? 'fa-solid fa-xmark text-lg' : 'fa-solid fa-bars text-lg'} />
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {onLanding && menuOpen && (
        <nav id="public-navigation" className="border-t border-ink-200/50 bg-white px-4 py-3 shadow-lg lg:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-1">
            {NAV.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className="rounded-xl px-3 py-2.5 text-sm font-medium text-ink-700 hover:bg-brand-50 hover:text-brand-700"
              >
                {item.label}
              </a>
            ))}
            {!isAuthenticated && (
              <div className="mt-2 grid grid-cols-2 gap-2 border-t border-ink-200 pt-3">
                <Link to="/login" onClick={() => setMenuOpen(false)} className="btn btn-secondary btn-sm">
                  Log in
                </Link>
                <Link to="/register" onClick={() => setMenuOpen(false)} className="btn btn-primary btn-sm">
                  Get started
                </Link>
              </div>
            )}
          </div>
        </nav>
      )}
    </header>
  );
}
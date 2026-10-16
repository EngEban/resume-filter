import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function UserMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [open]);

  // Close on Escape
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }
    if (open) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [open]);

  if (!user) return null;

    const displayName =
    user.display_name || user.email.split('@')[0] || 'User';
  const initial = (displayName[0] || '?').toUpperCase();
  const isB2B = user.account_type === 'b2b';

  const items: { label: string; href: string; icon: string }[] = isB2B
    ? [
        { label: 'Dashboard', href: '/b2b/dashboard', icon: 'fa-solid fa-gauge-high' },
        { label: 'Batches', href: '/b2b/batches', icon: 'fa-solid fa-layer-group' },
        { label: 'Candidates', href: '/b2b/candidates', icon: 'fa-solid fa-users' },
        { label: 'Analytics', href: '/b2b/analytics', icon: 'fa-solid fa-chart-pie' },
        { label: 'Settings', href: '/b2b/settings', icon: 'fa-solid fa-gear' },
      ]
    : [
        { label: 'Dashboard', href: '/dashboard', icon: 'fa-solid fa-gauge-high' },
        { label: 'Analyze', href: '/analyze', icon: 'fa-solid fa-wand-magic-sparkles' },
        { label: 'History', href: '/history', icon: 'fa-solid fa-clock-rotate-left' },
        { label: 'Settings', href: '/settings', icon: 'fa-solid fa-gear' },
      ];

    function handleLogout() {
    setOpen(false);
    logout();
    navigate('/', { replace: true });
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="menu"
        className="flex items-center gap-2.5 rounded-full border border-ink-200 bg-white py-1.5 pl-1.5 pr-4 text-sm font-medium text-ink-800 transition-all hover:border-brand-300 hover:shadow-soft-md focus:outline-none focus:ring-2 focus:ring-brand-500/20"
      >
        <span className="grid h-8 w-8 place-items-center rounded-full gradient-primary font-display text-xs font-bold text-white">
          {initial}
        </span>
        <span className="hidden max-w-[140px] truncate sm:inline">
          {displayName}
        </span>
        <i
          className={`fa-solid fa-chevron-down text-[10px] text-ink-400 transition-transform ${
            open ? 'rotate-180' : ''
          }`}
        />
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 z-50 mt-2 w-72 origin-top-right animate-fade-in-up overflow-hidden rounded-2xl border border-ink-100 bg-white shadow-soft-xl"
        >
          {/* Header */}
          <div className="border-b border-ink-100 bg-gradient-to-br from-brand-50 to-pink-50/50 px-5 py-4">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-full gradient-primary font-display text-sm font-bold text-white shadow-soft-md">
                {initial}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate font-display text-sm font-semibold text-ink-900">
                  {displayName}
                </p>
                <p className="truncate text-xs text-ink-500">{user.email}</p>
              </div>
            </div>
            <div className="mt-3">
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide ${
                  isB2B
                    ? 'bg-brand-100 text-brand-700'
                    : 'bg-pink-100 text-pink-700'
                }`}
              >
                <i
                  className={`${
                    isB2B ? 'fa-solid fa-building' : 'fa-solid fa-user'
                  } text-[9px]`}
                />
                {isB2B ? 'Organization' : 'Individual'}
              </span>
            </div>
          </div>

          {/* Menu items */}
          <div className="py-2">
            {items.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 px-5 py-2.5 text-sm text-ink-700 transition-colors hover:bg-brand-50 hover:text-brand-700"
              >
                <i className={`${item.icon} w-4 text-center text-ink-400`} />
                {item.label}
              </Link>
            ))}
          </div>

          {/* Logout */}
          <div className="border-t border-ink-100 py-2">
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 px-5 py-2.5 text-left text-sm text-red-600 transition-colors hover:bg-red-50"
            >
              <i className="fa-solid fa-right-from-bracket w-4 text-center" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
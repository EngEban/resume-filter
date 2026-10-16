import { useState, type ReactNode } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from './Logo';

interface NavItemProps {
  to: string;
  label: string;
  icon: ReactNode;
  end?: boolean;
}

function NavItem({ to, label, icon, end }: NavItemProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          'group flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
          isActive
            ? 'bg-white/12 text-white shadow-sm'
            : 'text-slate-300 hover:bg-white/8 hover:text-white hover:translate-x-0.5',
        ].join(' ')
      }
    >
      <span className="shrink-0 transition-transform duration-200 group-hover:scale-110">
        {icon}
      </span>
      <span className="truncate">{label}</span>
    </NavLink>
  );
}

const icons = {
  dashboard: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9" rx="1" />
      <rect x="14" y="3" width="7" height="5" rx="1" />
      <rect x="14" y="12" width="7" height="9" rx="1" />
      <rect x="3" y="16" width="7" height="5" rx="1" />
    </svg>
  ),
  batches: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  ),
  candidates: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  analytics: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 3v18h18" />
      <path d="m19 9-5 5-4-4-3 3" />
    </svg>
  ),
  exports: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  ),
  analyze: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <path d="M9 15l2 2 4-4" />
    </svg>
  ),
  history: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l4 2" />
    </svg>
  ),
  settings: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
  logout: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  ),
};

function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <p
      className="px-3.5 pt-6 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500"
    >
      {children}
    </p>
  );
}

function B2CNav() {
  return (
    <>
      <SectionLabel>Workspace</SectionLabel>
      <div className="space-y-1">
        <NavItem to="/dashboard" label="Dashboard" icon={icons.dashboard} />
        <NavItem to="/analyze" label="Analyze Resume" icon={icons.analyze} />
        <NavItem to="/history" label="History" icon={icons.history} />
      </div>

      <SectionLabel>Account</SectionLabel>
      <div className="space-y-1">
        <NavItem to="/settings" label="Settings" icon={icons.settings} />
      </div>
    </>
  );
}

function B2BNav() {
  return (
    <>
      <SectionLabel>Workspace</SectionLabel>
      <div className="space-y-1">
        <NavItem to="/b2b/dashboard" label="Dashboard" icon={icons.dashboard} />
        <NavItem to="/b2b/batches" label="Batches" icon={icons.batches} />
        <NavItem to="/b2b/candidates" label="Candidates" icon={icons.candidates} />
      </div>

      <SectionLabel>Insights</SectionLabel>
      <div className="space-y-1">
        <NavItem to="/b2b/analytics" label="Analytics" icon={icons.analytics} />
        <NavItem to="/b2b/exports" label="Exports" icon={icons.exports} />
      </div>

      <SectionLabel>Organization</SectionLabel>
      <div className="space-y-1">
        <NavItem to="/b2b/settings" label="AI Settings" icon={icons.settings} />
      </div>
    </>
  );
}

export function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <aside className="relative z-40 w-full shrink-0 border-b border-slate-800 bg-ink-950 text-white md:sticky md:top-0 md:h-screen md:w-72 md:border-b-0 md:border-r">
      <div className="flex h-[68px] items-center justify-between border-b border-white/10 px-4 sm:px-5">
        <Logo size="md" variant="light" />
        <button
          type="button"
          className="grid h-10 w-10 place-items-center rounded-xl text-slate-300 hover:bg-white/10 hover:text-white md:hidden"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          aria-controls="workspace-navigation"
          aria-label={open ? 'Close navigation' : 'Open navigation'}
        >
          <span className="text-xl leading-none"><i className={open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars'} /></span>
        </button>
      </div>

      <nav
        id="workspace-navigation"
        onClick={() => setOpen(false)}
        className={`${open ? 'flex' : 'hidden'} absolute left-0 right-0 top-[68px] max-h-[calc(100vh-68px)] flex-col overflow-y-auto border-b border-white/10 bg-ink-950 px-3 pb-4 shadow-2xl md:static md:flex md:h-[calc(100vh-68px)] md:max-h-none md:border-0 md:shadow-none`}
      >
        <div className="mb-2 mt-4 rounded-2xl border border-white/10 bg-white/5 px-3.5 py-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-brand-300">Workspace</p>
          <p className="mt-1 truncate text-sm font-semibold text-white">
            {user?.account_type === 'b2b' ? 'Organization intelligence' : 'Personal intelligence'}
          </p>
        </div>
        {user?.account_type === 'b2b' ? <B2BNav /> : <B2CNav />}

        <div className="mt-auto border-t border-white/10 pt-3">
          <div className="mb-2 flex items-center gap-3 rounded-xl bg-white/5 px-3 py-2.5">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-400 to-brand-700 text-sm font-semibold text-white ring-1 ring-white/20">
            {(user?.email?.[0] ?? 'U').toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-white">{user?.email ?? 'User'}</p>
              <p className="text-xs uppercase tracking-wide text-slate-500">{user?.account_type ?? ''}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-300 transition-all duration-150 hover:bg-red-500/10 hover:text-red-300"
          >
            {icons.logout}
            <span>Sign out</span>
          </button>
        </div>
      </nav>
    </aside>
  );
}

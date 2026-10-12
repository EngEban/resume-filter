import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from './Logo';
import { DeveloperCard } from './DeveloperCard';
import { BORDER, TEXT_MUTED } from '@/theme';

export function Footer() {
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  const onLanding = location.pathname === '/';
  const dashboardPath = user?.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';

  return (
    <footer className="border-t bg-white" style={{ borderColor: BORDER }}>
      {/* ============ Main content ============ */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 pt-12 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="md:col-span-2 space-y-4">
            <Logo size="md" />
            <p className="text-sm max-w-sm" style={{ color: TEXT_MUTED }}>
              AI-powered resume intelligence for job seekers and organizations.
              Understand how your resume matches the job before you apply.
            </p>
          </div>

          {/* Product — only on landing */}
          {onLanding && (
            <div className="space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
                Product
              </h4>
              <ul className="space-y-2">
                <li>
                  <a
                    href="/#features"
                    className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                  >
                    Features
                    <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                  </a>
                </li>
                <li>
                  <a
                    href="/#how"
                    className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                  >
                    How it works
                    <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                  </a>
                </li>
              </ul>
            </div>
          )}

          {/* Account — auth-aware */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
              Account
            </h4>
            <ul className="space-y-2">
              {isAuthenticated ? (
                <>
                  <li>
                    <Link
                      to={dashboardPath}
                      className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                    >
                      Go to Dashboard
                      <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                    </Link>
                  </li>
                  {user?.account_type === 'b2c' && (
                    <li>
                      <Link
                        to="/analyze"
                        className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                      >
                        Analyze Resume
                        <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                      </Link>
                    </li>
                  )}
                  {user?.account_type === 'b2b' && (
                    <li>
                      <Link
                        to="/b2b/batches"
                        className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                      >
                        Batches
                        <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                      </Link>
                    </li>
                  )}
                </>
              ) : (
                <>
                  <li>
                    <Link
                      to="/register?type=b2c"
                      className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                    >
                      For Individuals
                      <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/register?type=b2b"
                      className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                    >
                      For Organizations
                      <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                    </Link>
                  </li>
                  <li>
                    <Link
                      to="/login"
                      className="text-sm text-ink-600 hover:text-brand-600 transition-colors relative group inline-block"
                    >
                      Sign in
                      <span className="absolute -bottom-0.5 left-0 w-0 h-px bg-brand-600 transition-all duration-200 group-hover:w-full" />
                    </Link>
                  </li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* ============ Bottom bar — same background, thin border ============ */}
      <div className="border-t bg-ink-50/50" style={{ borderColor: BORDER }}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs" style={{ color: TEXT_MUTED }}>
              © {new Date().getFullYear()} TalentScope. All rights reserved.
            </p>
            <DeveloperCard />
          </div>
        </div>
      </div>
    </footer>
  );
}
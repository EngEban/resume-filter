import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Logo } from './Logo';

export function Footer() {
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  const onLanding = location.pathname === '/';
  const dashboardPath = user?.account_type === 'b2b' ? '/b2b/batches' : '/dashboard';

  return (
    <footer className="relative overflow-hidden border-t border-ink-200/50 bg-white">
      {/* Decorative blob */}
      <img
        src="/images/hero/06_footer_decorative_blob_400x400.png"
        alt=""
        aria-hidden
        className="pointer-events-none absolute -right-16 -bottom-16 w-64 opacity-60 lg:w-80"
      />

      <div className="relative mx-auto max-w-7xl px-6 pt-16 pb-8 lg:px-8">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-12">
          {/* Brand */}
          <div className="md:col-span-4 space-y-5">
            <Logo size="md" />
            <p className="max-w-sm text-sm leading-relaxed text-ink-500">
              AI-powered resume intelligence for job seekers and organizations.
              Understand how your resume matches the job before you apply.
            </p>
            <SocialLinks />
          </div>

          {/* Product */}
          {onLanding && (
            <div className="md:col-span-2 space-y-4">
              <h4 className="font-display text-xs font-semibold uppercase tracking-wider text-ink-900">
                Product
              </h4>
              <ul className="space-y-2.5 text-sm">
                <FooterLink href="/#features" label="Features" />
                <FooterLink href="/#how" label="How it works" />
                <FooterLink href="/#pricing" label="Pricing" />
              </ul>
            </div>
          )}

          {/* Company */}
          <div className="md:col-span-2 space-y-4">
            <h4 className="font-display text-xs font-semibold uppercase tracking-wider text-ink-900">
              Company
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/about" className="text-ink-600 transition-colors hover:text-brand-600">
                  About the developer
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-ink-600 transition-colors hover:text-brand-600">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-ink-600 transition-colors hover:text-brand-600">
                  Report an issue
                </Link>
              </li>
            </ul>
          </div>

          {/* Account */}
          <div className="md:col-span-4 space-y-4">
            <h4 className="font-display text-xs font-semibold uppercase tracking-wider text-ink-900">
              Account
            </h4>
            <ul className="space-y-2.5 text-sm">
              {isAuthenticated ? (
                <>
                  <li>
                    <Link to={dashboardPath} className="text-ink-600 transition-colors hover:text-brand-600">
                      Go to Dashboard
                    </Link>
                  </li>
                  {user?.account_type === 'b2c' && (
                    <li>
                      <Link to="/analyze" className="text-ink-600 transition-colors hover:text-brand-600">
                        Analyze Resume
                      </Link>
                    </li>
                  )}
                  {user?.account_type === 'b2b' && (
                    <li>
                      <Link to="/b2b/batches" className="text-ink-600 transition-colors hover:text-brand-600">
                        Batches
                      </Link>
                    </li>
                  )}
                </>
              ) : (
                <>
                  <li>
                    <Link to="/register?type=b2c" className="text-ink-600 transition-colors hover:text-brand-600">
                      For Individuals
                    </Link>
                  </li>
                  <li>
                    <Link to="/register?type=b2b" className="text-ink-600 transition-colors hover:text-brand-600">
                      For Organizations
                    </Link>
                  </li>
                  <li>
                    <Link to="/login" className="text-ink-600 transition-colors hover:text-brand-600">
                      Sign in
                    </Link>
                  </li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="relative border-t border-ink-200/50 bg-ink-50/50">
        <div className="mx-auto max-w-7xl px-6 py-5 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-xs text-ink-500">
              © {new Date().getFullYear()} Talentscope. All rights reserved.
            </p>
            <div className="flex items-center gap-4 text-xs text-ink-500">
              <Link to="/contact" className="hover:text-brand-600">
                Privacy
              </Link>
              <span className="text-ink-300">·</span>
              <Link to="/contact" className="hover:text-brand-600">
                Terms
              </Link>
              <span className="text-ink-300">·</span>
              <p>
                Built by{' '}
                <Link to="/about" className="font-semibold text-brand-600 hover:text-brand-700">
                  Eban Tbail
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ============================================================
// Social Links — colored brand icons
// ============================================================
function SocialLinks() {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <SocialButton
        href="https://wa.me/970592630530"
        label="WhatsApp"
        className="bg-[#25D366] hover:bg-[#1EBE5A]"
        icon="fa-brands fa-whatsapp"
      />
      <SocialButton
        href="https://www.instagram.com/smartdev1.ai/"
        label="Instagram"
        className="bg-gradient-to-tr from-[#F58529] via-[#DD2A7B] to-[#8134AF] hover:opacity-90"
        icon="fa-brands fa-instagram"
      />
      <SocialButton
        href="https://github.com/EngEban"
        label="GitHub"
        className="bg-[#181717] hover:bg-[#333]"
        icon="fa-brands fa-github"
      />
      <SocialButton
        href="https://www.linkedin.com/in/eban-tbail/"
        label="LinkedIn"
        className="bg-[#0A66C2] hover:bg-[#0856A8]"
        icon="fa-brands fa-linkedin-in"
      />
      <SocialButton
        href="mailto:ebantbaeil2004@gmail.com"
        label="Email"
        className="bg-brand-600 hover:bg-brand-700"
        icon="fa-solid fa-envelope"
      />
    </div>
  );
}

function SocialButton({
  href,
  label,
  className,
  icon,
}: {
  href: string;
  label: string;
  className: string;
  icon: string;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={label}
      title={label}
      className={`grid h-9 w-9 place-items-center rounded-full text-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md ${className}`}
    >
      <i className={`${icon} text-sm`} />
    </a>
  );
}

function FooterLink({ href, label }: { href: string; label: string }) {
  return (
    <li>
      <a href={href} className="text-ink-600 transition-colors hover:text-brand-600">
        {label}
      </a>
    </li>
  );
}
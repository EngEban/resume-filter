// ============================================================
// src/components/Logo.tsx
// TalentScope brand mark + wordmark (monochrome wordmark).
// ============================================================
import { Link } from 'react-router-dom';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showWordmark?: boolean;
  to?: string;
  variant?: 'dark' | 'light' | 'auto';
}

const SIZES = {
  sm: { box: 'h-8 w-8', text: 'text-base', icon: 16 },
  md: { box: 'h-9 w-9', text: 'text-lg', icon: 18 },
  lg: { box: 'h-12 w-12', text: 'text-2xl', icon: 24 },
} as const;

export function Logo({
  size = 'md',
  showWordmark = true,
  to = '/',
  variant = 'auto',
}: LogoProps) {
  const { box, text, icon } = SIZES[size];

  // ---------- Wordmark color ----------
  let wordmarkStyle: React.CSSProperties | undefined;
  let wordmarkClass = 'font-semibold tracking-tight';

  if (variant === 'light') {
    wordmarkClass += ' text-white';
  } else if (variant === 'dark') {
    wordmarkClass += ' text-ink-900';
  } else {
    // Auto: inherit from parent (currentColor)
    wordmarkStyle = { color: 'currentColor' };
  }

  // ---------- Icon background ----------
  // The mark keeps a subtle gradient for brand recognition.
  const iconBg =
    variant === 'light'
      ? 'bg-white/15 backdrop-blur-sm ring-1 ring-white/20'
      : 'bg-gradient-to-br from-brand-500 to-brand-700 shadow-brand';

  const content = (
    <div className="flex items-center gap-2.5 select-none">
      <div className={`${box} rounded-[14px] grid place-items-center ${iconBg} transition-transform duration-300 group-hover:rotate-3`}>
        <svg
          width={icon}
          height={icon}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="2" fill="none" />
          <path
            d="M12 4v4M12 16v4M4 12h4M16 12h4"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <circle cx="12" cy="12" r="2" fill="white" />
        </svg>
      </div>

      {showWordmark && (
        <span className={`${text} ${wordmarkClass}`} style={wordmarkStyle}>
          TalentScope
        </span>
      )}
    </div>
  );

  if (to) {
    return (
      <Link to={to} className="group inline-flex hover:opacity-90 transition-opacity duration-200">
        {content}
      </Link>
    );
  }

  return content;
}

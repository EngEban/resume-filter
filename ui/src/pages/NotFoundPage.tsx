// ============================================================
// src/pages/NotFoundPage.tsx
// ============================================================
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="page-enter relative flex min-h-[70vh] items-center justify-center overflow-hidden px-6">
      <div aria-hidden className="absolute h-80 w-80 rounded-full bg-brand-100/50 blur-3xl" />
      <div className="text-center space-y-6 max-w-md">
        <p className="relative text-[8rem] font-bold leading-none tracking-[-0.08em] bg-gradient-to-br from-brand-500 to-brand-700 bg-clip-text text-transparent">
          404
        </p>
        <h1 className="font-display text-2xl font-bold text-ink-900">
          Page not found
        </h1>
        <p className="text-ink-500">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link to="/" className="btn btn-primary">
            Back to home
          </Link>
          <Link to="/login" className="btn btn-secondary">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

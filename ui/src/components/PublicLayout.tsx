// ============================================================
// src/components/PublicLayout.tsx
// Public page layout: header + main + footer.
// ============================================================
import type { ReactNode } from 'react';
import { Footer } from './Footer';
import { PublicHeader } from './PublicHeader';

interface PublicLayoutProps {
  children: ReactNode;
  showHeader?: boolean;
  showFooter?: boolean;
}

export function PublicLayout({
  children,
  showHeader = true,
  showFooter = true,
}: PublicLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-ink-50">
      {showHeader && <PublicHeader />}
      <main className="flex-1 page-enter">{children}</main>
      {showFooter && <Footer />}
    </div>
  );
}

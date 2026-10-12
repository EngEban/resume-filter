// ============================================================
// src/components/AppLayout.tsx
// Authenticated page layout: sidebar + main content.
// ============================================================
import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-ink-50 md:flex">
      <Sidebar />
      <main className="flex-1 min-w-0">
        <div className="page-enter mx-auto max-w-[1440px] px-4 py-7 sm:px-6 lg:px-10 lg:py-10">
          {children}
        </div>
      </main>
    </div>
  );
}

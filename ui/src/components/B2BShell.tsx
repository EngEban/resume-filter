import { type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { UserMenu } from './UserMenu';

interface B2BShellProps {
  children: ReactNode;
  active?: string;
  batchId?: string;
}

export default function B2BShell({ children }: B2BShellProps) {
  return (
    <div className="min-h-screen bg-ink-50 md:flex">
      <Sidebar />
      <main className="flex-1 min-w-0">
        {/* Topbar */}
        <div className="sticky top-0 z-40 border-b border-ink-200/50 bg-white/70 backdrop-blur-xl">
          <div className="mx-auto flex h-[68px] max-w-[1440px] items-center justify-end gap-3 px-4 sm:px-6 lg:px-10">
            <UserMenu />
          </div>
        </div>

        {/* Content */}
        <div className="page-enter mx-auto max-w-[1440px] px-4 py-7 sm:px-6 lg:px-10 lg:py-10">
          {children}
        </div>
      </main>
    </div>
  );
}
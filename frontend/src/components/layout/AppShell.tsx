import type { ReactNode } from 'react';
import { Header } from './Header';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-warm">
      <Header />
      <main className="flex-1 overflow-y-auto px-4 md:px-6 py-6 pb-8">
        {children}
      </main>
    </div>
  );
}

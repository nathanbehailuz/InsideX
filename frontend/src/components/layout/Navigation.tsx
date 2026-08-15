/**
 * OpenSignal top navigation — brand + app links only (no account chrome)
 */

'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Signals', href: '/signals' },
  { name: 'Companies', href: '/companies' },
  { name: 'People', href: '/insiders' },
  { name: 'Trades', href: '/trades' },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-surface border-b border-border shadow-sm fixed top-0 w-full z-50">
      <div className="os-container flex items-center gap-8 h-16">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <Image
            src="/opensignal-logo.png"
            alt="OpenSignal"
            width={32}
            height={32}
            className="h-8 w-8 rounded-md object-cover"
            priority
          />
          <span className="text-xl font-bold text-primary tracking-tight">
            OpenSignal
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-6 h-16">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'text-xs font-semibold tracking-wider uppercase h-full flex items-center border-b-2 transition-colors',
                  isActive
                    ? 'text-primary border-primary'
                    : 'text-secondary border-transparent hover:text-primary'
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>

      <div className="md:hidden border-t border-border overflow-x-auto">
        <div className="flex gap-1 px-4 py-2">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'whitespace-nowrap px-3 py-1.5 rounded text-xs font-semibold tracking-wider uppercase',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-secondary hover:text-primary'
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />
      <main className="flex-grow pt-20 md:pt-24 pb-12 os-container w-full relative z-10">
        {children}
      </main>
      <SiteFooter />
    </div>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-surface mt-auto">
      <div className="os-container py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-sm text-secondary">
        <p>
          <span className="font-semibold text-primary">OpenSignal</span>
          {' '}© 2026. Data from public financial disclosures. Not investment advice.
        </p>
        <p>
          Made by{' '}
          <a
            href="https://nathanbehailu.vercel.app/projects.html#insidex"
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-primary hover:underline"
          >
            Nathan
          </a>
        </p>
      </div>
    </footer>
  );
}

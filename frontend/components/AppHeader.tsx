'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { href: '/', label: 'Products' },
  { href: '/deals', label: 'Best Deals' },
  { href: '/stores', label: 'Stores' },
  { href: '/help', label: 'Get Intelligent Help' },
];

export default function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <Link href="/" className="w-fit">
            <p className="text-3xl font-bold text-gray-900">PromoChecker</p>
            <p className="text-sm text-gray-600 mt-1">Find the best laptop deals in Tunisia</p>
          </Link>
          <nav className="flex items-center gap-x-5 gap-y-2 overflow-x-auto pb-1 lg:pb-0" aria-label="Main navigation">
            {navigation.map((item) => {
              const isActive = item.href === '/'
                ? pathname === '/' || pathname.startsWith('/products/')
                : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`whitespace-nowrap text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-teal-700 font-semibold'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}

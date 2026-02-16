'use client';

import { useState, useEffect } from 'react';
import { getStores } from '@/lib/api';
import type { Store } from '@/lib/types';

export default function StoresPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStores();
  }, []);

  const loadStores = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStores();
      setStores(data);
    } catch (err) {
      setError('Failed to load stores. Make sure the backend is running on http://localhost:8000');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">PromoChecker</h1>
              <p className="text-sm text-gray-600 mt-1">Find the best laptop deals in Tunisia</p>
            </div>
            <nav className="flex gap-6">
              <a href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                Products
              </a>
              <a href="/deals" className="text-gray-600 hover:text-gray-900 transition-colors">
                Best Deals
              </a>
              <a href="/stores" className="text-blue-600 font-semibold hover:text-blue-700 transition-colors">
                Stores
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Our Partner Stores</h2>
          <p className="text-gray-600">Compare prices across these trusted retailers in Tunisia</p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800 font-semibold mb-2">Oops! Something went wrong</p>
            <p className="text-red-600 text-sm">{error}</p>
            <button 
              onClick={loadStores}
              className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Stores Grid */}
        {!loading && !error && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stores.map((store) => (
              <div
                key={store.store_name}
                className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-200 group"
              >
                {/* Store Header */}
                <div className="bg-gradient-to-r from-teal-600 to-teal-700 p-6 text-white">
                  <div className="flex items-center gap-3 mb-2">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    <h3 className="text-2xl font-bold">{store.store_name}</h3>
                  </div>
                  <a 
                    href={store.base_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-100 hover:text-white text-sm flex items-center gap-1 group-hover:gap-2 transition-all"
                  >
                    Visit Website
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>

                {/* Store Stats */}
                <div className="p-6">
                  <div className="mb-4">
                    <div className="bg-teal-50 rounded-lg p-4 text-center">
                      <p className="text-xs text-teal-600 font-semibold uppercase tracking-wide mb-1">
                        Products Available
                      </p>
                      <p className="text-3xl font-bold text-gray-900">{store.product_count}</p>
                    </div>
                  </div>

                  <div className="border-t border-gray-200 pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-600">Lowest Price:</span>
                      <span className="text-sm font-bold text-green-600">
                        {store.min_price?.toFixed(2) ?? 'N/A'} TND
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Highest Price:</span>
                      <span className="text-sm font-bold text-red-600">
                        {store.max_price?.toFixed(2) ?? 'N/A'} TND
                      </span>
                    </div>
                  </div>

                  {/* Price Range Bar */}
                  <div className="mt-4">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-green-500 to-blue-600"
                        style={{ width: '100%' }}
                      ></div>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-gray-400">Affordable</span>
                      <span className="text-xs text-gray-400">Premium</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600 text-sm">
          <p>PromoChecker - Compare laptop prices across Tunisian stores</p>
          <p className="mt-2 text-gray-400">Prices updated daily at 2:00 AM</p>
        </div>
      </footer>
    </div>
  );
}

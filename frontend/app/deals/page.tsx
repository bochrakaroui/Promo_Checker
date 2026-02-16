'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getDeals } from '@/lib/api';
import type { Deal, PaginatedResponse } from '@/lib/types';

export default function DealsPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [minDifference, setMinDifference] = useState(100);

  useEffect(() => {
    loadDeals();
  }, [page, minDifference]);

  const loadDeals = async () => {
    try {
      setLoading(true);
      setError(null);
      const response: any = await getDeals(minDifference, page, 20);
      console.log('Deals response:', response);
      
      // Handle both array response and paginated response
      if (Array.isArray(response)) {
        setDeals(response);
        setTotalPages(1);
      } else {
        setDeals(response.items || []);
        setTotalPages(response.total_pages || 1);
      }
    } catch (err) {
      setError('Failed to load deals. Make sure the backend is running on http://localhost:8000');
      console.error('Deals error:', err);
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
              <a href="/deals" className="text-blue-600 font-semibold hover:text-blue-700 transition-colors">
                Best Deals
              </a>
              <a href="/stores" className="text-gray-600 hover:text-gray-900 transition-colors">
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
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Best Deals</h2>
          <p className="text-gray-600">Products with the biggest price differences between stores</p>
        </div>

        {/* Filter */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <label className="text-sm font-semibold text-gray-700">
              Minimum Savings:
            </label>
            <div className="flex gap-2 flex-wrap">
              {[50, 100, 200, 500, 1000].map((value) => (
                <button
                  key={value}
                  onClick={() => {
                    setMinDifference(value);
                    setPage(1);
                  }}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    minDifference === value
                      ? 'bg-teal-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {value}+ TND
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
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
              onClick={loadDeals}
              className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Deals List */}
        {!loading && !error && (
          <>
            {!deals || deals.length === 0 ? (
              <div className="text-center py-20">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-500 text-lg">No deals found with savings over {minDifference} TND</p>
                <p className="text-gray-400 text-sm mt-2">Try lowering the minimum savings amount</p>
              </div>
            ) : (
              <>
                <div className="mb-6">
                  <p className="text-gray-600 text-sm">
                    Found <span className="font-semibold">{deals?.length ?? 0}</span> great deals
                  </p>
                </div>
                
                <div className="space-y-6">
                  {deals.map((deal, index) => (
                    <Link
                      key={`${deal.product_key}_${index}`}
                      href={`/products/${deal.product_key}`}
                      className="block bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-200 group"
                    >
                      <div className="flex flex-col md:flex-row">
                        {/* Image */}
                        <div className="relative md:w-64 aspect-square md:aspect-auto bg-gray-50">
                          {deal.image_url ? (
                            <Image
                              src={deal.image_url}
                              alt={deal.model || 'Product'}
                              fill
                              className="object-contain p-4 group-hover:scale-105 transition-transform duration-300"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                                if (target.nextElementSibling) {
                                  (target.nextElementSibling as HTMLElement).style.display = 'flex';
                                }
                              }}
                            />
                          ) : null}
                          <div className={`flex items-center justify-center h-full text-gray-400 ${deal.image_url ? 'hidden' : ''}`}>
                            <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                          </div>
                          
                          {/* Rank Badge */}
                          <div className="absolute top-4 left-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                            #{index + 1}
                          </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 p-6">
                          <div className="flex flex-col h-full">
                            {/* Product Info */}
                            <div className="mb-4">
                              <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-2">
                                {deal.brand}
                              </p>
                              <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                                {deal.model}
                              </h3>
                            </div>

                            {/* Savings Banner */}
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-500 rounded-lg p-4 mb-4">
                              <div className="flex items-center justify-between flex-wrap gap-4">
                                <div>
                                  <p className="text-xs text-green-700 font-semibold uppercase tracking-wide mb-1">
                                    Save up to
                                  </p>
                                  <p className="text-3xl font-bold text-green-700">
                                    {deal.price_difference.toFixed(2)} TND
                                  </p>
                                  <p className="text-sm text-green-600 mt-1">
                                    That's {deal.savings_percent.toFixed(0)}% off!
                                  </p>
                                </div>
                                <div className="bg-white rounded-full px-6 py-3 shadow-md">
                                  <p className="text-xs text-gray-500 mb-1">Best Price</p>
                                  <p className="text-2xl font-bold text-gray-900">
                                    {deal.lowest_price.toFixed(2)}
                                    <span className="text-sm font-normal text-gray-600 ml-1">TND</span>
                                  </p>
                                </div>
                              </div>
                            </div>

                            {/* Store Comparison */}
                            <div className="grid grid-cols-2 gap-4 mt-auto">
                              <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                                <div className="flex items-center gap-2 mb-2">
                                  <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <p className="text-xs text-green-700 font-semibold uppercase">Best Store</p>
                                </div>
                                <p className="font-semibold text-gray-900 truncate">{deal.lowest_store}</p>
                                <p className="text-lg font-bold text-green-700 mt-1">
                                  {deal.lowest_price.toFixed(2)} TND
                                </p>
                              </div>
                              
                              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                                <div className="flex items-center gap-2 mb-2">
                                  <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <p className="text-xs text-red-700 font-semibold uppercase">Highest</p>
                                </div>
                                <p className="font-semibold text-gray-900 truncate">{deal.highest_store}</p>
                                <p className="text-lg font-bold text-red-700 mt-1">
                                  {deal.highest_price.toFixed(2)} TND
                                </p>
                              </div>
                            </div>

                            {/* Card is already clickable via Link */}
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-12 flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-gray-900"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <span className="px-6 py-2 bg-white border border-gray-300 rounded-lg font-semibold text-gray-900">
                  {page} / {totalPages}
                </span>
                
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-gray-900"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
          </>
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

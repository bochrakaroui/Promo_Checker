'use client';

import { useEffect, useState } from 'react';
import AppHeader from '@/components/AppHeader';
import ProductCard from '@/components/ProductCard';
import { getBrands, getProducts } from '@/lib/api';
import {
  recommendProducts,
  useCaseDefaults,
  type ScoredRecommendation,
  type UseCase,
} from '@/lib/recommender';

const useCases: Array<{ value: UseCase; label: string; description: string }> = [
  { value: 'everyday', label: 'Everyday', description: 'Browsing, email and streaming' },
  { value: 'study', label: 'Study', description: 'Research, classes and assignments' },
  { value: 'business', label: 'Business', description: 'Office work and multitasking' },
  { value: 'programming', label: 'Programming', description: 'Development tools and local apps' },
  { value: 'creative', label: 'Creative work', description: 'Design, photo and video work' },
  { value: 'gaming', label: 'Gaming', description: 'Games and graphics-heavy apps' },
];

export default function IntelligentHelpPage() {
  const [budget, setBudget] = useState(2500);
  const [useCase, setUseCase] = useState<UseCase>('study');
  const [brand, setBrand] = useState('');
  const [minRam, setMinRam] = useState(8);
  const [minStorage, setMinStorage] = useState(256);
  const [brands, setBrands] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<ScoredRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getBrands().then(setBrands).catch((err) => console.error('Failed to load brands', err));
  }, []);

  const selectUseCase = (nextUseCase: UseCase) => {
    const defaults = useCaseDefaults[nextUseCase];
    setUseCase(nextUseCase);
    setMinRam(defaults.ram);
    setMinStorage(defaults.storage);
  };

  const findMatches = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setHasSubmitted(true);
    setError(null);

    try {
      const firstPage = await getProducts(
        1,
        100,
        'price',
        'asc',
        undefined,
        brand || undefined,
      );
      const remainingPages = firstPage.total_pages > 1
        ? await Promise.all(
            Array.from({ length: firstPage.total_pages - 1 }, (_, index) =>
              getProducts(index + 2, 100, 'price', 'asc', undefined, brand || undefined),
            ),
          )
        : [];
      const candidates = [firstPage, ...remainingPages].flatMap((page) => page.items);

      setRecommendations(recommendProducts(candidates, {
        budget,
        useCase,
        brand,
        minRam,
        minStorage,
      }));
    } catch (err) {
      console.error(err);
      setRecommendations([]);
      setError('We could not analyze the current products. Please check that the backend is running and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-teal-50 to-blue-50">
      <AppHeader />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-700 via-teal-600 to-cyan-600 px-6 py-10 text-white shadow-xl sm:px-10 lg:px-14">
          <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/10" />
          <div className="absolute -bottom-24 right-40 h-48 w-48 rounded-full bg-cyan-300/10" />
          <div className="relative max-w-3xl">
            <span className="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-sm font-semibold ring-1 ring-white/25">
              Smart laptop finder
            </span>
            <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">Get Intelligent Help</h1>
            <p className="mt-4 max-w-2xl text-lg leading-8 text-teal-50">
              Tell us what matters to you. We will rank live deals by budget, performance, memory, storage and value—then explain every match.
            </p>
          </div>
        </section>

        <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,420px)_1fr] lg:items-start">
          <form onSubmit={findMatches} className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:sticky lg:top-6">
            <div className="mb-6">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-teal-700">Your preferences</p>
              <h2 className="mt-2 text-2xl font-bold text-gray-900">What are you looking for?</h2>
            </div>

            <label className="block text-sm font-semibold text-gray-800" htmlFor="budget">Maximum budget</label>
            <div className="relative mt-2">
              <input
                id="budget"
                type="number"
                min="300"
                step="50"
                required
                value={budget}
                onChange={(event) => setBudget(Number(event.target.value))}
                className="w-full rounded-xl border border-gray-300 px-4 py-3 pr-16 text-gray-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-gray-500">TND</span>
            </div>

            <fieldset className="mt-6">
              <legend className="text-sm font-semibold text-gray-800">Main use</legend>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {useCases.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => selectUseCase(option.value)}
                    className={`rounded-xl border p-3 text-left transition ${
                      useCase === option.value
                        ? 'border-teal-500 bg-teal-50 ring-2 ring-teal-100'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <span className="block text-sm font-semibold text-gray-900">{option.label}</span>
                    <span className="mt-1 block text-xs leading-4 text-gray-500">{option.description}</span>
                  </button>
                ))}
              </div>
            </fieldset>

            <label className="mt-6 block text-sm font-semibold text-gray-800" htmlFor="preferred-brand">Preferred brand</label>
            <select
              id="preferred-brand"
              value={brand}
              onChange={(event) => setBrand(event.target.value)}
              className="mt-2 w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
            >
              <option value="">No preference</option>
              {brands.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-800" htmlFor="minimum-ram">Minimum RAM</label>
                <select
                  id="minimum-ram"
                  value={minRam}
                  onChange={(event) => setMinRam(Number(event.target.value))}
                  className="mt-2 w-full rounded-xl border border-gray-300 bg-white px-3 py-3 text-gray-900 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                >
                  {[4, 8, 16, 32].map((value) => <option key={value} value={value}>{value} GB</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-800" htmlFor="minimum-storage">Minimum storage</label>
                <select
                  id="minimum-storage"
                  value={minStorage}
                  onChange={(event) => setMinStorage(Number(event.target.value))}
                  className="mt-2 w-full rounded-xl border border-gray-300 bg-white px-3 py-3 text-gray-900 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-200"
                >
                  {[128, 256, 512, 1024].map((value) => <option key={value} value={value}>{value} GB</option>)}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || budget <= 0}
              className="mt-7 flex w-full items-center justify-center gap-2 rounded-xl bg-teal-600 px-5 py-3.5 font-bold text-white shadow-sm transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Analyzing products…' : 'Find my best matches'}
              {!loading && (
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              )}
            </button>
          </form>

          <section aria-live="polite">
            {!hasSubmitted && (
              <div className="rounded-2xl border border-dashed border-teal-300 bg-white/70 px-6 py-16 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-teal-100 text-teal-700">
                  <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9.663 17h4.674M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.05 9.032a6 6 0 118.628 0c-.89.817-1.314 1.487-1.314 2.332H9c0-.845-.424-1.515-1.314-2.332z" />
                  </svg>
                </div>
                <h2 className="mt-5 text-2xl font-bold text-gray-900">Your shortlist will appear here</h2>
                <p className="mx-auto mt-2 max-w-md text-gray-600">Complete the preferences and we will compare the catalog for you.</p>
              </div>
            )}

            {loading && (
              <div className="flex min-h-80 items-center justify-center rounded-2xl border border-gray-200 bg-white">
                <div className="text-center">
                  <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-teal-100 border-t-teal-600" />
                  <p className="mt-4 font-medium text-gray-600">Scoring the best available laptops…</p>
                </div>
              </div>
            )}

            {!loading && error && (
              <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-800">{error}</div>
            )}

            {!loading && !error && hasSubmitted && recommendations.length === 0 && (
              <div className="rounded-2xl border border-gray-200 bg-white px-6 py-16 text-center">
                <h2 className="text-2xl font-bold text-gray-900">No matches found</h2>
                <p className="mt-2 text-gray-600">Try another brand or adjust your preferences.</p>
              </div>
            )}

            {!loading && recommendations.length > 0 && (
              <div>
                <div className="mb-5">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-teal-700">Personalized shortlist</p>
                  <h2 className="mt-2 text-3xl font-bold text-gray-900">Your top {recommendations.length} matches</h2>
                  <p className="mt-2 text-gray-600">Ranked against your budget and selected requirements.</p>
                </div>
                <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                  {recommendations.map((recommendation, index) => (
                    <article key={recommendation.product.product_key} className="flex flex-col">
                      <div className="mb-3 flex items-center justify-between rounded-xl bg-gray-900 px-4 py-3 text-white">
                        <span className="font-bold">#{index + 1} recommendation</span>
                        <span className="rounded-full bg-teal-400/20 px-3 py-1 text-sm font-bold text-teal-200">{recommendation.score}% match</span>
                      </div>
                      <div className="mb-3 flex-1 rounded-xl border border-teal-100 bg-teal-50 p-4">
                        <p className="text-xs font-bold uppercase tracking-wide text-teal-800">Why it fits</p>
                        <ul className="mt-2 space-y-1.5 text-sm text-gray-700">
                          {recommendation.reasons.map((reason) => (
                            <li key={reason} className="flex gap-2">
                              <span className="text-teal-600">✓</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <ProductCard product={recommendation.product} />
                    </article>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

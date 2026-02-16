'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { getProductDetail } from '@/lib/api';
import type { ProductDetail } from '@/lib/types';

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const productKey = params.productKey as string;
  
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProduct();
  }, [productKey]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getProductDetail(productKey);
      setProduct(data);
    } catch (err) {
      setError('Failed to load product details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-teal-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl mb-4">{error || 'Product not found'}</p>
          <button 
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors"
          >
            Back to Products
          </button>
        </div>
      </div>
    );
  }

  const pricesByStore = product.price_history.reduce((acc, price) => {
    if (!acc[price.store_name] || new Date(price.date) > new Date(acc[price.store_name].date)) {
      acc[price.store_name] = price;
    }
    return acc;
  }, {} as Record<string, typeof product.price_history[0]>);

  const currentPrices = Object.values(pricesByStore).sort((a, b) => a.price - b.price);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-teal-50">
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
              <a href="/stores" className="text-gray-600 hover:text-gray-900 transition-colors">
                Stores
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button 
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to all products
        </button>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Image and Basic Info */}
          <div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              {/* Image */}
              <div className="relative aspect-square bg-gray-50 rounded-lg overflow-hidden mb-6">
                {product.image_url ? (
                  <Image
                    src={product.image_url}
                    alt={product.model}
                    fill
                    className="object-contain p-4"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      if (target.nextElementSibling) {
                        (target.nextElementSibling as HTMLElement).style.display = 'flex';
                      }
                    }}
                  />
                ) : null}
                <div className={`flex items-center justify-center h-full text-gray-400 ${product.image_url ? 'hidden' : ''}`}>
                  <svg className="w-32 h-32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>

              {/* Brand and Model */}
              <p className="text-sm font-semibold text-teal-600 uppercase tracking-wide mb-2">
                {product.brand}
              </p>
              <h1 className="text-2xl font-bold text-gray-900 mb-6">
                {product.model}
              </h1>

              {/* Specifications */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 text-lg">Specifications</h3>
                <div className="grid grid-cols-2 gap-4">
                  {product.cpu_type && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Processor</span>
                      <span className="text-sm font-medium text-gray-900">{product.cpu_type}</span>
                    </div>
                  )}
                  {product.ram_size && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">RAM</span>
                      <span className="text-sm font-medium text-gray-900">{product.ram_size}</span>
                    </div>
                  )}
                  {product.storage_capacity && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Storage</span>
                      <span className="text-sm font-medium text-gray-900">{product.storage_capacity}</span>
                    </div>
                  )}
                  {product.display_size && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Display</span>
                      <span className="text-sm font-medium text-gray-900">{product.display_size}</span>
                    </div>
                  )}
                  {product.graphics_card && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Graphics</span>
                      <span className="text-sm font-medium text-gray-900">{product.graphics_card}</span>
                    </div>
                  )}
                  {product.operating_system && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">OS</span>
                      <span className="text-sm font-medium text-gray-900">{product.operating_system}</span>
                    </div>
                  )}
                  {product.display_technology && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Display Tech</span>
                      <span className="text-sm font-medium text-gray-900">{product.display_technology}</span>
                    </div>
                  )}
                  {product.color && (
                    <div className="flex flex-col">
                      <span className="text-xs text-gray-500 uppercase tracking-wide mb-1">Color</span>
                      <span className="text-sm font-medium text-gray-900">{product.color}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Prices and Comparison */}
          <div>
            {/* Price Summary */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Price Comparison</h2>
              
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="text-xs text-green-600 font-semibold uppercase tracking-wide mb-2">Best Price</p>
                  <p className="text-3xl font-bold text-green-700">
                    {product.lowest_price.toFixed(2)}
                    <span className="text-lg font-normal text-green-600 ml-2">TND</span>
                  </p>
                </div>
                
                {product.highest_price > product.lowest_price && (
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide mb-2">Highest Price</p>
                    <p className="text-3xl font-bold text-gray-700">
                      {product.highest_price.toFixed(2)}
                      <span className="text-lg font-normal text-gray-600 ml-2">TND</span>
                    </p>
                  </div>
                )}
              </div>

              {product.highest_price > product.lowest_price && (
                <div className="bg-teal-50 rounded-lg p-4 border border-teal-200 mb-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-teal-900">Potential Savings</span>
                    <span className="text-2xl font-bold text-teal-700">
                      {(product.highest_price - product.lowest_price).toFixed(2)} TND
                    </span>
                  </div>
                  <p className="text-xs text-teal-600 mt-2">
                    Save up to {Math.round(((product.highest_price - product.lowest_price) / product.highest_price) * 100)}% by choosing the best store
                  </p>
                </div>
              )}

              <p className="text-xs text-gray-500 text-center">
                Available in {product.store_count} store{product.store_count !== 1 ? 's' : ''}
              </p>
            </div>

            {/* Store Prices */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Where to Buy</h3>
              <div className="space-y-3">
                {currentPrices.map((price, index) => (
                  <div 
                    key={price.store_name}
                    className={`flex items-center justify-between p-4 rounded-lg border-2 transition-all ${
                      index === 0 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {index === 0 && (
                        <div className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded">
                          BEST
                        </div>
                      )}
                      <div>
                        <p className="font-semibold text-gray-900">{price.store_name}</p>
                        <p className="text-xs text-gray-500">
                          Updated {new Date(price.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-xl font-bold ${index === 0 ? 'text-green-700' : 'text-gray-900'}`}>
                        {price.price.toFixed(2)} TND
                      </p>
                      {index > 0 && (
                        <p className="text-xs text-red-600">
                          +{(price.price - currentPrices[0].price).toFixed(2)} TND
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

import Link from 'next/link';
import type { ProductSummary } from '@/lib/types';

interface ProductCardProps {
  product: ProductSummary;
}

export default function ProductCard({ product }: ProductCardProps) {
  const savingsPercent = product.highest_price > 0 
    ? Math.round(((product.highest_price - product.lowest_price) / product.highest_price) * 100)
    : 0;

  return (
    <Link 
      href={`/products/${product.product_key}`}
      className="group block bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
    >
      {/* Image Section */}
      <div className="relative aspect-square bg-gray-50 overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.model || 'Product image'}
            className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              const target = e.currentTarget;
              target.style.display = 'none';
              const parent = target.parentElement;
              if (parent) {
                const placeholder = parent.querySelector('.image-placeholder');
                if (placeholder) {
                  (placeholder as HTMLElement).classList.remove('hidden');
                }
              }
            }}
          />
        ) : null}
        <div className={`image-placeholder flex items-center justify-center h-full text-gray-400 ${product.image_url ? 'hidden' : ''}`}>
          <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        
        {/* Savings Badge */}
        {savingsPercent > 0 && (
          <div className="absolute top-3 right-3 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
            -{savingsPercent}%
          </div>
        )}
        
        {/* Store Count Badge */}
        {product.store_count > 1 && (
          <div className="absolute top-3 left-3 bg-teal-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
            {product.store_count} stores
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-5">
        {/* Brand */}
        <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide mb-1">
          {product.brand}
        </p>
        
        {/* Product Name */}
        <h3 className="text-base font-semibold text-gray-900 mb-3 line-clamp-2 group-hover:text-teal-600 transition-colors">
          {product.model}
        </h3>
        
        {/* Specs */}
        <div className="space-y-1 mb-4 text-xs text-gray-600">
          {product.cpu_type && (
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              <span className="truncate">{product.cpu_type}</span>
            </div>
          )}
          {product.ram_size && (
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              <span>{product.ram_size} RAM</span>
            </div>
          )}
          {product.storage_capacity && (
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
              <span>{product.storage_capacity}</span>
            </div>
          )}
        </div>
        
        {/* Price Section */}
        <div className="border-t border-gray-100 pt-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs text-gray-500 mb-1">Best Price</p>
              <p className="text-2xl font-bold text-gray-900">
                {product.lowest_price.toFixed(2)}
                <span className="text-sm font-normal text-gray-500 ml-1">TND</span>
              </p>
              {product.highest_price > product.lowest_price && (
                <p className="text-xs text-gray-400 line-through mt-1">
                  {product.highest_price.toFixed(2)} TND
                </p>
              )}
            </div>
            
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-1">at</p>
              <p className="text-sm font-semibold text-blue-600 truncate max-w-[120px]">
                {product.best_store}
              </p>
            </div>
          </div>
        </div>
        
        {/* View Details Button */}
        <button className="mt-4 w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2">
          View Details
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </Link>
  );
}
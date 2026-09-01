// API service layer for communicating with FastAPI backend

import type { 
  ProductSummary, 
  PaginatedResponse, 
  ProductDetail, 
  Deal,
  Store 
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Generic fetch wrapper with error handling
async function fetchAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

// Products API
export async function getProducts(
  page: number = 1,
  pageSize: number = 20,
  sortBy: string = 'lowest_price',
  sortOrder: 'asc' | 'desc' = 'asc',
  search?: string,
  brand?: string,
  minPrice?: number,
  maxPrice?: number,
  minRam?: number,
  minStorage?: number,
  cpuType?: string
): Promise<PaginatedResponse<ProductSummary>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    sort_by: sortBy,
    sort_order: sortOrder,
  });
  
  if (search) params.append('search', search);
  if (brand) params.append('brand', brand);
  if (minPrice !== undefined) params.append('min_price', minPrice.toString());
  if (maxPrice !== undefined) params.append('max_price', maxPrice.toString());
  if (minRam !== undefined) params.append('min_ram', minRam.toString());
  if (minStorage !== undefined) params.append('min_storage', minStorage.toString());
  if (cpuType) params.append('cpu_type', cpuType);
  
  return fetchAPI<PaginatedResponse<ProductSummary>>(`/api/products?${params}`);
}

export async function getBrands(): Promise<string[]> {
  return fetchAPI<string[]>('/api/products/filters/brands');
}

export async function getProductDetail(productKey: string): Promise<ProductDetail> {
  return fetchAPI<ProductDetail>(`/api/products/${productKey}`);
}

// Deals API
export async function getDeals(
  minDifference: number = 100,
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedResponse<Deal>> {
  const params = new URLSearchParams({
    min_difference: minDifference.toString(),
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  
  return fetchAPI<PaginatedResponse<Deal>>(`/api/deals?${params}`);
}

// Stores API
export async function getStores(): Promise<Store[]> {
  return fetchAPI<Store[]>('/api/stores');
}

export async function getStoreDetails(storeName: string): Promise<Store> {
  return fetchAPI<Store>(`/api/stores/${storeName}`);
}

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
  brand?: string
): Promise<PaginatedResponse<ProductSummary>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
    sort_by: sortBy,
    sort_order: sortOrder,
  });
  
  if (search) params.append('search', search);
  if (brand) params.append('brand', brand);
  
  return fetchAPI<PaginatedResponse<ProductSummary>>(`/api/products?${params}`);
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

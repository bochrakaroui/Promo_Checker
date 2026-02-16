// TypeScript types matching the FastAPI backend models

export interface ProductSummary {
  product_key: string;
  model: string;
  brand: string;
  lowest_price: number;
  highest_price: number;
  store_count: number;
  best_store: string;
  image_url: string | null;
  cpu_type: string | null;
  ram_size: string | null;
  storage_capacity: string | null;
  display_size: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PriceHistory {
  date: string;
  price: number;
  store_name: string;
}

export interface ProductListing {
  store_name: string;
  final_price: number | null;
  original_price: number | null;
  discount_percentage: number | null;
  product_url: string;
  image_url: string | null;
  availability: string | null;
  scraped_at: string; // ISO datetime
}

export interface ProductDetail {
  product_key: string;
  model: string;
  brand: string;
  cpu_type: string | null;
  ram_size: string | null;
  storage_capacity: string | null;
  display_size: string | null;
  display_technology: string | null;
  graphics_card: string | null;
  operating_system: string | null;
  color: string | null;
  lowest_price: number;
  highest_price: number;
  store_count: number;
  image_url: string | null;
  listings: ProductListing[];
  // Optional: some backends may return this; keep for compatibility
  price_history?: PriceHistory[];
}

export interface Deal {
  product_key: string;
  model: string;
  brand: string;
  lowest_price: number;
  highest_price: number;
  price_difference: number;
  savings_percent: number;
  lowest_store: string;
  highest_store: string;
  image_url: string | null;
}

export interface Store {
  store_name: string;
  base_url: string;
  product_count: number;
  avg_price: number;
  min_price: number;
  max_price: number;
}

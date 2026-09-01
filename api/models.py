"""
PromoChecker API - Pydantic Models
Data validation and serialization models
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== Product Models ====================

class ProductSpecs(BaseModel):
    """Product specifications"""
    brand: Optional[str] = None
    model: Optional[str] = None
    cpu_type: Optional[str] = None
    cpu_generation: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None


class ProductBase(BaseModel):
    """Base product information"""
    product_key: str
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    cpu_type: Optional[str] = None
    cpu_generation: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None


class ProductListing(BaseModel):
    """Product listing at a specific store"""
    store_name: str
    final_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    product_url: str
    image_url: Optional[str] = None
    availability: Optional[str] = None
    scraped_at: datetime


class ProductDetail(ProductBase):
    """Detailed product with all store listings"""
    listings: List[ProductListing] = []
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    store_count: int = 0
    image_url: Optional[str] = None


class ProductSummary(ProductBase):
    """Product summary for list views"""
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    store_count: int = 0
    best_store: Optional[str] = None
    image_url: Optional[str] = None


# ==================== Price Models ====================

class PriceHistory(BaseModel):
    """Historical price point"""
    store_name: str
    final_price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    scraped_at: datetime


class PriceComparison(BaseModel):
    """Price comparison across stores"""
    product_key: str
    product_name: str
    stores: List[ProductListing]
    lowest_price: float
    highest_price: float
    price_difference: float
    savings_percentage: float


# ==================== Deal Models ====================

class Deal(BaseModel):
    """Best deal (multi-store product with price difference)"""
    product_key: str
    brand: Optional[str] = None
    model: Optional[str] = None
    cpu_type: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    store_count: int
    lowest_price: float
    lowest_store: str
    highest_price: float
    highest_store: str
    price_difference: float
    savings_percent: float
    image_url: Optional[str] = None


# ==================== Search & Filter Models ====================

class ProductFilters(BaseModel):
    """Filters for product search"""
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_ram: Optional[int] = None
    min_storage: Optional[int] = None
    cpu_type: Optional[str] = None
    store: Optional[str] = None
    search: Optional[str] = None  # Search in product name
    sort_by: Optional[str] = "price"  # price, name, brand
    sort_order: Optional[str] = "asc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated API response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ProductSummary]


# ==================== Store Models ====================

class Store(BaseModel):
    """Store information"""
    store_id: int
    store_name: str
    base_url: Optional[str] = None
    product_count: int = 0
    avg_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


# ==================== Stats Models ====================

class APIStats(BaseModel):
    """API statistics"""
    total_products: int
    total_listings: int
    total_prices: int
    total_stores: int
    multi_store_products: int
    cheapest_product: Optional[ProductSummary] = None
    best_deal: Optional[Deal] = None

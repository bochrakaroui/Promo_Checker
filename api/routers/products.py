"""
PromoChecker API - Products Router
Endpoints for product search, filters, and details
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from api.database import get_db_cursor
from api.models import ProductSummary, ProductDetail, ProductListing, PaginatedResponse, ProductFilters
import math

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedResponse)
async def get_products(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_ram: Optional[int] = Query(None, description="Minimum RAM (GB)"),
    min_storage: Optional[int] = Query(None, description="Minimum storage (GB)"),
    cpu_type: Optional[str] = Query(None, description="CPU type (e.g., i5, i7, ryzen5)"),
    store: Optional[str] = Query(None, description="Filter by store"),
    search: Optional[str] = Query(None, description="Search in product name"),
    sort_by: str = Query("price", description="Sort by: price, name, brand"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Get paginated list of products with filters
    
    - **brand**: Filter by brand (dell, hp, lenovo, etc.)
    - **min_price/max_price**: Price range
    - **min_ram/min_storage**: Minimum specs
    - **cpu_type**: Filter by CPU type
    - **store**: Show only products from specific store
    - **search**: Search in product name
    - **sort_by**: Sort by price, name, or brand
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (max 100)
    """
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if brand:
        where_conditions.append("p.brand ILIKE %s")
        params.append(f"%{brand}%")
    
    if min_price is not None:
        where_conditions.append("cbp.final_price >= %s")
        params.append(min_price)
    
    if max_price is not None:
        where_conditions.append("cbp.final_price <= %s")
        params.append(max_price)
    
    if min_ram is not None:
        where_conditions.append("p.ram_gb >= %s")
        params.append(min_ram)
    
    if min_storage is not None:
        where_conditions.append("p.storage_gb >= %s")
        params.append(min_storage)
    
    if cpu_type:
        where_conditions.append("p.cpu_type ILIKE %s")
        params.append(f"%{cpu_type}%")
    
    if store:
        where_conditions.append("cbp.store_name ILIKE %s")
        params.append(f"%{store}%")
    
    if search:
        where_conditions.append("p.name ILIKE %s")
        params.append(f"%{search}%")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Sort validation
    valid_sort_fields = {"price": "ps.lowest_price", "name": "p.name", "brand": "p.brand"}
    sort_field = valid_sort_fields.get(sort_by, "ps.lowest_price")
    sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
    
    # Count total products
    with get_db_cursor() as cursor:
        count_query = f"""
            SELECT COUNT(DISTINCT p.product_key) as total
            FROM products p
            JOIN current_best_prices cbp ON p.product_key = cbp.product_key
            WHERE {where_clause} AND cbp.final_price IS NOT NULL
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Calculate pagination
        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        # Get products with best price per product
        query = f"""
            WITH product_stats AS (
                SELECT 
                    cbp.product_key,
                    MIN(cbp.final_price) as lowest_price,
                    COUNT(DISTINCT cbp.store_name) as store_count,
                    (ARRAY_AGG(cbp.store_name ORDER BY cbp.final_price ASC))[1] as best_store
                FROM current_best_prices cbp
                WHERE cbp.final_price IS NOT NULL
                GROUP BY cbp.product_key
            ),
            product_images AS (
                SELECT DISTINCT ON (pl.product_key)
                    pl.product_key,
                    pl.image_url
                FROM product_listings pl
                WHERE pl.image_url IS NOT NULL
                ORDER BY pl.product_key, pl.listing_id
            )
            SELECT DISTINCT
                p.product_key,
                p.name,
                p.brand,
                p.model,
                p.cpu_type,
                p.cpu_generation,
                p.ram_gb,
                p.storage_gb,
                ps.lowest_price,
                ps.store_count,
                ps.best_store,
                pi.image_url
            FROM products p
            JOIN product_stats ps ON p.product_key = ps.product_key
            JOIN current_best_prices cbp ON p.product_key = cbp.product_key
            LEFT JOIN product_images pi ON p.product_key = pi.product_key
            WHERE {where_clause} AND cbp.final_price IS NOT NULL
            ORDER BY {sort_field} {sort_direction}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [page_size, offset])
        products = cursor.fetchall()
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[ProductSummary(**product) for product in products]
    )


@router.get("/{product_key}", response_model=ProductDetail)
async def get_product_detail(product_key: str):
    """
    Get detailed information for a specific product
    
    Includes:
    - Product specifications
    - All store listings with current prices
    - Price comparison across stores
    """
    
    with get_db_cursor() as cursor:
        # Get product info
        cursor.execute("""
            SELECT * FROM products WHERE product_key = %s
        """, (product_key,))
        
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get all listings with latest prices
        cursor.execute("""
            SELECT 
                s.store_name,
                pr.final_price,
                pr.original_price,
                pr.discount_percentage,
                pl.product_url,
                pl.image_url,
                pl.availability,
                pr.scraped_at
            FROM product_listings pl
            JOIN stores s ON pl.store_id = s.store_id
            JOIN LATERAL (
                SELECT final_price, original_price, discount_percentage, scraped_at
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON true
            WHERE pl.product_key = %s
            ORDER BY pr.final_price ASC NULLS LAST
        """, (product_key,))
        
        listings = cursor.fetchall()
        
        # Calculate price stats
        prices = [l['final_price'] for l in listings if l['final_price'] is not None]
        lowest_price = min(prices) if prices else None
        highest_price = max(prices) if prices else None
        
        # Get image_url from listing with lowest price, or first available
        image_url = None
        if listings:
            # Try to get image from listing with lowest price
            sorted_listings = sorted(
                [l for l in listings if l['final_price'] is not None],
                key=lambda x: x['final_price']
            )
            if sorted_listings:
                image_url = sorted_listings[0].get('image_url')
            # Fallback to any listing with image_url
            if not image_url:
                for listing in listings:
                    if listing.get('image_url'):
                        image_url = listing['image_url']
                        break
        
        return ProductDetail(
            **product,
            listings=[ProductListing(**listing) for listing in listings],
            lowest_price=lowest_price,
            highest_price=highest_price,
            store_count=len(listings),
            image_url=image_url
        )


@router.get("/{product_key}/stores", response_model=List[ProductListing])
async def get_product_stores(product_key: str):
    """
    Get all store listings for a product (price comparison)
    """
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.store_name,
                pr.final_price,
                pr.original_price,
                pr.discount_percentage,
                pl.product_url,
                pl.image_url,
                pl.availability,
                pr.scraped_at
            FROM product_listings pl
            JOIN stores s ON pl.store_id = s.store_id
            JOIN LATERAL (
                SELECT final_price, original_price, discount_percentage, scraped_at
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON true
            WHERE pl.product_key = %s
            ORDER BY pr.final_price ASC NULLS LAST
        """, (product_key,))
        
        listings = cursor.fetchall()
        
        if not listings:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return [ProductListing(**listing) for listing in listings]

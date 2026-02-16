"""
PromoChecker API - Deals Router
Endpoints for best deals and price comparisons
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from api.database import get_db_cursor
from api.models import Deal

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("/", response_model=List[Deal])
async def get_best_deals(
    min_savings: Optional[float] = Query(None, ge=0, description="Minimum savings in TND"),
    min_savings_percent: Optional[float] = Query(None, ge=0, le=100, description="Minimum savings percentage"),
    limit: int = Query(20, ge=1, le=100, description="Number of deals to return")
):
    """
    Get the best deals across multiple stores
    
    - **min_savings**: Minimum price difference in TND (optional)
    - **min_savings_percent**: Minimum savings percentage (optional)
    - **limit**: Number of deals to return (default: 20, max: 100)
    
    Returns products with the biggest price differences between stores
    """
    
    with get_db_cursor() as cursor:
        # Build dynamic HAVING clause
        having_conditions = []
        params = []
        
        if min_savings is not None:
            having_conditions.append("(pr_high.final_price - pr_low.final_price) >= %s")
            params.append(min_savings)
        
        if min_savings_percent is not None:
            having_conditions.append("((pr_high.final_price - pr_low.final_price) / pr_high.final_price * 100) >= %s")
            params.append(min_savings_percent)
        
        having_clause = " AND " + " AND ".join(having_conditions) if having_conditions else ""
        
        query = f"""
            SELECT 
                p.product_key,
                p.brand,
                p.model,
                p.cpu_type,
                p.ram_gb,
                p.storage_gb,
                s_low.store_name as lowest_store,
                pr_low.final_price as lowest_price,
                s_high.store_name as highest_store,
                pr_high.final_price as highest_price,
                (pr_high.final_price - pr_low.final_price) as price_difference,
                ROUND(((pr_high.final_price - pr_low.final_price) / pr_high.final_price * 100)::numeric, 2) as savings_percent,
                COUNT(DISTINCT pl.store_id) as store_count,
                pl_low.image_url
            FROM products p
            -- Get lowest price store
            JOIN product_listings pl_low ON p.product_key = pl_low.product_key
            JOIN stores s_low ON pl_low.store_id = s_low.store_id
            JOIN LATERAL (
                SELECT final_price, scraped_at
                FROM prices
                WHERE listing_id = pl_low.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr_low ON pr_low.final_price = (
                SELECT MIN(pr2.final_price)
                FROM product_listings pl2
                JOIN prices pr2 ON pl2.listing_id = pr2.listing_id
                WHERE pl2.product_key = p.product_key
                  AND pr2.price_id = (
                      SELECT price_id FROM prices 
                      WHERE listing_id = pl2.listing_id 
                      ORDER BY scraped_at DESC 
                      LIMIT 1
                  )
            )
            -- Get highest price store
            JOIN product_listings pl_high ON p.product_key = pl_high.product_key
            JOIN stores s_high ON pl_high.store_id = s_high.store_id
            JOIN LATERAL (
                SELECT final_price, scraped_at
                FROM prices
                WHERE listing_id = pl_high.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr_high ON pr_high.final_price = (
                SELECT MAX(pr2.final_price)
                FROM product_listings pl2
                JOIN prices pr2 ON pl2.listing_id = pr2.listing_id
                WHERE pl2.product_key = p.product_key
                  AND pr2.price_id = (
                      SELECT price_id FROM prices 
                      WHERE listing_id = pl2.listing_id 
                      ORDER BY scraped_at DESC 
                      LIMIT 1
                  )
            )
            -- Count stores
            JOIN product_listings pl ON p.product_key = pl.product_key
            WHERE pr_low.final_price < pr_high.final_price
            GROUP BY 
                p.product_key, p.brand, p.model, p.cpu_type, p.ram_gb, p.storage_gb,
                s_low.store_name, pr_low.final_price,
                s_high.store_name, pr_high.final_price,
                pl_low.image_url
            HAVING 1=1{having_clause}
            ORDER BY price_difference DESC
            LIMIT %s
        """
        
        params.append(limit)
        cursor.execute(query, params)
        
        deals = cursor.fetchall()
        
        if not deals:
            raise HTTPException(
                status_code=404, 
                detail="No deals found matching the criteria"
            )
        
        return [Deal(**record) for record in deals]


@router.get("/top-discounts", response_model=List[dict])
async def get_top_discounts(
    limit: int = Query(20, ge=1, le=100, description="Number of deals to return")
):
    """
    Get products with the highest discount percentages (single store deals)
    """
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.product_key,
                p.brand,
                p.model,
                p.cpu_type,
                p.ram_gb,
                p.storage_gb,
                s.store_name,
                pr.final_price,
                pr.original_price,
                pr.discount_percentage
            FROM products p
            JOIN product_listings pl ON p.product_key = pl.product_key
            JOIN stores s ON pl.store_id = s.store_id
            JOIN LATERAL (
                SELECT final_price, original_price, discount_percentage
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON pr.discount_percentage > 0
            WHERE pr.original_price IS NOT NULL 
              AND pr.discount_percentage IS NOT NULL
            ORDER BY pr.discount_percentage DESC
            LIMIT %s
        """, (limit,))
        
        discounts = cursor.fetchall()
        
        if not discounts:
            raise HTTPException(status_code=404, detail="No discounts found")
        
        return discounts


@router.get("/by-brand/{brand}", response_model=List[Deal])
async def get_deals_by_brand(
    brand: str,
    limit: int = Query(20, ge=1, le=100, description="Number of deals to return")
):
    """
    Get best deals for a specific brand
    """
    
    with get_db_cursor() as cursor:
        query = """
            SELECT 
                p.product_key,
                p.brand,
                p.model,
                p.cpu_type,
                p.ram_gb,
                p.storage_gb,
                s_low.store_name as lowest_store,
                pr_low.final_price as lowest_price,
                s_high.store_name as highest_store,
                pr_high.final_price as highest_price,
                (pr_high.final_price - pr_low.final_price) as price_difference,
                ROUND(((pr_high.final_price - pr_low.final_price) / pr_high.final_price * 100)::numeric, 2) as savings_percent,
                COUNT(DISTINCT pl.store_id) as store_count,
                pl_low.image_url
            FROM products p
            JOIN product_listings pl_low ON p.product_key = pl_low.product_key
            JOIN stores s_low ON pl_low.store_id = s_low.store_id
            JOIN LATERAL (
                SELECT final_price, scraped_at
                FROM prices
                WHERE listing_id = pl_low.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr_low ON pr_low.final_price = (
                SELECT MIN(pr2.final_price)
                FROM product_listings pl2
                JOIN prices pr2 ON pl2.listing_id = pr2.listing_id
                WHERE pl2.product_key = p.product_key
                  AND pr2.price_id = (
                      SELECT price_id FROM prices 
                      WHERE listing_id = pl2.listing_id 
                      ORDER BY scraped_at DESC 
                      LIMIT 1
                  )
            )
            JOIN product_listings pl_high ON p.product_key = pl_high.product_key
            JOIN stores s_high ON pl_high.store_id = s_high.store_id
            JOIN LATERAL (
                SELECT final_price, scraped_at
                FROM prices
                WHERE listing_id = pl_high.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr_high ON pr_high.final_price = (
                SELECT MAX(pr2.final_price)
                FROM product_listings pl2
                JOIN prices pr2 ON pl2.listing_id = pr2.listing_id
                WHERE pl2.product_key = p.product_key
                  AND pr2.price_id = (
                      SELECT price_id FROM prices 
                      WHERE listing_id = pl2.listing_id 
                      ORDER BY scraped_at DESC 
                      LIMIT 1
                  )
            )
            JOIN product_listings pl ON p.product_key = pl.product_key
            WHERE p.brand ILIKE %s
              AND pr_low.final_price < pr_high.final_price
            GROUP BY 
                p.product_key, p.brand, p.model, p.cpu_type, p.ram_gb, p.storage_gb,
                s_low.store_name, pr_low.final_price,
                s_high.store_name, pr_high.final_price,
                pl_low.image_url
            ORDER BY price_difference DESC
            LIMIT %s
        """
        
        cursor.execute(query, (f"%{brand}%", limit))
        deals = cursor.fetchall()
        
        if not deals:
            raise HTTPException(
                status_code=404, 
                detail=f"No deals found for brand: {brand}"
            )
        
        return [Deal(**record) for record in deals]

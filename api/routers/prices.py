"""
PromoChecker API - Prices Router
Endpoints for price history and tracking
"""
from typing import List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from api.database import get_db_cursor
from api.models import PriceHistory

router = APIRouter(prefix="/prices", tags=["Prices"])


@router.get("/{product_key}/history", response_model=List[PriceHistory])
async def get_price_history(
    product_key: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history")
):
    """
    Get price history for a product across all stores
    
    - **product_key**: Product identifier
    - **days**: Number of days of history to retrieve (default: 30, max: 365)
    
    Returns price points from all stores over the specified period
    """
    
    since_date = datetime.now() - timedelta(days=days)
    
    with get_db_cursor() as cursor:
        # Check if product exists
        cursor.execute("""
            SELECT product_key FROM products WHERE product_key = %s
        """, (product_key,))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get price history
        cursor.execute("""
            SELECT 
                s.store_name,
                p.final_price,
                p.original_price,
                p.discount_percentage,
                p.scraped_at
            FROM prices p
            JOIN product_listings pl ON p.listing_id = pl.listing_id
            JOIN stores s ON pl.store_id = s.store_id
            WHERE pl.product_key = %s 
              AND p.scraped_at >= %s
            ORDER BY p.scraped_at ASC, s.store_name
        """, (product_key, since_date))
        
        history = cursor.fetchall()
        
        if not history:
            raise HTTPException(
                status_code=404, 
                detail=f"No price history found for the last {days} days"
            )
        
        return [PriceHistory(**record) for record in history]


@router.get("/{product_key}/lowest", response_model=PriceHistory)
async def get_lowest_price_ever(product_key: str):
    """
    Get the lowest price ever recorded for a product
    """
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.store_name,
                p.final_price,
                p.original_price,
                p.discount_percentage,
                p.scraped_at
            FROM prices p
            JOIN product_listings pl ON p.listing_id = pl.listing_id
            JOIN stores s ON pl.store_id = s.store_id
            WHERE pl.product_key = %s 
              AND p.final_price IS NOT NULL
            ORDER BY p.final_price ASC
            LIMIT 1
        """, (product_key,))
        
        record = cursor.fetchone()
        
        if not record:
            raise HTTPException(status_code=404, detail="No price history found")
        
        return PriceHistory(**record)


@router.get("/{product_key}/current")
async def get_current_prices(product_key: str):
    """
    Get current prices from all stores for a product
    """
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.store_name,
                pr.final_price,
                pr.original_price,
                pr.discount_percentage,
                pr.scraped_at,
                pl.product_url
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
        
        prices = cursor.fetchall()
        
        if not prices:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "product_key": product_key,
            "stores": prices
        }

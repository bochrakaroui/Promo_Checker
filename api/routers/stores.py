"""
PromoChecker API - Stores Router
Endpoints for store information and statistics
"""
from typing import List
from fastapi import APIRouter, HTTPException
from api.database import get_db_cursor
from api.models import Store

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("/", response_model=List[Store])
async def get_all_stores():
    """
    Get list of all stores with product counts
    """
    
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.store_id,
                s.store_name,
                s.base_url,
                COUNT(DISTINCT pl.product_key) as product_count,
                ROUND(AVG(pr.final_price)::numeric, 2) as avg_price,
                MIN(pr.final_price) as min_price,
                MAX(pr.final_price) as max_price
            FROM stores s
            LEFT JOIN product_listings pl ON s.store_id = pl.store_id
            LEFT JOIN LATERAL (
                SELECT final_price
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON true
            GROUP BY s.store_id, s.store_name, s.base_url
            ORDER BY s.store_name
        """)
        
        stores = cursor.fetchall()
        return [Store(**record) for record in stores]


@router.get("/{store_name}")
async def get_store_details(store_name: str):
    """
    Get detailed information about a specific store
    """
    
    with get_db_cursor() as cursor:
        # Get store basic info
        cursor.execute("""
            SELECT store_id, store_name, base_url
            FROM stores
            WHERE store_name ILIKE %s
        """, (store_name,))
        
        store = cursor.fetchone()
        
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT pl.product_key) as product_count,
                COUNT(DISTINCT pl.listing_id) as listing_count,
                ROUND(AVG(pr.final_price)::numeric, 2) as avg_price,
                MIN(pr.final_price) as min_price,
                MAX(pr.final_price) as max_price
            FROM product_listings pl
            JOIN LATERAL (
                SELECT final_price
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON true
            WHERE pl.store_id = %s
        """, (store['store_id'],))
        
        stats = cursor.fetchone()
        
        return {
            **store,
            **stats
        }


@router.get("/{store_name}/products")
async def get_store_products(store_name: str):
    """
    Get all products available in a specific store with current prices
    """
    
    with get_db_cursor() as cursor:
        # Get store ID
        cursor.execute("""
            SELECT store_id FROM stores WHERE store_name ILIKE %s
        """, (store_name,))
        
        store = cursor.fetchone()
        
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get products
        cursor.execute("""
            SELECT 
                p.product_key,
                p.brand,
                p.model,
                p.cpu,
                p.ram,
                p.storage,
                pl.product_url,
                pr.final_price,
                pr.original_price,
                pr.discount_percentage,
                pr.scraped_at
            FROM products p
            JOIN product_listings pl ON p.product_key = pl.product_key
            JOIN LATERAL (
                SELECT final_price, original_price, discount_percentage, scraped_at
                FROM prices
                WHERE listing_id = pl.listing_id
                ORDER BY scraped_at DESC
                LIMIT 1
            ) pr ON true
            WHERE pl.store_id = %s
            ORDER BY p.brand, p.model
        """, (store['store_id'],))
        
        products = cursor.fetchall()
        
        return {
            "store_name": store_name,
            "product_count": len(products),
            "products": products
        }

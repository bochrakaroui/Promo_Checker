"""
Database import script for PromoChecker
Imports normalized JSON data into PostgreSQL database
"""
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Database configuration - reads from environment or uses defaults
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DB_CONFIG = {
        'dsn': DATABASE_URL
    }
else:
    DB_CONFIG = {
        'dbname': os.getenv('DB_NAME', 'promochecker'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432))
    }


def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f" Error connecting to database: {e}")
        raise


def import_products(conn, normalized_data: List[Dict[str, Any]]) -> int:
    """
    Import products into products table
    Uses INSERT ON CONFLICT to update existing products
    
    Returns:
        Number of products inserted/updated
    """
    cursor = conn.cursor()
    
    products_data = []
    for item in normalized_data:
        product_key = item.get('product_key', '')
        if not product_key:  # Skip products without valid key
            continue
        
        specs = item.get('specs', {})
        products_data.append((
            product_key,
            item.get('name', ''),
            specs.get('brand'),
            specs.get('model'),
            specs.get('cpu_type'),
            specs.get('cpu_generation'),
            specs.get('ram'),
            specs.get('storage')
        ))
    
    # Remove duplicates (same product_key might appear multiple times in one source)
    unique_products = list({p[0]: p for p in products_data}.values())
    
    # Bulk insert with ON CONFLICT UPDATE
    insert_query = """
        INSERT INTO products (product_key, name, brand, model, cpu_type, cpu_generation, ram_gb, storage_gb)
        VALUES %s
        ON CONFLICT (product_key) DO UPDATE SET
            name = EXCLUDED.name,
            brand = EXCLUDED.brand,
            model = EXCLUDED.model,
            cpu_type = EXCLUDED.cpu_type,
            cpu_generation = EXCLUDED.cpu_generation,
            ram_gb = EXCLUDED.ram_gb,
            storage_gb = EXCLUDED.storage_gb,
            updated_at = CURRENT_TIMESTAMP
    """
    
    execute_values(cursor, insert_query, unique_products)
    conn.commit()
    
    print(f"    Imported {len(unique_products)} unique products")
    return len(unique_products)


def import_listings_and_prices(conn, normalized_data: List[Dict[str, Any]], source: str) -> tuple:
    """
    Import product listings and current prices
    
    Returns:
        Tuple of (listings_count, prices_count)
    """
    cursor = conn.cursor()
    
    # Get store_id for this source
    cursor.execute("SELECT store_id FROM stores WHERE store_name = %s", (source,))
    result = cursor.fetchone()
    if not result:
        print(f"    Store '{source}' not found in database!")
        return 0, 0
    
    store_id = result[0]
    scrape_timestamp = datetime.now()
    
    prices_data = []
    
    # Get listing IDs after insert - track mapping between items and listing_ids
    listing_id_map = {}  # Maps item index to listing_id
    
    for idx, item in enumerate(normalized_data):
        product_key = item.get('product_key', '')
        if not product_key:
            continue
        
        # Store NULL (not '') for a missing image so the API's "has an image"
        # filters and COALESCE fallbacks behave correctly.
        image_url = (item.get('image') or '').strip() or None

        listing = (
            product_key,
            store_id,
            item.get('original_name', ''),
            item.get('link', ''),
            image_url,
            item.get('sku', ''),
            item.get('reference', ''),
            item.get('availability', ''),
            scrape_timestamp
        )
        
        cursor.execute(
            """
            INSERT INTO product_listings 
            (product_key, store_id, source_name, product_url, image_url, sku, reference, availability, last_scraped_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_key, store_id, product_url) DO UPDATE SET
                source_name = EXCLUDED.source_name,
                -- Keep the previous image when this scrape found none, so a
                -- temporary selector/render failure doesn't blank the card.
                image_url = COALESCE(EXCLUDED.image_url, product_listings.image_url),
                sku = EXCLUDED.sku,
                reference = EXCLUDED.reference,
                availability = EXCLUDED.availability,
                last_scraped_at = EXCLUDED.last_scraped_at
            RETURNING listing_id
            """,
            listing
        )
        listing_id = cursor.fetchone()[0]
        listing_id_map[idx] = listing_id
    
    conn.commit()
    
    # Now insert prices for each listing
    for idx, item in enumerate(normalized_data):
        if idx in listing_id_map:
            listing_id = listing_id_map[idx]
            final_price = item.get('final_price')
            original_price = item.get('original_price')
            discount_pct = item.get('discount_percentage', 0)
            
            prices_data.append((
                listing_id,
                final_price,
                original_price,
                discount_pct,
                scrape_timestamp
            ))
    
    # Bulk insert prices
    prices_insert_query = """
        INSERT INTO prices (listing_id, final_price, original_price, discount_percentage, scraped_at)
        VALUES %s
    """
    
    execute_values(cursor, prices_insert_query, prices_data)
    conn.commit()
    
    print(f"    Imported {len(listing_id_map)} listings and {len(prices_data)} price records")
    return len(listing_id_map), len(prices_data)


def import_source_file(conn, json_file: str, source: str):
    """Import a single normalized JSON file"""
    print(f"\n Importing {source.upper()}...")
    print(f"   File: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   Found {len(data)} products in file")
    
    # Import products first
    products_count = import_products(conn, data)
    
    # Import listings and prices
    listings_count, prices_count = import_listings_and_prices(conn, data, source)
    
    return products_count, listings_count, prices_count


def verify_import(conn):
    """Verify data was imported correctly"""
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print(" DATABASE STATISTICS")
    print("="*70)
    
    # Count products
    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]
    print(f"   Products:         {products_count:>6}")
    
    # Count listings
    cursor.execute("SELECT COUNT(*) FROM product_listings")
    listings_count = cursor.fetchone()[0]
    print(f"   Listings:         {listings_count:>6}")
    
    # Count prices
    cursor.execute("SELECT COUNT(*) FROM prices")
    prices_count = cursor.fetchone()[0]
    print(f"   Price records:    {prices_count:>6}")
    
    # Count products in multiple stores
    cursor.execute("SELECT COUNT(*) FROM multi_store_products")
    multi_store_count = cursor.fetchone()[0]
    print(f"   Multi-store:      {multi_store_count:>6}")
    
    # Show sample: cheapest laptop
    print("\n Sample: Top 3 Cheapest Laptops")
    cursor.execute("""
        SELECT name, store_name, final_price, product_url
        FROM current_best_prices
        WHERE final_price IS NOT NULL
        ORDER BY final_price ASC
        LIMIT 3
    """)
    
    for idx, row in enumerate(cursor.fetchall(), 1):
        name, store, price, url = row
        print(f"   {idx}. {name[:50]}")
        print(f"      {store.upper()}: {price} DT")
        print(f"      {url[:60]}...")
    
    # Show sample: best deals (multi-store products)
    print("\n Sample: Top 3 Products with Biggest Price Differences")
    cursor.execute("""
        SELECT 
            p.name,
            msp.store_count,
            msp.lowest_price,
            msp.highest_price,
            msp.price_difference
        FROM multi_store_products msp
        JOIN products p ON msp.product_key = p.product_key
        ORDER BY msp.price_difference DESC
        LIMIT 3
    """)
    
    for idx, row in enumerate(cursor.fetchall(), 1):
        name, stores, lowest, highest, diff = row
        print(f"   {idx}. {name[:50]}")
        print(f"      Available in {stores} stores")
        print(f"      Price range: {lowest} DT - {highest} DT (Save {diff} DT!)")
    
    print("="*70)


def main():
    """Main import process"""
    print("="*70)
    print("PromoChecker - Database Import")
    print("="*70)
    
    # Files to import
    files_to_import = [
        ('products_normalized.json', 'mytek'),
        ('tunisianet_laptops_normalized.json', 'tunisianet'),
        ('spacenet_promotions_normalized.json', 'spacenet')
    ]
    
    try:
        # Connect to database
        print("\n Connecting to PostgreSQL database...")
        conn = get_db_connection()
        print("    Connected successfully!")
        
        total_products = 0
        total_listings = 0
        total_prices = 0
        
        # Import each file
        for json_file, source in files_to_import:
            try:
                products, listings, prices = import_source_file(conn, json_file, source)
                total_products += products
                total_listings += listings
                total_prices += prices
            except FileNotFoundError:
                print(f"    File not found: {json_file} - skipping")
            except Exception as e:
                print(f"    Error importing {json_file}: {e}")
        
        # Verify import
        verify_import(conn)
        
        print("\n Import completed successfully!")
        print(f"   Total: {total_products} products, {total_listings} listings, {total_prices} prices")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"\n Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()

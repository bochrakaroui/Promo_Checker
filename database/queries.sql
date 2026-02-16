-- PromoChecker - Useful SQL Queries
-- Reference guide for common database operations

-- =====================================================
-- BASIC STATISTICS
-- =====================================================

-- Count total products
SELECT COUNT(*) as total_products FROM products;

-- Count listings per store
SELECT s.store_name, COUNT(pl.listing_id) as listings
FROM stores s
LEFT JOIN product_listings pl ON s.store_id = pl.store_id
GROUP BY s.store_name
ORDER BY listings DESC;

-- Count total price records
SELECT COUNT(*) as total_price_records FROM prices;

-- Products available in multiple stores
SELECT COUNT(*) as multi_store_products FROM multi_store_products;


-- =====================================================
-- PRICE QUERIES
-- =====================================================

-- Find cheapest laptops (current prices)
SELECT 
    name,
    store_name,
    final_price,
    product_url
FROM current_best_prices
WHERE final_price IS NOT NULL
ORDER BY final_price ASC
LIMIT 20;

-- Find products with best discounts
SELECT 
    name,
    store_name,
    original_price,
    final_price,
    discount_percentage,
    product_url
FROM current_best_prices
WHERE discount_percentage > 0
ORDER BY discount_percentage DESC
LIMIT 20;

-- Compare prices across stores for specific product
SELECT 
    s.store_name,
    pr.final_price,
    pr.original_price,
    pr.discount_percentage,
    pl.product_url,
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
WHERE pl.product_key = 'dell_vostro_3520_i5_12_8_512'
ORDER BY pr.final_price ASC;


-- =====================================================
-- PRODUCT SEARCH
-- =====================================================

-- Search by brand
SELECT DISTINCT
    p.name,
    MIN(cbp.final_price) as lowest_price,
    MAX(cbp.final_price) as highest_price,
    COUNT(DISTINCT cbp.store_name) as available_in_stores
FROM products p
JOIN current_best_prices cbp ON p.product_key = cbp.product_key
WHERE p.brand = 'dell'
GROUP BY p.product_key, p.name
ORDER BY lowest_price ASC;

-- Filter by specifications (example: i5 laptops, 8GB RAM, 512GB storage)
SELECT DISTINCT
    p.name,
    p.cpu_type,
    p.ram_gb,
    p.storage_gb,
    MIN(cbp.final_price) as best_price
FROM products p
JOIN current_best_prices cbp ON p.product_key = cbp.product_key
WHERE p.cpu_type = 'i5'
  AND p.ram_gb = 8
  AND p.storage_gb = 512
  AND cbp.final_price IS NOT NULL
GROUP BY p.product_key, p.name, p.cpu_type, p.ram_gb, p.storage_gb
ORDER BY best_price ASC;

-- Find products under budget (example: under 1500 DT)
SELECT 
    name,
    store_name,
    final_price,
    product_url
FROM current_best_prices
WHERE final_price < 1500
ORDER BY final_price ASC;


-- =====================================================
-- PRICE HISTORY & TRENDS
-- =====================================================

-- Price history for a specific product (last 30 days)
SELECT 
    s.store_name,
    p.final_price,
    p.original_price,
    p.discount_percentage,
    p.scraped_at
FROM prices p
JOIN product_listings pl ON p.listing_id = pl.listing_id
JOIN stores s ON pl.store_id = s.store_id
WHERE pl.product_key = 'dell_vostro_3520_i5_12_8_512'
  AND p.scraped_at >= NOW() - INTERVAL '30 days'
ORDER BY p.scraped_at DESC, s.store_name;

-- Price changes (products that got cheaper)
WITH price_comparison AS (
    SELECT 
        pl.product_key,
        p.name,
        s.store_name,
        pr.final_price as current_price,
        LAG(pr.final_price) OVER (PARTITION BY pl.listing_id ORDER BY pr.scraped_at) as previous_price,
        pr.scraped_at
    FROM product_listings pl
    JOIN products p ON pl.product_key = p.product_key
    JOIN stores s ON pl.store_id = s.store_id
    JOIN prices pr ON pl.listing_id = pr.listing_id
    WHERE pr.scraped_at >= NOW() - INTERVAL '7 days'
)
SELECT 
    name,
    store_name,
    previous_price,
    current_price,
    (previous_price - current_price) as price_drop,
    ROUND(((previous_price - current_price) / previous_price * 100)::numeric, 2) as drop_percentage
FROM price_comparison
WHERE previous_price IS NOT NULL 
  AND current_price < previous_price
ORDER BY price_drop DESC
LIMIT 20;

-- Average price per product across all stores
SELECT 
    p.name,
    p.brand,
    COUNT(DISTINCT s.store_id) as store_count,
    ROUND(AVG(pr.final_price)::numeric, 2) as avg_price,
    MIN(pr.final_price) as min_price,
    MAX(pr.final_price) as max_price
FROM products p
JOIN product_listings pl ON p.product_key = pl.product_key
JOIN stores s ON pl.store_id = s.store_id
JOIN LATERAL (
    SELECT final_price
    FROM prices
    WHERE listing_id = pl.listing_id
    ORDER BY scraped_at DESC
    LIMIT 1
) pr ON true
WHERE pr.final_price IS NOT NULL
GROUP BY p.product_key, p.name, p.brand
HAVING COUNT(DISTINCT s.store_id) > 1
ORDER BY (MAX(pr.final_price) - MIN(pr.final_price)) DESC;


-- =====================================================
-- BEST DEALS & SAVINGS
-- =====================================================

-- Products with biggest price difference between stores
SELECT 
    product_key,
    store_count,
    lowest_price,
    highest_price,
    price_difference,
    ROUND((price_difference / highest_price * 100)::numeric, 2) as savings_percentage
FROM multi_store_products
ORDER BY price_difference DESC
LIMIT 20;

-- Best deals right now (high discount + low price)
SELECT 
    name,
    store_name,
    original_price,
    final_price,
    discount_percentage,
    product_url
FROM current_best_prices
WHERE discount_percentage > 10
  AND final_price < 2000
ORDER BY discount_percentage DESC, final_price ASC
LIMIT 20;

-- Products only available at one store
SELECT 
    p.name,
    s.store_name,
    pr.final_price,
    pl.product_url
FROM products p
JOIN product_listings pl ON p.product_key = pl.product_key
JOIN stores s ON pl.store_id = s.store_id
JOIN LATERAL (
    SELECT final_price
    FROM prices
    WHERE listing_id = pl.listing_id
    ORDER BY scraped_at DESC
    LIMIT 1
) pr ON true
WHERE p.product_key NOT IN (
    SELECT product_key FROM multi_store_products
)
ORDER BY pr.final_price ASC;


-- =====================================================
-- INVENTORY & AVAILABILITY
-- =====================================================

-- Products currently in stock
SELECT 
    p.name,
    s.store_name,
    pl.availability,
    cbp.final_price
FROM products p
JOIN product_listings pl ON p.product_key = pl.product_key
JOIN stores s ON pl.store_id = s.store_id
JOIN current_best_prices cbp ON p.product_key = cbp.product_key AND s.store_name = cbp.store_name
WHERE LOWER(pl.availability) LIKE '%stock%'
ORDER BY cbp.final_price ASC;

-- Recently scraped products (last 24 hours)
SELECT 
    p.name,
    s.store_name,
    pl.last_scraped_at
FROM products p
JOIN product_listings pl ON p.product_key = pl.product_key
JOIN stores s ON pl.store_id = s.store_id
WHERE pl.last_scraped_at >= NOW() - INTERVAL '24 hours'
ORDER BY pl.last_scraped_at DESC;


-- =====================================================
-- DATA QUALITY CHECKS
-- =====================================================

-- Products missing specifications
SELECT 
    product_key,
    name,
    brand,
    model,
    cpu_type,
    ram_gb,
    storage_gb
FROM products
WHERE model IS NULL OR cpu_type IS NULL OR ram_gb IS NULL OR storage_gb IS NULL;

-- Listings without prices
SELECT 
    pl.listing_id,
    p.name,
    s.store_name,
    pl.product_url
FROM product_listings pl
JOIN products p ON pl.product_key = p.product_key
JOIN stores s ON pl.store_id = s.store_id
LEFT JOIN prices pr ON pl.listing_id = pr.listing_id
WHERE pr.price_id IS NULL;

-- Duplicate products (same name, different keys)
SELECT 
    name,
    COUNT(*) as count,
    STRING_AGG(product_key, ', ') as product_keys
FROM products
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY count DESC;


-- =====================================================
-- MAINTENANCE
-- =====================================================

-- Delete old price records (keep only last 90 days)
-- DELETE FROM prices WHERE scraped_at < NOW() - INTERVAL '90 days';

-- Update product statistics
-- ANALYZE products;
-- ANALYZE product_listings;
-- ANALYZE prices;

-- Check database size
SELECT 
    pg_size_pretty(pg_database_size('promochecker')) as database_size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

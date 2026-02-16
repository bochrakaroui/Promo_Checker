-- PromoChecker Database Schema
-- PostgreSQL 12+

-- Drop existing tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS prices CASCADE;
DROP TABLE IF EXISTS product_listings CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;

-- =====================================================
-- STORES TABLE - Store information
-- =====================================================
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name VARCHAR(100) UNIQUE NOT NULL,
    base_url VARCHAR(255),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial stores
INSERT INTO stores (store_name, base_url) VALUES
    ('mytek', 'https://www.mytek.tn'),
    ('tunisianet', 'https://www.tunisianet.tn'),
    ('spacenet', 'https://www.spacenet.tn');

-- =====================================================
-- PRODUCTS TABLE - Master product catalog (deduplicated)
-- =====================================================
CREATE TABLE products (
    product_key VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(200),
    cpu_type VARCHAR(50),
    cpu_generation VARCHAR(50),
    ram_gb INTEGER,
    storage_gb INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for searching by brand
CREATE INDEX idx_products_brand ON products(brand);

-- Index for searching by specs (filters)
CREATE INDEX idx_products_specs ON products(brand, cpu_type, ram_gb, storage_gb);

-- =====================================================
-- PRODUCT_LISTINGS TABLE - Store-specific product listings
-- =====================================================
CREATE TABLE product_listings (
    listing_id SERIAL PRIMARY KEY,
    product_key VARCHAR(255) NOT NULL REFERENCES products(product_key) ON DELETE CASCADE,
    store_id INTEGER NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    source_name VARCHAR(500),  -- Original name from scraper
    product_url TEXT NOT NULL,
    image_url TEXT,
    sku VARCHAR(100),          -- Store's product code/SKU
    reference VARCHAR(100),    -- Alternative identifier
    availability VARCHAR(100),
    last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique combination (same URL can't be added twice for same product/store)
    UNIQUE(product_key, store_id, product_url)
);

-- Index for finding all listings of a product
CREATE INDEX idx_listings_product ON product_listings(product_key);

-- Index for finding listings by store
CREATE INDEX idx_listings_store ON product_listings(store_id);

-- Index for recent scrapes
CREATE INDEX idx_listings_scraped ON product_listings(last_scraped_at DESC);

-- =====================================================
-- PRICES TABLE - Historical price tracking
-- =====================================================
CREATE TABLE prices (
    price_id BIGSERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES product_listings(listing_id) ON DELETE CASCADE,
    final_price DECIMAL(10, 3),      -- Current/final price (3 decimals for millimes)
    original_price DECIMAL(10, 3),   -- Original price before discount
    discount_percentage DECIMAL(5, 2),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check constraint: final_price should be <= original_price
    CONSTRAINT price_check CHECK (final_price IS NULL OR original_price IS NULL OR final_price <= original_price)
);

-- Index for finding latest price of a listing
CREATE INDEX idx_prices_listing ON prices(listing_id, scraped_at DESC);

-- Index for finding prices in time range (for graphs)
CREATE INDEX idx_prices_time ON prices(scraped_at);

-- Composite index for fast price queries
CREATE INDEX idx_prices_listing_time ON prices(listing_id, scraped_at DESC);

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at in products table
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- USEFUL VIEWS
-- =====================================================

-- View: Current best prices for all products
CREATE OR REPLACE VIEW current_best_prices AS
SELECT 
    p.product_key,
    p.name,
    p.brand,
    p.model,
    s.store_name,
    pr.final_price,
    pr.original_price,
    pr.discount_percentage,
    pl.product_url,
    pl.availability,
    pr.scraped_at
FROM products p
JOIN product_listings pl ON p.product_key = pl.product_key
JOIN stores s ON pl.store_id = s.store_id
JOIN LATERAL (
    SELECT final_price, original_price, discount_percentage, scraped_at
    FROM prices
    WHERE listing_id = pl.listing_id
    ORDER BY scraped_at DESC
    LIMIT 1
) pr ON true
WHERE s.active = true;

-- View: Products available in multiple stores
CREATE OR REPLACE VIEW multi_store_products AS
SELECT 
    product_key,
    COUNT(DISTINCT store_id) as store_count,
    MIN(final_price) as lowest_price,
    MAX(final_price) as highest_price,
    MAX(final_price) - MIN(final_price) as price_difference
FROM (
    SELECT 
        pl.product_key,
        pl.store_id,
        (SELECT final_price 
         FROM prices 
         WHERE listing_id = pl.listing_id 
         ORDER BY scraped_at DESC 
         LIMIT 1) as final_price
    FROM product_listings pl
    WHERE pl.last_scraped_at >= NOW() - INTERVAL '7 days'
) latest_prices
WHERE final_price IS NOT NULL
GROUP BY product_key
HAVING COUNT(DISTINCT store_id) > 1
ORDER BY price_difference DESC;

-- =====================================================
-- PERMISSIONS (optional - for production)
-- =====================================================
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO promochecker_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO promochecker_app;

COMMENT ON TABLE products IS 'Master product catalog - one row per unique product';
COMMENT ON TABLE stores IS 'E-commerce store information';
COMMENT ON TABLE product_listings IS 'Store-specific product listings - many-to-many relationship';
COMMENT ON TABLE prices IS 'Historical price tracking - time-series data';

# PromoChecker Database Architecture

## 📊 Database Schema Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PROMOCHECKER DATABASE                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│     STORES       │  ← 3 static rows (mytek, tunisianet, spacenet)
├──────────────────┤
│ store_id (PK)    │
│ store_name       │
│ base_url         │
│ active           │
│ created_at       │
└────────┬─────────┘
         │
         │ 1
         │
         │ N
         ▼
┌──────────────────┐         N           1   ┌──────────────────┐
│ PRODUCT_LISTINGS │◄────────────────────────┤    PRODUCTS      │
├──────────────────┤                         ├──────────────────┤
│ listing_id (PK)  │                         │ product_key (PK) │
│ product_key (FK) │                         │ name             │
│ store_id (FK)    │                         │ brand            │
│ source_name      │                         │ model            │
│ product_url      │                         │ cpu_type         │
│ image_url        │                         │ cpu_generation   │
│ sku              │                         │ ram_gb           │
│ reference        │                         │ storage_gb       │
│ availability     │                         │ created_at       │
│ last_scraped_at  │                         │ updated_at       │
│ created_at       │                         └──────────────────┘
└────────┬─────────┘                          Unique products
         │                                    ~3,000 rows
         │ 1
         │
         │ N                                  Example:
         ▼                                    product_key: "dell_vostro_3520_i5_12_8_512"
┌──────────────────┐                         name: "PC Portable Dell Vostro 3520..."
│     PRICES       │                         brand: "dell"
├──────────────────┤                         model: "vostro_3520"
│ price_id (PK)    │                         cpu_type: "i5"
│ listing_id (FK)  │                         ram_gb: 8
│ final_price      │                         storage_gb: 512
│ original_price   │
│ discount_pct     │
│ scraped_at       │
└──────────────────┘
Historical prices
Grows over time
~3,000+ per import
```

## 🔄 Data Flow

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   SCRAPY    │────▶│  NORMALIZE   │────▶│  POSTGRESQL  │
│  Spiders    │     │  JSON Files  │     │   Database   │
└─────────────┘     └──────────────┘     └──────────────┘
      │                    │                     │
      │                    │                     │
      ▼                    ▼                     ▼
products.json      products_normalized     products table
tunisianet.json    tunisianet_normalized   listings table
spacenet.json      spacenet_normalized     prices table (NEW rows each time)
```

## 📈 Price History Example

```
Product: Dell Vostro 3520 i5 8GB 512GB (product_key: "dell_vostro_3520_i5_12_8_512")

MYTEK Listing (listing_id: 101)
├── Dec 1, 2025 08:00 → 1459 DT (price_id: 1001)
├── Dec 2, 2025 08:00 → 1399 DT (price_id: 1002) ← Price dropped!
└── Dec 3, 2025 08:00 → 1459 DT (price_id: 1003)

TUNISIANET Listing (listing_id: 102)
├── Dec 1, 2025 08:00 → 1499 DT (price_id: 2001)
├── Dec 2, 2025 08:00 → 1499 DT (price_id: 2002)
└── Dec 3, 2025 08:00 → 1449 DT (price_id: 2003) ← Price dropped!

SPACENET Listing (listing_id: 103)
└── Not available

Result: Best price on Dec 2 was MYTEK at 1399 DT!
```

## 🔍 Query Patterns

### Pattern 1: Find Current Best Price
```sql
SELECT store_name, final_price 
FROM current_best_prices
WHERE product_key = 'dell_vostro_3520_i5_12_8_512'
ORDER BY final_price ASC;
```

```
Result:
store_name  | final_price
------------|------------
mytek       | 1399.0
tunisianet  | 1449.0
```

### Pattern 2: Price History Graph
```sql
SELECT scraped_at, store_name, final_price
FROM prices p
JOIN product_listings pl ON p.listing_id = pl.listing_id
JOIN stores s ON pl.store_id = s.store_id
WHERE pl.product_key = 'dell_vostro_3520_i5_12_8_512'
ORDER BY scraped_at;
```

```
Result (for frontend graph):
Date        Store       Price
Dec 1       mytek       1459
Dec 1       tunisianet  1499
Dec 2       mytek       1399  ← Best deal!
Dec 2       tunisianet  1499
Dec 3       mytek       1459
Dec 3       tunisianet  1449
```

### Pattern 3: Multi-Store Comparison
```sql
SELECT * FROM multi_store_products
WHERE product_key = 'dell_vostro_3520_i5_12_8_512';
```

```
Result:
store_count | lowest_price | highest_price | price_difference
------------|--------------|---------------|------------------
2           | 1399.0       | 1499.0        | 100.0
```

## 🎯 Key Concepts

### Deduplication
```
Same laptop sold by 3 stores = 1 product + 3 listings + 3N prices

products table:
  1 row: dell_vostro_3520_i5_12_8_512

product_listings table:
  3 rows: (one per store)
  - listing_id: 101, store: mytek
  - listing_id: 102, store: tunisianet
  - listing_id: 103, store: spacenet

prices table:
  3N rows: (3 listings × N scraper runs)
  Each import adds 3 new rows
  After 30 days of daily scraping = 90 price points!
```

### Why Separate Tables?

❌ **Bad Design (All in One Table):**
```
product_key | name | brand | store | price | url | scraped_at
dell_vostro | ... | dell  | mytek | 1459 | ... | Dec 1
dell_vostro | ... | dell  | mytek | 1399 | ... | Dec 2  ← Duplicate specs!
dell_vostro | ... | dell  | tunis | 1499 | ... | Dec 1  ← Duplicate specs!
```
Problems: Data duplication, hard to query, slow, wastes space

✅ **Good Design (Normalized):**
```
products: 1 row with specs (brand, model, CPU, RAM, storage)
product_listings: 3 rows (links products to stores)
prices: N rows per listing (time-series data)
```
Benefits: No duplication, fast queries, clear relationships

## 🚀 Scalability

### Current State
- **Products:** ~3,000 unique laptops
- **Listings:** ~3,000 (1 per store avg)
- **Prices:** ~3,000 (1 per listing currently)

### After 30 Days of Daily Scraping
- **Products:** ~3,000 (grows slowly as new laptops added)
- **Listings:** ~3,000 (stable)
- **Prices:** ~90,000 (30 scrapes × 3,000 listings)

### After 1 Year
- **Products:** ~5,000
- **Listings:** ~5,000
- **Prices:** ~1,825,000 (365 days × 5,000 listings)

**Solution:** Archive old prices after 90 days to keep recent data fast.
Indexes ensure queries remain fast even with millions of rows.

## 📊 Views (Pre-Computed Queries)

### current_best_prices
```
Shows latest price for each product listing
Used for: Product search, filters, "buy now" links
Updates: Automatically reflects latest prices
```

### multi_store_products
```
Shows products available in 2+ stores with price comparison
Used for: Best deals page, savings calculator
Updates: Automatically reflects latest prices
```

## 💡 Pro Tips

1. **Price History Queries Are Fast**
   - Index on (listing_id, scraped_at) makes time-range queries instant
   - Can show 30-day graph in milliseconds

2. **Search by Specs**
   - Index on (brand, cpu_type, ram_gb, storage_gb)
   - Filters like "i5 laptops with 8GB RAM" are instant

3. **Each Import Adds History**
   - Don't delete old prices - they're valuable!
   - Show users: "Lowest price in 30 days: 1399 DT on Dec 2"

4. **Real-Time Updates**
   - Just run scraper + normalize + import
   - Website instantly shows new prices
   - Price drops trigger alerts

## 🔗 Relationships Summary

```
stores (3) ──┬─► product_listings (~3,000)
             │
products (~3,000) ──┘
             
product_listings ──► prices (~3,000 per import, growing)
```

One product can have multiple listings (different stores).
One listing has multiple prices (historical data).

---

**This architecture supports:**
✅ Price comparison across stores  
✅ Price history tracking  
✅ Price drop alerts  
✅ Search and filters  
✅ Best deals discovery  
✅ Scalability to millions of prices  

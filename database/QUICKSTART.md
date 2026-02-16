# Database Setup - Quick Start

## What I Created for You

### 📁 Files Created:
1. **`database/schema.sql`** - Complete database structure (tables, indexes, views)
2. **`database/import_to_db.py`** - Python script to import your JSON data into PostgreSQL
3. **`database/README.md`** - Detailed step-by-step setup guide
4. **`database/queries.sql`** - Useful SQL query examples
5. **`.env.example`** - Configuration template

---

## ⚡ Quick Setup Steps

### 1️⃣ Install PostgreSQL
- Download from: https://www.postgresql.org/download/windows/
- **Remember your postgres password!**

### 2️⃣ Create Database
```powershell
psql -U postgres
CREATE DATABASE promochecker;
\q
```

### 3️⃣ Run Schema
```powershell
cd C:\Users\Bochra\PromoChecker
psql -U postgres -d promochecker -f database\schema.sql
```

### 4️⃣ Configure Password
Edit `database\import_to_db.py` line 17:
```python
'password': 'YOUR_ACTUAL_PASSWORD',  # Change this!
```

### 5️⃣ Import Data
```powershell
python database\import_to_db.py
```

---

## 📊 What Gets Created

```
DATABASE: promochecker
├── stores (3 rows)
│   ├── mytek
│   ├── tunisianet
│   └── spacenet
│
├── products (~3000 unique products)
│   └── Deduplicated product catalog
│
├── product_listings (~3000 listings)
│   └── Links products to stores
│
└── prices (~3000+ price records)
    └── Historical price tracking (grows over time)
```

---

## 🎯 Key Features

✅ **Automatic deduplication** - Same product once, sold by multiple stores  
✅ **Price history** - Every scraper run adds new price points  
✅ **Fast queries** - Optimized indexes for search/filters  
✅ **Best price tracking** - Find cheapest store instantly  
✅ **Price trends** - See price changes over time (graphs!)  
✅ **Smart views** - Pre-built queries for common operations  

---

## 💡 How It Works

### Import Process:
```
Scraped JSON → Normalize → Database Import
```

Each time you run `import_to_db.py`:
1. **Updates** products table (new products added)
2. **Updates** product_listings (new stores/URLs)
3. **Adds NEW** price records with timestamp ← This builds price history!

### Daily Workflow:
```powershell
# 1. Scrape fresh data
scrapy crawl mytekproducts -o products.json
scrapy crawl tunisianetproducts -o tunisianet_laptops.json
scrapy crawl spacenetproducts -o spacenet_promotions.json

# 2. Normalize
python normalize_all.py

# 3. Import to database (adds new price points)
python database\import_to_db.py
```

After 30 days of daily imports = **30 price points per product** = Beautiful price trend graphs! 📈

---

## 🔍 Example Queries

**Find cheapest laptop:**
```sql
SELECT name, store_name, final_price 
FROM current_best_prices 
ORDER BY final_price ASC LIMIT 1;
```

**Compare prices for specific product:**
```sql
SELECT store_name, final_price
FROM current_best_prices
WHERE product_key = 'dell_vostro_3520_i5_12_8_512';
```

**Products in multiple stores (best deals):**
```sql
SELECT * FROM multi_store_products 
ORDER BY price_difference DESC;
```

**Price history (last 30 days):**
```sql
SELECT store_name, final_price, scraped_at
FROM prices p
JOIN product_listings pl ON p.listing_id = pl.listing_id
JOIN stores s ON pl.store_id = s.store_id
WHERE pl.product_key = 'dell_vostro_3520_i5_12_8_512'
  AND p.scraped_at >= NOW() - INTERVAL '30 days';
```

More examples in `database/queries.sql` file!

---

## 🚀 Next Steps

After database is working:

1. **Test queries** - Verify data using SQL queries
2. **Build FastAPI backend** - REST API to query database
3. **Add scheduled scraping** - Automatic daily imports
4. **Create frontend** - Display products, compare prices
5. **Add features** - Price alerts, watchlists, trends

---

## 📚 Full Documentation

See `database/README.md` for:
- Detailed installation instructions
- Troubleshooting guide
- Database structure explanation
- Advanced queries

See `database/queries.sql` for:
- 40+ useful SQL query examples
- Search, filter, statistics queries
- Price history & trends
- Data quality checks

---

## ⚠️ Important Notes

1. **Password Security**: 
   - Don't commit passwords to Git!
   - Use environment variables in production
   - `.env` file is in `.gitignore`

2. **Data Growth**:
   - Prices table grows with each import (this is intentional!)
   - Consider archiving old prices after 90 days
   - Current data: ~3,243 products = ~3,243 price records per import

3. **Performance**:
   - All tables are indexed for fast queries
   - Views are pre-optimized for common operations
   - Can handle millions of price records

---

## 🆘 Need Help?

1. Check `database/README.md` troubleshooting section
2. Test connection: `psql -U postgres -d promochecker`
3. Verify tables exist: `\dt` in psql
4. Check import output for errors

---

**You're all set!** Follow the 5 quick steps above to get your database running. 🎉

# PromoChecker - Database Setup Guide

## 📋 Overview
Complete guide to set up PostgreSQL database for PromoChecker price comparison system.

---

## ✅ STEP 1: Install PostgreSQL

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 16.x installer (latest version)

2. **Run the installer**
   - Accept default installation directory
   - **IMPORTANT**: Set a password for `postgres` user (write it down!)
   - Default port: `5432` (keep this)
   - Install **pgAdmin 4** (graphical interface - recommended)
   - Install **Stack Builder** (optional)

3. **Verify installation**
   ```powershell
   psql --version
   ```
   Should show: `psql (PostgreSQL) 16.x`

---

## ✅ STEP 2: Create the Database

### Option A: Using pgAdmin (Graphical - Easier)

1. Open **pgAdmin 4** from Start Menu
2. Enter your master password (if asked)
3. In left sidebar: Expand **Servers** → **PostgreSQL 16**
4. Enter the password you set during installation
5. Right-click **Databases** → **Create** → **Database...**
6. Database name: `promochecker`
7. Owner: `postgres`
8. Click **Save**

### Option B: Using Command Line (psql)

```powershell
# Open PowerShell and run:
psql -U postgres

# Enter your password when prompted
# Then in psql prompt:
CREATE DATABASE promochecker;

# Verify it was created:
\l

# Exit psql:
\q
```

---

## ✅ STEP 3: Run the Schema File

This creates all tables (products, stores, product_listings, prices).

### Option A: Using pgAdmin

1. In pgAdmin, connect to `promochecker` database (click on it)
2. Click **Tools** → **Query Tool** (or press F5)
3. Click **Open File** icon (folder icon)
4. Navigate to: `C:\Users\Bochra\PromoChecker\database\schema.sql`
5. Click **Execute** button (▶️ play icon) or press F5
6. You should see: "Query returned successfully" with 3 rows affected (the stores)

### Option B: Using Command Line

```powershell
cd C:\Users\Bochra\PromoChecker
psql -U postgres -d promochecker -f database\schema.sql
```

**Expected output:**
```
DROP TABLE
DROP TABLE
DROP TABLE
DROP TABLE
CREATE TABLE
INSERT 0 3
CREATE TABLE
CREATE INDEX
CREATE INDEX
... (more CREATE statements)
```

---

## ✅ STEP 4: Configure Database Connection

Edit the file `database\import_to_db.py`:

**Line 14-20:** Change the password to match yours:

```python
DB_CONFIG = {
    'dbname': 'promochecker',
    'user': 'postgres',
    'password': 'YOUR_ACTUAL_PASSWORD',  # ⚠️ Change this!
    'host': 'localhost',
    'port': 5432
}
```

---

## ✅ STEP 5: Import Existing Data

Run the import script to populate the database with your scraped data:

```powershell
cd C:\Users\Bochra\PromoChecker
python database\import_to_db.py
```

**Expected output:**
```
======================================================================
PromoChecker - Database Import
======================================================================

🔌 Connecting to PostgreSQL database...
   ✅ Connected successfully!

📦 Importing MYTEK...
   File: products_normalized.json
   Found 2269 products in file
   ✅ Imported 2269 unique products
   ✅ Imported 2269 listings and 2269 price records

📦 Importing TUNISIANET...
   File: tunisianet_laptops_normalized.json
   Found 774 products in file
   ✅ Imported 774 unique products
   ✅ Imported 774 listings and 774 price records

📦 Importing SPACENET...
   File: spacenet_promotions_normalized.json
   Found 200 products in file
   ✅ Imported 200 unique products
   ✅ Imported 200 listings and 200 price records

======================================================================
📊 DATABASE STATISTICS
======================================================================
   Products:         XXXX
   Listings:         XXXX
   Price records:    XXXX
   Multi-store:       251

💰 Sample: Top 3 Cheapest Laptops
   ... (shows actual data)

⭐ Sample: Top 3 Products with Biggest Price Differences
   ... (shows savings opportunities)

======================================================================
✅ Import completed successfully!
```

---

## ✅ STEP 6: Verify Everything Works

### Query 1: Count products in database
```sql
SELECT COUNT(*) FROM products;
```

### Query 2: Show cheapest laptops
```sql
SELECT name, store_name, final_price
FROM current_best_prices
WHERE final_price IS NOT NULL
ORDER BY final_price ASC
LIMIT 10;
```

### Query 3: Find products in multiple stores
```sql
SELECT * FROM multi_store_products
ORDER BY price_difference DESC
LIMIT 10;
```

### Query 4: Price history for a specific product
```sql
SELECT 
    s.store_name,
    p.final_price,
    p.scraped_at
FROM prices p
JOIN product_listings pl ON p.listing_id = pl.listing_id
JOIN stores s ON pl.store_id = s.store_id
WHERE pl.product_key = 'dell_vostro_3520_i5_12_8_512'
ORDER BY p.scraped_at DESC;
```

**Run these in pgAdmin Query Tool or psql:**
```powershell
psql -U postgres -d promochecker
```

---

## 📁 Database Structure Summary

```
stores (3 rows)
├── mytek
├── tunisianet
└── spacenet

products (~3000 rows)
└── One row per unique product
    ├── product_key (PRIMARY KEY)
    ├── name, brand, model
    └── cpu, ram, storage specs

product_listings (~3000 rows)
└── One row per product per store
    ├── Links product to store
    ├── Store-specific info (URL, SKU)
    └── Last scraped timestamp

prices (~3000+ rows, grows over time)
└── Historical price tracking
    ├── Each scraper run adds new prices
    ├── Tracks final_price, original_price, discount
    └── Scraped_at timestamp for history
```

---

## 🔄 Daily Workflow (After Setup)

1. **Run scrapers** (get fresh data):
   ```powershell
   scrapy crawl mytekproducts -o products.json
   scrapy crawl tunisianetproducts -o tunisianet_laptops.json
   scrapy crawl spacenetproducts -o spacenet_promotions.json
   ```

2. **Normalize data**:
   ```powershell
   python normalize_all.py
   ```

3. **Import to database** (adds new price points):
   ```powershell
   python database\import_to_db.py
   ```

Each import adds **new price records** with current timestamp → builds price history automatically! 📈

---

## 🛠️ Troubleshooting

### Error: "psql: command not found"
- Add PostgreSQL to PATH:
  - Default location: `C:\Program Files\PostgreSQL\16\bin`
  - Add to System Environment Variables → Path

### Error: "password authentication failed"
- Check your password in `import_to_db.py`
- Reset postgres password if needed:
  ```powershell
  psql -U postgres
  ALTER USER postgres PASSWORD 'new_password';
  ```

### Error: "database 'promochecker' does not exist"
- Go back to STEP 2 and create the database first

### Error: "relation 'products' does not exist"
- Go back to STEP 3 and run `schema.sql`

### Error: "psycopg2 module not found"
- Already installed! But if needed:
  ```powershell
  pip install psycopg2-binary
  ```

---

## 🎯 Next Steps

After database is set up:
- ✅ Build FastAPI backend to query database
- ✅ Create REST API endpoints (search products, compare prices, get deals)
- ✅ Add scheduled scraping with background tasks
- ✅ Build frontend (React/Vue) to display products

---

## 📞 Need Help?

Check PostgreSQL logs:
- Windows: `C:\Program Files\PostgreSQL\16\data\log\`
- Or view in pgAdmin: **Dashboard** → **Server Activity**

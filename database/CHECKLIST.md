# PromoChecker Database Setup - Checklist

## ✅ Pre-Setup Checklist

- [ ] You have admin rights on Windows
- [ ] You have stable internet connection (for PostgreSQL download)
- [ ] You have ~500 MB free disk space (for PostgreSQL installation)
- [ ] You know your Windows user password (may be needed during install)

---

## 📋 Installation Checklist

### Step 1: Install PostgreSQL
- [ ] Downloaded PostgreSQL 16.x installer from postgresql.org
- [ ] Ran the installer
- [ ] Set postgres user password: `________________` (write it down!)
- [ ] Kept default port: 5432
- [ ] Installed pgAdmin 4 (GUI tool)
- [ ] Verified installation: `psql --version` works

### Step 2: Create Database
- [ ] Opened pgAdmin 4 OR psql command line
- [ ] Created database named `promochecker`
- [ ] Verified database exists (visible in pgAdmin or `\l` in psql)

### Step 3: Create Tables
- [ ] Navigated to PromoChecker folder
- [ ] Ran: `psql -U postgres -d promochecker -f database\schema.sql`
- [ ] Saw success messages (CREATE TABLE, INSERT, etc.)
- [ ] Verified tables exist: `\dt` in psql shows 4 tables
  - [ ] stores
  - [ ] products
  - [ ] product_listings
  - [ ] prices

### Step 4: Configure Import Script
- [ ] Opened `database\import_to_db.py` in editor
- [ ] Changed line 17 password to actual postgres password
- [ ] Saved file

### Step 5: Import Data
- [ ] Ensured normalized JSON files exist:
  - [ ] `products_normalized.json`
  - [ ] `tunisianet_laptops_normalized.json`
  - [ ] `spacenet_promotions_normalized.json`
- [ ] Ran: `python database\import_to_db.py`
- [ ] Saw success messages for all 3 sources
- [ ] Saw database statistics at the end

### Step 6: Verify Everything Works
- [ ] Connected to database: `psql -U postgres -d promochecker`
- [ ] Counted products: `SELECT COUNT(*) FROM products;` (should be ~3000)
- [ ] Counted listings: `SELECT COUNT(*) FROM product_listings;` (should be ~3000)
- [ ] Counted prices: `SELECT COUNT(*) FROM prices;` (should be ~3000)
- [ ] Checked multi-store products: `SELECT COUNT(*) FROM multi_store_products;` (should be ~251)
- [ ] Tested a query from `database/queries.sql`

---

## 🎯 Post-Setup Checklist

### Database is Working
- [ ] Can connect to database without errors
- [ ] All 4 tables exist and have data
- [ ] Views work (current_best_prices, multi_store_products)
- [ ] Sample queries return results

### Data Quality
- [ ] Products have correct specs (brand, model, CPU, RAM, storage)
- [ ] Prices look reasonable (not NULL, not 0)
- [ ] Multi-store matches look logical (same product, different stores)
- [ ] URLs are valid and accessible

### Documentation Review
- [ ] Read `database/README.md` (full guide)
- [ ] Reviewed `database/QUICKSTART.md` (this file)
- [ ] Bookmarked `database/queries.sql` (query examples)
- [ ] Understand daily workflow (scrape → normalize → import)

---

## 🚀 Next Phase Checklist

### Backend Development (FastAPI)
- [ ] Install FastAPI and dependencies
- [ ] Create API endpoints:
  - [ ] GET /products (search, filter)
  - [ ] GET /products/{product_key} (details)
  - [ ] GET /products/{product_key}/prices (price history)
  - [ ] GET /products/deals (best deals)
  - [ ] GET /products/compare (multi-store comparison)
- [ ] Add authentication (optional)
- [ ] Test API with Swagger UI

### Automation
- [ ] Set up scheduled scraping (daily/hourly)
- [ ] Automatic normalization after scraping
- [ ] Automatic database import
- [ ] Error notifications

### Frontend Development
- [ ] Choose framework (React/Vue/Next.js)
- [ ] Product listing page
- [ ] Product detail page with price comparison
- [ ] Price history graphs
- [ ] Search and filters
- [ ] Best deals page

### Production Deployment
- [ ] Database backup strategy
- [ ] Environment variables for production
- [ ] Server hosting (cloud or local)
- [ ] Domain name and SSL
- [ ] Monitoring and logging

---

## 📝 Notes & Issues

Use this space to track problems, solutions, or customizations:

```
Date: _____________
Issue: 

Solution:


Date: _____________
Issue: 

Solution:


Date: _____________
Custom Changes:

```

---

## 🎉 Success Criteria

You can consider the database setup complete when:

✅ PostgreSQL is installed and running  
✅ `promochecker` database exists  
✅ All 4 tables created (stores, products, product_listings, prices)  
✅ Sample data imported (3,000+ products)  
✅ Queries return expected results  
✅ You understand the data flow (scrape → normalize → import)  
✅ Ready to build FastAPI backend  

---

**Last Updated:** December 3, 2025  
**Version:** 1.0  
**Status:** [ ] Not Started | [ ] In Progress | [ ] Complete

# PromoChecker - Quick Start Guide

## Running the Complete Application

### 1. Start the Backend API

Open a terminal and run:

```powershell
cd C:\Users\Bochra\PromoChecker
uvicorn api.main:app --reload
```

The API will be available at: `http://localhost:8000`
API documentation (Swagger UI): `http://localhost:8000/docs`

### 2. Start the Frontend

Open a **new terminal** and run:

```powershell
cd C:\Users\Bochra\PromoChecker\frontend
npm run dev
```

The website will be available at: `http://localhost:3000`

### 3. Access the Application

Open your browser and go to:
- **Main App**: http://localhost:3000
- **Best Deals**: http://localhost:3000/deals
- **Stores**: http://localhost:3000/stores
- **API Docs**: http://localhost:8000/docs

## What You Built

### Backend (FastAPI)
✅ REST API with 13 endpoints
✅ PostgreSQL database integration
✅ Automated web scraping (Scrapy)
✅ Daily data pipeline automation (APScheduler)
✅ Price comparison algorithms

### Frontend (Next.js)
✅ Modern, responsive UI
✅ Product browsing with search & filters
✅ Best deals comparison page
✅ Store statistics page
✅ Individual product detail pages
✅ Real-time price comparison

### Automation
✅ Scrapes 3 e-commerce sites daily
✅ Normalizes and matches products
✅ Updates database automatically at 2:00 AM
✅ Runs completely in the background

## Testing the System

1. **View Products**: Go to http://localhost:3000 and browse laptops
2. **Search**: Try searching for "Dell" or "i7"
3. **Sort**: Change sorting to see highest/lowest prices
4. **View Deals**: Click "Best Deals" to see biggest savings
5. **Product Details**: Click any product to see full price comparison
6. **Check Stores**: View "Stores" page to see all retailers

## Running the Data Pipeline Manually

To manually scrape new data:

```powershell
cd C:\Users\Bochra\PromoChecker
python automation/run_scrapers.py
```

This will:
1. Scrape all configured stores
2. Normalize the data
3. Update the database

## Troubleshooting

### Frontend shows "Failed to load products"
- Make sure the backend is running on port 8000
- Check that PostgreSQL is running
- Verify database has data

### No products showing
- Run the data pipeline manually: `python automation/run_scrapers.py`
- Check API at http://localhost:8000/docs
- Test the `/api/products` endpoint

### Port already in use
- Backend: Change port with `uvicorn api.main:app --port 8001`
- Frontend: Change port with `npm run dev -- -p 3001`

## Next Steps

- Customize the UI colors and branding
- Add more stores to scrape
- Deploy to production (Vercel for frontend, cloud hosting for backend)
- Add email notifications for price drops
- Implement user accounts and wishlists

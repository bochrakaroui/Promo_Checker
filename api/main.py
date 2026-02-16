"""
PromoChecker API - Main Application
FastAPI backend for price comparison and deal tracking
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import test_connection, connection_pool
from api.routers import products, prices, deals, stores
from api.models import APIStats
from api.database import get_db_cursor
from automation.scheduler import start_scheduler, stop_scheduler

# Create FastAPI app
app = FastAPI(
    title="PromoChecker API",
    description="REST API for laptop price comparison across Tunisian e-commerce stores",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(deals.router, prefix="/api")
app.include_router(stores.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    """
    API welcome message with basic information
    """
    return {
        "message": "Welcome to PromoChecker API",
        "version": "1.0.0",
        "description": "REST API for laptop price comparison across Tunisian e-commerce stores",
        "documentation": "/docs",
        "stores": ["MyTek", "Tunisianet", "Spacenet"],
        "endpoints": {
            "products": "/api/products",
            "prices": "/api/prices",
            "deals": "/api/deals",
            "stores": "/api/stores",
            "stats": "/api/stats"
        }
    }


# Stats endpoint
@app.get("/api/stats", response_model=APIStats)
async def get_stats():
    """
    Get API statistics: total products, stores, listings, etc.
    """
    
    with get_db_cursor() as cursor:
        # Total products
        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()['count']
        
        # Total stores
        cursor.execute("SELECT COUNT(*) as count FROM stores")
        total_stores = cursor.fetchone()['count']
        
        # Total listings
        cursor.execute("SELECT COUNT(*) as count FROM product_listings")
        total_listings = cursor.fetchone()['count']
        
        # Multi-store products
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM (
                SELECT product_key
                FROM product_listings
                GROUP BY product_key
                HAVING COUNT(DISTINCT store_id) > 1
            ) multi
        """)
        multi_store_products = cursor.fetchone()['count']
        
        # Latest scrape
        cursor.execute("""
            SELECT MAX(scraped_at) as latest_scrape
            FROM prices
        """)
        latest_scrape = cursor.fetchone()['latest_scrape']
        
        # Average price
        cursor.execute("""
            SELECT ROUND(AVG(final_price)::numeric, 2) as avg_price
            FROM (
                SELECT DISTINCT ON (listing_id) final_price
                FROM prices
                WHERE final_price IS NOT NULL
                ORDER BY listing_id, scraped_at DESC
            ) latest_prices
        """)
        avg_price = cursor.fetchone()['avg_price']
        
        return APIStats(
            total_products=total_products,
            total_stores=total_stores,
            total_listings=total_listings,
            multi_store_products=multi_store_products,
            latest_scrape=latest_scrape,
            avg_price=float(avg_price) if avg_price else 0.0
        )


# Startup event
@app.on_event("startup")
async def startup():
    """
    Initialize database connection pool on startup
    """
    print("🚀 Starting PromoChecker API...")
    
    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
        print(f"📊 Connection pool initialized (min: 1, max: 10)")
    else:
        print("❌ Database connection failed - check your .env configuration")
    
    # Start automated scraping scheduler
    try:
        start_scheduler()
        print("⏰ Automated scraping scheduler started")
    except Exception as e:
        print(f"⚠️  Scheduler failed to start: {e}")
    
    print("📚 API documentation available at http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """
    Close database connection pool on shutdown
    """
    print("🛑 Shutting down PromoChecker API...")
    
    # Stop scheduler
    try:
        stop_scheduler()
        print("✅ Scheduler stopped")
    except Exception as e:
        print(f"⚠️  Error stopping scheduler: {e}")
    
    if connection_pool:
        connection_pool.closeall()
        print("✅ Database connections closed")


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    db_status = "healthy" if test_connection() else "unhealthy"
    
    return {
        "status": "online",
        "database": db_status,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

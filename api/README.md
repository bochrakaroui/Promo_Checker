# PromoChecker FastAPI Backend

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn[standard] python-dotenv psycopg2-binary
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=promochecker
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3. Run the API
```bash
# From the project root directory
python -m uvicorn api.main:app --reload

# Or run directly
python api/main.py
```

### 4. Access the API
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## API Endpoints

### Products
- `GET /api/products` - List all products with filters and pagination
  - Query params: `brand`, `min_price`, `max_price`, `min_ram`, `min_storage`, `cpu_type`, `store`, `search`, `sort_by`, `sort_order`, `page`, `page_size`
- `GET /api/products/{product_key}` - Get product details with all store listings
- `GET /api/products/{product_key}/stores` - Compare prices across stores

### Prices
- `GET /api/prices/{product_key}/history` - Get price history over time (default: 30 days)
- `GET /api/prices/{product_key}/lowest` - Get lowest price ever recorded
- `GET /api/prices/{product_key}/current` - Get current prices from all stores

### Deals
- `GET /api/deals` - Get best multi-store deals (biggest savings)
  - Query params: `min_savings`, `min_savings_percent`, `limit`
- `GET /api/deals/top-discounts` - Get products with highest discount percentages
- `GET /api/deals/by-brand/{brand}` - Get best deals for a specific brand

### Stores
- `GET /api/stores` - List all stores with product counts
- `GET /api/stores/{store_name}` - Get detailed store information
- `GET /api/stores/{store_name}/products` - Get all products from a store

### Stats
- `GET /api/stats` - Get API statistics
- `GET /health` - Health check endpoint

## Example Requests

### Search for laptops
```bash
curl "http://localhost:8000/api/products?brand=dell&min_ram=16&sort_by=price&sort_order=asc"
```

### Get product details
```bash
curl "http://localhost:8000/api/products/dell_latitude_5430_i5_1235u_16_512"
```

### Get best deals
```bash
curl "http://localhost:8000/api/deals?min_savings=200&limit=10"
```

### Get price history
```bash
curl "http://localhost:8000/api/prices/dell_latitude_5430_i5_1235u_16_512/history?days=30"
```

## Architecture

```
api/
├── main.py              # FastAPI app entry point
├── database.py          # Database connection pool
├── models.py            # Pydantic models
└── routers/
    ├── products.py      # Products endpoints
    ├── prices.py        # Price history endpoints
    ├── deals.py         # Deals endpoints
    └── stores.py        # Stores endpoints
```

## Features

- **Connection Pooling**: Efficient database connections (min: 1, max: 10)
- **Data Validation**: Pydantic models for request/response validation
- **Auto Documentation**: Swagger UI and ReDoc generated automatically
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Error Handling**: HTTP exceptions with proper status codes
- **Complex Queries**: Optimized SQL with window functions and LATERAL joins
- **Pagination**: All list endpoints support pagination
- **Filtering**: Multiple filter options for products
- **Sorting**: Flexible sorting by price, name, brand

## Testing with Swagger UI

1. Start the API server
2. Open http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in parameters and click "Execute"
5. View the response below

## Notes

- Default page size: 20 items
- Maximum page size: 100 items
- Price history default: 30 days (max: 365)
- All prices in TND (Tunisian Dinar)
- Timestamps in ISO 8601 format

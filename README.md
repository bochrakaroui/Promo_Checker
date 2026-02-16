# PromoChecker

PromoChecker is a full‑stack app that **scrapes, normalizes, and compares laptop prices** across major Tunisian e‑commerce stores (MyTek, Tunisianet, Spacenet).  
It exposes a **FastAPI REST API** and a **Next.js (React) frontend** to browse products, compare prices, and find best deals.

## Tech stack
- **Backend**: FastAPI + PostgreSQL
- **Scraping**: Scrapy (+ Playwright where needed)
- **Frontend**: Next.js / React / TypeScript

## Project structure
- `PromoChecker/` — Scrapy project (spiders + normalization helpers)
- `automation/` — scheduled scraping runner
- `database/` — schema + import script
- `api/` — FastAPI backend
- `frontend/` — Next.js frontend

## Run locally

### 1) Backend API (FastAPI)
From the repo root:

```powershell
uvicorn api.main:app --reload
```

API runs on `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### 2) Frontend (Next.js)

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Data pipeline (scrape → normalize → import)
Run the full pipeline from the repo root:

```powershell
python automation/run_scrapers.py
```

## Database
- Schema: `database/schema.sql`
- Import script: `database/import_to_db.py`
- Guides: `database/README.md` and `database/QUICKSTART.md`

## Environment variables
- Backend: copy `.env.example` → `.env` and fill in DB settings
- Frontend: set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if your API isn’t on `http://localhost:8000`

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

## Scheduling (automatic weekly scraping)

The pipeline runs **every Sunday at 03:00 (Africa/Tunis)** by default. The
schedule lives in `automation/scheduler.py` and starts automatically with the
API, so it only runs while `uvicorn` is running.

Override the timing in `.env`:

```ini
SCRAPE_ENABLED=true       # false to turn the scheduler off
SCRAPE_DAY_OF_WEEK=sun    # mon..sun, or * for every day
SCRAPE_HOUR=3             # 0-23
SCRAPE_MINUTE=0           # 0-59
SCRAPE_TIMEZONE=Africa/Tunis
```

Run the scheduler on its own, without the API:

```powershell
python automation/scheduler.py          # wait for the next scheduled run
python automation/scheduler.py --now    # scrape once immediately, then keep waiting
```

### Running it without keeping a process alive (Windows)

The in-process scheduler stops when the API stops. To scrape weekly even when
nothing is running, register a Windows scheduled task instead (and set
`SCRAPE_ENABLED=false` so the job doesn't run twice):

```powershell
schtasks /Create /TN "PromoChecker Weekly Scrape" /SC WEEKLY /D SUN /ST 03:00 `
  /TR "'C:\Users\Bochra\PromoChecker\venv\Scripts\python.exe' 'C:\Users\Bochra\PromoChecker\automation\run_scrapers.py'" `
  /RL HIGHEST /F
```

Useful follow-ups: `schtasks /Run /TN "PromoChecker Weekly Scrape"` to test it
now, `schtasks /Query /TN "PromoChecker Weekly Scrape" /V /FO LIST` to see the
next run and last result, `schtasks /Delete /TN "PromoChecker Weekly Scrape" /F`
to remove it.

## Database
- Schema: `database/schema.sql`
- Import script: `database/import_to_db.py`
- Guides: `database/README.md` and `database/QUICKSTART.md`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) — Supabase (database), Render (API), Vercel
(frontend), GitHub Actions (weekly scrape).

## Environment variables
- Backend: copy `.env.example` → `.env` and fill in DB settings
- Frontend: set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if your API isn’t on `http://localhost:8000`

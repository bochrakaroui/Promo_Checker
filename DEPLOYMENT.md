# Deploying PromoChecker

Four pieces, three services:

| Piece | Runs on | Why there |
|---|---|---|
| Postgres | Supabase | Nothing deployed can reach `localhost:5432` on your laptop |
| FastAPI backend | Render | Long-lived process, real connection pooling |
| Next.js frontend | Vercel | What Vercel is built for |
| Weekly scrape | GitHub Actions | Playwright needs a real Chromium and the crawl takes minutes — Vercel functions can't do either |

Do the steps in order: each one produces a value the next one needs.

---

## Step 1 — Database on Supabase

1. Create a project at [supabase.com](https://supabase.com) (free tier is fine). Save the database password.
2. **Project Settings → Database → Connection string → URI**. Copy it and put the
   password in place of `[YOUR-PASSWORD]`. It looks like:
   ```
   postgresql://postgres.abcdefgh:PASSWORD@aws-0-eu-west-3.pooler.supabase.com:6543/postgres
   ```
   Use the **Session pooler** (port 6543) string — it handles many short-lived connections better.
3. Create the tables: **SQL Editor → New query**, paste all of
   [`database/schema.sql`](database/schema.sql), and run it.

   > ⚠️ `schema.sql` starts with `DROP TABLE ... CASCADE`. That's fine on a fresh
   > project, but never run it again later — it deletes all your price history.

4. Load your existing data into it from your machine:
   ```powershell
   $env:DATABASE_URL = "postgresql://...your-supabase-uri..."
   .\venv\Scripts\python.exe database/import_to_db.py
   ```
   You should see the products/listings/prices counts at the end.

`api/database.py` prefers `DATABASE_URL` over the `DB_*` variables, so nothing in
the code needs changing.

---

## Step 2 — Weekly scraping on GitHub Actions

The workflow is already committed at
[`.github/workflows/weekly-scrape.yml`](.github/workflows/weekly-scrape.yml).
It runs **Sundays at 02:00 UTC = 03:00 Africa/Tunis**.

1. Push your branch to GitHub.
2. **Repo → Settings → Secrets and variables → Actions → New repository secret**
   - Name: `DATABASE_URL`
   - Value: the Supabase URI from Step 1
3. Test it now instead of waiting a week: **Actions → Weekly scrape → Run workflow**.
   The run takes ~10–20 minutes and uploads the scraped JSON as an artifact so you
   can inspect what it got.

To change the schedule, edit the `cron:` line (GitHub cron is **always UTC**):

| Wanted | cron |
|---|---|
| Sunday 03:00 Tunis | `0 2 * * 0` |
| Every day 03:00 Tunis | `0 2 * * *` |
| Mon + Thu 06:00 Tunis | `0 5 * * 1,4` |

---

## Step 3 — Backend on Render

1. [render.com](https://render.com) → **New → Blueprint** → select this repo.
   It picks up [`render.yaml`](render.yaml) automatically.
2. Set the two secret env vars when prompted:
   - `DATABASE_URL` — the Supabase URI
   - `ALLOWED_ORIGINS` — leave as `*` for now; you'll set it in Step 5
3. Deploy, then confirm it's alive:
   `https://promochecker-api.onrender.com/health` → `{"status":"online","database":"healthy"}`

`SCRAPE_ENABLED=false` is already set in the blueprint — the in-process scheduler
must stay off in production, since GitHub Actions owns the schedule now.

> Render's free tier sleeps after ~15 minutes idle, so the first request after a
> quiet spell takes ~30s. Fine for a portfolio project; upgrade if it bothers you.

---

## Step 4 — Frontend on Vercel

1. [vercel.com](https://vercel.com) → **Add New → Project** → import the repo.
2. **Set Root Directory to `frontend`.** This is the step everyone misses — the
   Next.js app is not at the repo root, and the build fails without it.
3. Add an environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://promochecker-api.onrender.com` (no trailing slash)
4. Deploy.

`NEXT_PUBLIC_*` variables are baked in at **build** time, so if you change the API
URL later you must redeploy — editing it in the dashboard alone does nothing.

---

## Step 5 — Close the CORS hole

Back in Render, set `ALLOWED_ORIGINS` to your actual Vercel URL:

```
ALLOWED_ORIGINS=https://your-project.vercel.app
```

Render redeploys automatically. Until you do this the API answers requests from
any website on the internet.

---

## Checklist

- [ ] `https://<api>.onrender.com/health` returns `database: healthy`
- [ ] `https://<api>.onrender.com/api/products?page_size=5` returns products with `image_url`
- [ ] The Vercel site lists products and pictures load
- [ ] A manually-triggered **Weekly scrape** run finishes green
- [ ] `ALLOWED_ORIGINS` is your Vercel domain, not `*`

## Troubleshooting

**Frontend shows "Failed to load products"** — open the browser console. A CORS
error means `ALLOWED_ORIGINS` doesn't match your Vercel domain exactly (scheme
included, no trailing slash). A 404/timeout means `NEXT_PUBLIC_API_URL` is wrong
or Render is cold-starting.

**Scrape workflow fails on Playwright** — the `--with-deps` flag installs the
system libraries Chromium needs; keep it.

**Scrape succeeds but the site shows nothing new** — check the workflow used the
`DATABASE_URL` secret and not a stale local `.env`; the Actions log prints the
imported row counts.

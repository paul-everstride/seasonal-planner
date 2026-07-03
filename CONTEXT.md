# Everstride — Project Context

> **You are in the `seasonal-planner` repo — the season-plan tool for Everstride.**
> Self-contained overview of the whole Everstride system. Full founder-level docs live in a
> private Obsidian vault (not in git).

## What Everstride is

A coach-first athlete intelligence platform for endurance coaches. It aggregates wearable data (recovery via WHOOP, activities via Strava) through the Open Wearables backend into a coaching dashboard. This repo is the **seasonal planner** — coaches build periodized training plans per athlete.

## The three repos

| Repo | What it is | Stack | Live URL |
|------|-----------|-------|----------|
| **Everstride-notion** | Coach frontend + dashboard | Next.js 14, TypeScript, Supabase | `app.everstride.fit` |
| **open-wearables** (fork) | Wearable data backend | FastAPI, Celery/Redis, Postgres | `backend-production-412a.up.railway.app` |
| **seasonal-planner** (this) | Season-plan tool | Flask + HTML/JS, Supabase | `planner.everstride.fit` |

## This repo — how it works

- Flask app (`app.py`) serving `index.html` (form) + `dashboard.html` (interactive plan). Plan logic in `planner.py`, Excel export in `generate_plan.py`.
- Opened from Everstride with `?coach_id=&coach_name=&token=` in the URL.
- Reads/writes plans in the shared **Supabase** DB (`season_plans` table) using a service key.
- **Auth:** the `/api/*` endpoints authenticate the coach from an **HMAC-signed token** (verified against `PLANNER_SHARED_SECRET`) that the Everstride frontend mints. Secret-gated: with no secret set it falls back to legacy query-param mode.
  - ⚠️ **Open action:** set `PLANNER_SHARED_SECRET` (same value) on BOTH this service and the Everstride frontend service in Railway, then redeploy both, to actually turn auth on. Until then the API is still open.
- Hardening already in place: 1MB request cap, URL-encoded Excel filename, clean 400s.

## Deployment / ops

- Hosted on **Railway** (auto-deploy from `main`). Flask must bind `0.0.0.0`; Railway sets `PORT`.
- Env vars: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `PLANNER_SHARED_SECRET`.
- Push: `git push`.

## Current open action items (as of 2026-07-03)

1. **Set `PLANNER_SHARED_SECRET`** on both this service and the Everstride frontend → activates API auth.
2. Optional: add rate limiting to `/api/*`.

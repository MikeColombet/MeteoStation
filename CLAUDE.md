# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal weather-station pipeline: Python scripts poll Open-Meteo for a
fixed list of French cities, append readings to per-city CSV files tracked
in git, and render those CSVs into a static HTML dashboard. A second,
independent Next.js dashboard reads the same CSVs at build time. Everything
is in French (comments, commit messages, UI text) — keep new text consistent
with that.

## Repository layout

- `cities.py` — single source of truth for the tracked cities (slug, name,
  lat/lon). Every Python script imports `CITIES` from here. Currently 4
  personal locations plus a ~20-city representative spread across the Nord
  department (59), grouped and commented by area (métropole lilloise,
  Flandres, Douaisis, Cambrésis, Valenciennois, Avesnois) — not an
  exhaustive list of the department's ~650 communes.
- `fetch_weather.py` — fetches the *current* reading for each city and
  appends it to `weather_data_<slug>.csv` if the timestamp isn't already
  present. Meant to run frequently (every 15 min via GitHub Actions).
- `seed_history.py` — backfills the last 7 days at 15-min resolution
  (Open-Meteo `minutely_15`). Used to bootstrap a new city or self-heal
  after a gap (e.g. the machine/runner was off). Run automatically after
  every `fetch_weather.py` in CI as a self-healing step.
- `seed_archive.py` — backfills older history (up to ~1 month, hourly
  resolution) via the Open-Meteo Archive (ERA5) API, stopping 6 days before
  today since archive data needs time to consolidate. Run manually, not
  from CI.
- `generate_dashboard.py` — reads all `weather_data_*.csv` and renders a
  single self-contained `weather_dashboard.html` (Plotly via CDN, vanilla
  JS, inlined data as JSON) with a city selector, dual-axis charts, sortable
  filterable table, and persisted dark mode. This file is regenerated, not
  hand-edited, and is gitignored.
- `plot_weather.py` — renders a static PNG chart (matplotlib) per city for
  the last 4 days, mostly a quick sanity-check tool.
- `weather_data_<slug>.csv` — the actual historical data, one file per city,
  columns: `timestamp, temperature_2m, relative_humidity_2m,
  apparent_temperature, precipitation, rain, weather_code, wind_speed_10m,
  wind_direction_10m, wind_gusts_10m, surface_pressure`. These ARE tracked
  in git (append-only, deduped by timestamp) — this is the durable data
  store for the whole project, treat it accordingly.
- `nextjs-dashboard/` — a separate, independently deployed Next.js
  dashboard with equivalent functionality (see below). Deliberately not
  wired into the CSV-producing pipeline.

## Data flow / automation

`.github/workflows/fetch.yml` is the only production automation (any
previous launchd/local-cron setup has been removed):
1. Runs every 15 minutes on GitHub Actions (`workflow_dispatch` also
   available for manual runs).
2. `fetch_weather.py` → `seed_history.py` (self-heal any gap) →
   commits changed `weather_data_*.csv` back to `main` if there's a diff.
3. `generate_dashboard.py` regenerates `weather_dashboard.html` into
   `_site/index.html` and deploys it to GitHub Pages.

The Next.js dashboard is NOT part of this workflow — it reads the CSVs at
`next build` time from the parent directory, so it only reflects data as of
whenever it was last built. It has no deployment target configured (the
prior Netlify setup was removed); `npm run build` produces a static export
in `out/` to publish manually if/when needed.

## Commands

Python (root) — no virtualenv/requirements file in the repo; scripts only
need `requests` (fetch/seed scripts) or `matplotlib` (plot_weather.py):
```bash
python3 fetch_weather.py      # one poll cycle, all cities
python3 seed_history.py       # backfill last 7 days (15-min resolution)
python3 seed_archive.py       # backfill older history (hourly, ERA5)
python3 generate_dashboard.py # regenerate weather_dashboard.html
python3 plot_weather.py       # regenerate per-city PNG charts
```
There are no automated tests for the Python side.

Next.js (`nextjs-dashboard/`):
```bash
npm install
npm run dev     # local dev server, http://localhost:3000
npm run build   # static export to out/ (output: "export" in next.config.ts)
npm run lint    # eslint
```
No test suite is configured for the Next.js app either. No deployment
target is configured — `out/` is a plain static export to publish manually
wherever needed.

## Working on this codebase

- Adding a city: add one entry to `cities.py`'s `CITIES` list (geocode via
  `https://geocoding-api.open-meteo.com/v1/search?name=<ville>&country=FR`
  as noted in that file), then mirror the same slug/name into
  `nextjs-dashboard/lib/cities.ts` if the Next.js dashboard should show it
  too — the two lists are maintained by hand and must stay in sync.
- CSV schema changes must be applied consistently across `fetch_weather.py`,
  `seed_history.py`, `seed_archive.py`, `generate_dashboard.py`,
  `plot_weather.py`, and `nextjs-dashboard/lib/data.ts`/`types.ts` — they
  all hardcode the same field list independently rather than sharing one
  definition.
- `weather_dashboard.html`, `weather_chart*.png`, `_site/`, and the Next.js
  `out/`/`.next/` build output are all gitignored/regenerated — don't hand
  edit or commit them.
- Timestamps in the CSVs and the HTML dashboard's JS are treated as naive
  local time (Europe/Paris, per the Open-Meteo `timezone` param) and parsed
  as UTC internally in `weather_dashboard.html` purely to compute relative
  durations (e.g. moving averages) independent of the viewer's timezone —
  not to display an absolute time in a different zone.

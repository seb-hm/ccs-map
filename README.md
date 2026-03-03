# CCS Projects Europe — Interactive Map

Interactive Leaflet map tracking 220+ European Carbon Capture and Storage (CCS) projects. Data sourced from CATF's Europe database, enriched with Factor2 Energy business development intelligence.

**Live map:** `https://seb-hm.github.io/ccs-map/`

## How it works

The map (`index.html`) currently embeds all project data inline. The CSV and merge script are included for the quarterly CATF refresh workflow.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Interactive Leaflet map (self-contained, deploy via GitHub Pages) |
| `projects.csv` | CSV export of the master Excel for reference and future dynamic loading |
| `catf_merge.py` | Python script to merge fresh CATF data into the F2E Excel |
| `README.md` | This file |

## Map update workflow

The master database lives on SharePoint as `CCS Projects Europe.xlsx`. To update the map after editing the Excel:

1. Export the **Projects** sheet as CSV UTF-8 (File → Save As → CSV UTF-8)
2. Rename to `projects.csv`
3. Upload to this repo via GitHub web UI (Add file → Upload files)
4. The map currently uses inline data — to reflect CSV changes, regenerate `index.html`

## CATF quarterly refresh

1. Download fresh CATF spreadsheet from [catf.us/ccstableeurope](https://www.catf.us/ccstableeurope/)
2. Download current Excel from SharePoint
3. Run: `python catf_merge.py CATF_CCUS_Database.xlsx "CCS Projects Europe.xlsx"`
4. Review merge log, re-upload merged Excel to SharePoint
5. Export CSV and update this repo

## Map features

- Color by subsector: Cement, Hydrogen, Storage, Transport Hub, Biomass, DAC, WtE
- Border by status: Operational, Under Construction, In Development, Planned
- Filters: Status, Sector, Subsector, Contact Status, Internal Priority
- Search: Real-time across project name, entities, country, subsector
- Popups: Full project details including contacts, funding, and links

## GitHub Pages setup

Settings → Pages → Source: deploy from `main` branch, `/ (root)` → Save

## Requirements

- `catf_merge.py` requires Python 3.8+ with `pandas` and `openpyxl`

# CCS Projects Europe — Interactive Map

Interactive map tracking 220+ European Carbon Capture and Storage (CCS) projects, maintained by Factor2 Energy.

**Live map:** `https://seb-hm.github.io/ccs-map/`

## Files

| File | Purpose |
|------|---------|
| `index.html` | Interactive Leaflet map, deployed via GitHub Pages |
| `CCS Projects Europe.xlsx` | Master database — single source of truth |
| `projects.csv` | Auto-generated from Excel by GitHub Action — do not edit manually |
| `convert_excel_to_csv.py` | Conversion script called by the GitHub Action |
| `catf_merge.py` | Script to merge fresh CATF data into the master Excel |
| `.github/workflows/excel_to_csv.yml` | GitHub Action: converts Excel → CSV on every push |

## Workflow — updating the map

The master database lives on SharePoint as `CCS Projects Europe.xlsx`. To update the map:

1. Edit the Excel on SharePoint (you or a team member)
2. Download a copy and replace the file in this repo folder
3. Push to GitHub:
   ```
   cd "C:\Users\sebas\OneDrive\Dokumente\GitHub\ccs-map"
   git add "CCS Projects Europe.xlsx"
   git commit -m "Update project data"
   git push
   ```
4. The GitHub Action automatically converts the Excel to `projects.csv` and commits it (~1 min)
5. GitHub Pages picks up the change and the map updates

**Never edit `projects.csv` manually** — it is always overwritten by the Action.

## Workflow — adding a new project

Use the built-in Claude Code slash command from the repo folder:

1. Open PowerShell and navigate to the repo:
   ```
   cd "C:\Users\sebas\OneDrive\Dokumente\GitHub\ccs-map"
   claude
   ```
2. Type `/add-project` and paste any raw project information (website text, press release, PDF content, etc.)
3. Claude reads the current Excel, checks if the project already exists, and outputs:
   - A summary table of all filled fields for verification
   - A tab-separated row to paste directly into Excel (click cell A of an empty row → paste)
4. Paste the row into your formatted Excel on SharePoint, then push to GitHub

## Workflow — merging a fresh CATF database download

When CATF publishes an updated CCS database, merge it into the master Excel:

1. Download the latest CATF database from https://www.catf.us/ccstableeurope/ (e.g. `CATF_CCUS_Database.xlsx`)
2. Place a copy of your current working Excel (`CCS Projects Europe.xlsx`) alongside it, or use the repo copy
3. Run the merge script:
   ```
   cd "C:\Users\sebas\OneDrive\Dokumente\GitHub\ccs-map"
   python catf_merge.py "C:\Users\sebas\Downloads\CATF_CCUS_Database.xlsx" "C:\Users\sebas\Downloads\CCS Projects Europe.xlsx"
   ```
4. The script will:
   - Match projects by name + country (exact match, then fuzzy matching above 80% similarity)
   - Refresh all CATF-sourced columns for matched projects
   - Preserve all F2E enrichment columns (contacts, funding, notes, etc.)
   - Preserve Excel formatting (fonts, colors, column widths)
   - Append any new CATF projects with auto-generated project IDs
   - Flag projects no longer in CATF (but never remove them)
   - Skip manually added projects (source = `Manual`)
5. Review the console output and open the updated Excel to spot-check
6. To write to a separate file instead of overwriting, use `--output`:
   ```
   python catf_merge.py "CATF_download.xlsx" "CCS Projects Europe.xlsx" --output merged_test.xlsx
   ```

## Map features

- Markers sized by capture capacity, colored by subsector
- Border color by status: Operational, Under Construction, In Development, Planned, Research
- Dashed marker border for projects without a confirmed site location (`approximate_location = Yes`)
- Filters: Status, Sector, Subsector, Contact Status, Internal Priority, Storage Type (multi-select)
- Search across project name, entities, country, subsector
- Popups with full project details including contacts, funding, and links

## GitHub Pages setup

Settings → Pages → Source: deploy from `main` branch, `/ (root)` → Save

## Requirements

- `convert_excel_to_csv.py` and `catf_merge.py` require Python 3.8+ with `pandas` and `openpyxl`

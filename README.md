# CCS Projects Europe - Interactive Map

Interactive map tracking 220+ European Carbon Capture and Storage (CCS) projects, maintained by Factor2 Energy.

CATF publishes their own [CCS map for Europe](https://www.catf.us/ccsmapeurope/), which serves as the primary data source for this map. We recreated it for internal use to add more granularity, additional filter options, and Factor2 Energy-specific data (contacts, funding, internal priority, etc.).

**Live map:** `https://seb-hm.github.io/ccs-map/`

## Files

| File | Purpose |
|------|---------|
| `index.html` | Interactive Leaflet map, deployed via GitHub Pages |
| `CCS Projects Europe.xlsx` | Master database - single source of truth |
| `projects.csv` | Auto-generated from Excel by GitHub Action - do not edit manually |
| `convert_excel_to_csv.py` | Conversion script called by the GitHub Action |
| `catf_merge.py` | Script to merge fresh CATF data into the master Excel |
| `.github/workflows/excel_to_csv.yml` | GitHub Action: converts Excel -> CSV on every push |

## Workflow - updating the map

The master database lives on SharePoint as `CCS Projects Europe.xlsx`. To update the map:

1. Edit the Excel on SharePoint
2. Download a copy and replace the file in the local repo folder
3. Push to GitHub:
   ```
   git add "CCS Projects Europe.xlsx"
   git commit -m "Update project data"
   git push
   ```
4. The GitHub Action automatically converts the Excel to `projects.csv` and commits it (~1 min)
5. GitHub Pages picks up the change and the map updates

**Never edit `projects.csv` manually** - it is always overwritten by the Action.

## Workflow - adding a new project

1. Open the master Excel on SharePoint
2. Add a new row with the project data (name, country, coordinates, capacity, status, etc.)
3. Assign a project ID following the existing pattern (e.g. `CCS-224`)
4. Save, download, and replace the file in this repo folder
5. Push to GitHub - the Action will regenerate `projects.csv` automatically

## Workflow - merging an updated CATF database download

When CATF publishes an updated CCS database, merge it into the master Excel:

1. Download the current master Excel from [SharePoint](https://factortwoenergy.sharepoint.com/:f:/s/BusinessDevelopment/IgDt99LdD2EFQ7ZloAzScmihAUVY-r_6PCOgzhr4sEe1_bw?e=TwZszq) (`CCS Projects Europe.xlsx`) and place it in the local repo folder
2. Download the latest CATF database from https://www.catf.us/ccstableeurope/ (e.g. `CATF_CCUS_Database.xlsx`) (Tab "Europe")
3. Run the merge script from the repo folder:
   ```
   python catf_merge.py path/to/CATF_CCUS_Database.xlsx "CCS Projects Europe.xlsx"
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
6. Push the updated Excel to GitHub:
   ```
   git add "CCS Projects Europe.xlsx"
   git commit -m "Merge CATF update YYYY-MM"
   git push
   ```
7. The GitHub Action automatically converts the Excel to `projects.csv` and the map updates (~1 min)
8. Upload the updated Excel back to SharePoint to keep it in sync


## Map features

- Markers sized by capture capacity, colored by subsector
- Border color by status: Operational, Under Construction, In Development, Planned, Research
- Dashed marker border for projects without a confirmed site location (`approximate_location = Yes`)
- Filters: Status, Sector, Subsector, Contact Status, Internal Priority, Storage Type (multi-select)
- Search across project name, entities, country, subsector
- Popups with full project details including contacts, funding, and links


## Requirements

- `convert_excel_to_csv.py` and `catf_merge.py` require Python 3.8+ with `pandas` and `openpyxl`

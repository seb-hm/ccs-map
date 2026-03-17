You are helping maintain a CCS (Carbon Capture and Storage) project database for Factor2 Energy.

The user has pasted raw project information below. Your job is to map it to the Excel database schema and output a row ready to paste into Excel.

## Step 1 — Read the current Excel

Run a node script to extract the column headers and all existing project IDs + names from `CCS Projects Europe.xlsx`:

```js
const XLSX = require('xlsx');
const wb = XLSX.readFile('CCS Projects Europe.xlsx');
const ws = wb.Sheets[wb.SheetNames[0]];
const data = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
const headers = data[0];
const projects = data.slice(1).map(r => ({ id: r[0], name: r[1], country: r[4] }));
console.log('HEADERS:', JSON.stringify(headers));
console.log('PROJECTS:', JSON.stringify(projects));
```

## Step 2 — Determine new or existing

- Search existing projects for a name or ID match (fuzzy match is fine)
- If **existing**: note which row it is and only output columns with new or updated values
- If **new**: assign a project_id following the pattern `XX-NNN` (ISO country code + next available 3-digit number for that country)

## Step 3 — Map the information

Use the pasted text to fill in as many columns as possible. Key mapping rules:

- **project_id**: country ISO code (2 letters) + 3-digit number (e.g. DE-042)
- **Status**: must be one of: `Operational`, `Under Construction`, `In Development`, `Planned`, `Research`
- **Sector Classification**: one of: `Industrial`, `Heat and Power`, `Storage`, `Waste-to-Energy`, `Direct Air Capture`
- **Subsector Classification**: one of: `Cement`, `Hydrogen`, `Storage`, `Biofuels`, `Transport Hub`, `Direct Air Capture`, `Waste-to-Energy`, `Biomass`, `Natural Gas`, `Aluminium`, `Chemical`, `Other Subsector`
- **Storage Classification**: one of: `Dedicated Saline Storage`, `Depleted Oil or Gas Reservoir`, `Depleted Gas Reservoir and Saline Storage`, `Basalt`, `Unknown`
- **Capacity (Metric Tons Per Annum)**: numeric tonnes/year, or `Unknown`
- **Visualized Capacity**: same as Capacity unless unknown, then `0`
- **Approx. Latitude / Longitude**: decimal degrees. If location is approximate (research project, region-level only), set `approximate_location` = `Yes`
- **approximate_location**: `Yes` if no specific site location is known, otherwise leave empty
- **source**: always set to `Manual` for projects added via this command
- Leave any unknown fields empty

## Step 4 — Copy to clipboard and output summary

### Copy row to clipboard
Build the full row as a tab-separated string in the exact column order from the Excel headers (empty fields = empty string between tabs). Then run this node script to write it to a temp file and copy it to the Windows clipboard:

```js
const fs = require('fs');
const { execSync } = require('child_process');
const row = /* tab-separated string */;
fs.writeFileSync('C:/Users/sebas/AppData/Local/Temp/ccs_row.txt', row, 'utf8');
execSync(`powershell -Command "Get-Content 'C:\\Users\\sebas\\AppData\\Local\\Temp\\ccs_row.txt' -Raw | Set-Clipboard"`);
console.log('Copied to clipboard');
```

Confirm the clipboard copy succeeded, then tell the user:
> Row copied to clipboard. Click cell A in the target row and press Ctrl+V.

### Summary (for verification)
Show only the non-empty fields as a compact two-column table:

| Column | Value |
|--------|-------|
| ...    | ...   |

If this is an **existing project**, only show the changed columns in the summary and note which row number to update.

---

## Project information to process:

$ARGUMENTS

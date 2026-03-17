import pandas as pd
import glob
import sys
import openpyxl

def to_str(val):
    if pd.isna(val):
        return ''
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)

xlsx_files = glob.glob('*.xlsx')
if not xlsx_files:
    print("No .xlsx file found — skipping CSV generation.")
    sys.exit(0)

xlsx_file = xlsx_files[0]
print(f"Reading {xlsx_file}...")

# Build a map of (row, col) -> hyperlink URL using openpyxl
wb = openpyxl.load_workbook(xlsx_file)
ws = wb.active
hyperlinks = {}
for row in ws.iter_rows():
    for cell in row:
        if cell.hyperlink and cell.hyperlink.target:
            hyperlinks[(cell.row, cell.column)] = cell.hyperlink.target

df = pd.read_excel(xlsx_file)
for col_idx, col in enumerate(df.columns, start=1):
    def resolve_cell(val, row_idx, col_idx=col_idx):
        url = hyperlinks.get((row_idx + 2, col_idx))  # +2: 1-based + header row
        if url:
            return url
        return to_str(val)
    df[col] = [resolve_cell(val, i) for i, val in enumerate(df[col])]

df.to_csv('projects.csv', sep=';', index=False, encoding='utf-8-sig')
print(f"Converted {len(df)} rows to projects.csv")

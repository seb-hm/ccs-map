import pandas as pd
import glob
import sys

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

df = pd.read_excel(xlsx_file)
for col in df.columns:
    df[col] = df[col].apply(to_str)

df.to_csv('projects.csv', sep=';', index=False, encoding='utf-8-sig')
print(f"Converted {len(df)} rows to projects.csv")

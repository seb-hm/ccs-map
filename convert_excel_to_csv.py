import pandas as pd
import numpy as np

def to_str(val):
    if pd.isna(val):
        return ''
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val)

df = pd.read_excel('CCS Projects Europe.xlsx', sheet_name='CCS Projects Europe')
for col in df.columns:
    df[col] = df[col].apply(to_str)

df.to_csv('projects.csv', sep=';', index=False, encoding='utf-8-sig')
print(f"Converted {len(df)} rows to projects.csv")

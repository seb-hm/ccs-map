#!/usr/bin/env python3
"""
CATF ↔ F2E CCS Database Merge Script
-------------------------------------
Updates CATF-sourced columns from a fresh CATF download while preserving
all F2E enrichment columns (contacts, funding, notes, SharePoint links).

Usage:
    python catf_merge.py <fresh_catf.xlsx> <f2e_database.xlsx> [--output merged.xlsx]

The script matches projects on (Project Name + Country) as the join key.
- Existing projects: CATF columns updated, F2E columns preserved
- New CATF projects: appended with empty F2E columns
- Removed CATF projects: kept in F2E database, flagged in notes
"""

import argparse
import pandas as pd
from datetime import datetime
import sys

CATF_COLUMNS = [
    'Project Name', 'Entities', 'Capture or Storage Details', 'Country', 'Location', 'State',
    'Sector Classification', 'Sector Description', 'Subsector Classification', 'Subsector Description',
    'Approx. Latitude', 'Approx. Longitude',
    'Capacity (Metric Tons Per Annum)',
    'Storage Classification', 'Storage Description',
    'Year Announced', 'Year Operational', 'Status', 'Notes', 'Month Announced', 'Reference'
]

F2E_COLUMNS = [
    'capture_lead_company', 'capture_lead_contact', 'capture_lead_email',
    'storage_lead_company', 'storage_lead_contact', 'storage_lead_email',
    'transport_operator', 'storage_capacity_mt', 'funding_source', 'funding_amount_eur_m',
    'eu_funding_program', 'fid_date', 'contact_status', 'contact_date', 'contact_notes',
    'internal_priority', 'relevance_f2e', 'project_website', 'sharepoint_folder',
    'internal_notes', 'last_updated_f2e', 'updated_by'
]

COUNTRY_CODES = {
    'Belgium': 'BE', 'Bulgaria': 'BG', 'Croatia': 'HR', 'Czechia': 'CZ',
    'Denmark': 'DK', 'Finland': 'FI', 'France': 'FR', 'Germany': 'DE',
    'Greece': 'GR', 'Hungary': 'HU', 'Iceland': 'IS', 'Italy': 'IT',
    'Latvia': 'LV', 'Lithuania': 'LT', 'Netherlands': 'NL', 'Norway': 'NO',
    'Poland': 'PL', 'Romania': 'RO', 'Slovakia': 'SK', 'Spain': 'ES',
    'Sweden': 'SE', 'Switzerland': 'CH', 'UK': 'GB',
}


def _parse_single_number(val):
    """Try to parse val as a single positive number. Returns the float, or None if not possible."""
    if pd.isna(val):
        return None
    s = str(val).strip().replace(',', '').replace(' ', '')
    if not s or s.lower() in ('unknown', 'unavailable', 'n/a', '-'):
        return None
    # Reject ranges (contain a dash that isn't a negative sign at the start)
    if '-' in s.lstrip('-'):
        return None
    try:
        n = float(s)
        return n if n > 0 else None
    except ValueError:
        return None


def normalize_capacity(cap_val, vis_cap_val=None):
    """Resolve best capacity value: prefer Capacity if it's a single number,
    fall back to Visualized Capacity, otherwise return 'Unknown'."""
    n = _parse_single_number(cap_val)
    if n is not None:
        return cap_val  # keep original formatting
    if vis_cap_val is not None:
        n = _parse_single_number(vis_cap_val)
        if n is not None:
            return vis_cap_val
    return 'Unknown'


def make_key(row):
    return f"{str(row.get('Project Name', '')).strip().lower()}|{str(row.get('Country', '')).strip().lower()}"


def merge(catf_path, f2e_path, output_path):
    print(f"Loading fresh CATF data from: {catf_path}")
    catf = pd.read_excel(catf_path, sheet_name='Europe')
    catf = catf.loc[:, ~catf.columns.str.startswith('Unnamed')]
    catf['Status'] = catf['Status'].replace('In development', 'In Development')
    if 'Capacity (Metric Tons Per Annum)' in catf.columns:
        vis_col = 'Visualized Capacity (Metric Tons Per Annum)'
        vis = catf[vis_col] if vis_col in catf.columns else pd.Series([None] * len(catf))
        catf['Capacity (Metric Tons Per Annum)'] = [
            normalize_capacity(c, v) for c, v in zip(catf['Capacity (Metric Tons Per Annum)'], vis)
        ]
    catf['_key'] = catf.apply(make_key, axis=1)
    print(f"  → {len(catf)} projects in fresh CATF file")

    print(f"Loading existing F2E database from: {f2e_path}")
    f2e = pd.read_excel(f2e_path, sheet_name='Projects')
    f2e['_key'] = f2e.apply(make_key, axis=1)
    print(f"  → {len(f2e)} projects in existing F2E database")

    existing_keys = set(f2e['_key'])
    catf_keys = set(catf['_key'])
    new_keys = catf_keys - existing_keys
    removed_keys = existing_keys - catf_keys
    updated_keys = existing_keys & catf_keys

    print(f"\nMerge summary:")
    print(f"  Updated (CATF columns refreshed): {len(updated_keys)}")
    print(f"  New projects to add:              {len(new_keys)}")
    print(f"  In F2E but not in CATF anymore:   {len(removed_keys)}")

    # Update existing rows with fresh CATF data
    catf_lookup = catf.set_index('_key')
    for idx, row in f2e.iterrows():
        key = row['_key']
        if key in catf_lookup.index:
            fresh = catf_lookup.loc[key]
            if isinstance(fresh, pd.DataFrame):
                fresh = fresh.iloc[0]
            for col in CATF_COLUMNS:
                if col in fresh.index:
                    f2e.at[idx, col] = fresh[col]

    # Flag removed projects
    today = datetime.now().strftime('%Y-%m-%d')
    for idx, row in f2e.iterrows():
        if row['_key'] in removed_keys:
            existing_notes = str(row.get('internal_notes', '') or '')
            flag = f"[{today}] No longer in CATF database"
            if flag not in existing_notes:
                f2e.at[idx, 'internal_notes'] = f"{existing_notes} {flag}".strip()

    # Add new projects
    if new_keys:
        max_counters = {}
        for pid in f2e['project_id'].dropna():
            parts = str(pid).split('-')
            if len(parts) == 2:
                cc, num = parts
                max_counters[cc] = max(max_counters.get(cc, 0), int(num))

        new_rows = []
        for _, row in catf.iterrows():
            if row['_key'] in new_keys:
                cc = COUNTRY_CODES.get(row['Country'], 'XX')
                max_counters[cc] = max_counters.get(cc, 0) + 1
                new_row = {'project_id': f"{cc}-{max_counters[cc]:03d}"}
                for col in CATF_COLUMNS:
                    new_row[col] = row.get(col, '')
                for col in F2E_COLUMNS:
                    new_row[col] = ''
                new_rows.append(new_row)

        new_df = pd.DataFrame(new_rows)
        f2e = pd.concat([f2e, new_df], ignore_index=True)
        print(f"\n  Added {len(new_rows)} new projects")

    f2e = f2e.drop(columns=['_key'], errors='ignore')
    f2e.to_excel(output_path, sheet_name='Projects', index=False)
    print(f"\nSaved merged database to: {output_path}")
    print(f"Total projects: {len(f2e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge fresh CATF data into F2E CCS database')
    parser.add_argument('catf_file', help='Path to fresh CATF download (.xlsx)')
    parser.add_argument('f2e_file', help='Path to existing F2E database (.xlsx)')
    parser.add_argument('--output', '-o', default=None, help='Output path (default: overwrites f2e_file)')
    args = parser.parse_args()

    output = args.output or args.f2e_file
    merge(args.catf_file, args.f2e_file, output)

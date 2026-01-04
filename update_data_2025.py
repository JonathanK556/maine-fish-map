"""
Script to update fish stocking data with 2025 data.
- Loads 2025 stocking data
- Merges coordinates from existing data and manually added coordinates
- Combines with permanent species data (pike and char)
- Updates df_updated.csv
- Creates coordinate_reference.csv for future use
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_2025_data(xlsx_path='2025_Stocking.xlsx'):
    """Load and standardize 2025 stocking data."""
    print(f"Loading 2025 data from: {xlsx_path}")
    df = pd.read_excel(xlsx_path)
    
    # Normalize column names to uppercase
    df.columns = df.columns.str.strip().str.upper()
    
    # Map column names to standard names
    column_mapping = {
        'DELIVERYDATE': 'DATE',
        'INCHES': 'SIZE (inch)',
        'QTYDELIVERED': 'QTY',
        'QTYREQUESTED': 'QTY',
        'SPP': 'SPECIES'
    }
    
    # Rename columns
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            if new_name not in df.columns or old_name == new_name:
                df = df.rename(columns={old_name: new_name})
    
    # Handle QTY - use QTYDELIVERED if available, otherwise QTYREQUESTED
    if 'QTYDELIVERED' in df.columns and 'QTY' not in df.columns:
        df['QTY'] = df['QTYDELIVERED']
    elif 'QTYREQUESTED' in df.columns and 'QTY' not in df.columns:
        df['QTY'] = df['QTYREQUESTED']
    
    # Map species codes to full names
    species_code_mapping = {
        'BKT': 'BROOK TROUT',
        'RBT': 'RAINBOW TROUT',
        'LKT': 'LAKE TROUT',
        'BNT': 'BROWN TROUT',
        'LLS': 'L.L. SALMON',
        'SPK': 'SPLAKE'
    }
    
    if 'SPECIES' in df.columns:
        df['SPECIES'] = df['SPECIES'].str.strip().str.upper().map(
            lambda x: species_code_mapping.get(x, x) if pd.notna(x) else x
        )
    
    # Select only required columns: TOWN, DATE, WATER, COUNTY, SPECIES, QTY, SIZE (inch)
    required_columns = ['TOWN', 'DATE', 'WATER', 'COUNTY', 'SPECIES', 'QTY', 'SIZE (inch)']
    
    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            print(f"Warning: Column '{col}' not found - added as None")
    
    # Select only required columns
    df_clean = df[required_columns].copy()
    
    print(f"  Loaded {len(df_clean)} rows")
    print(f"  Species: {sorted(df_clean['SPECIES'].dropna().unique())}")
    
    return df_clean

def load_existing_coordinates(df_current_path='df_updated.csv'):
    """Load coordinate lookup from existing data."""
    print(f"\nLoading existing coordinates from: {df_current_path}")
    df_current = pd.read_csv(df_current_path)
    
    coord_lookup = {}
    for _, row in df_current.iterrows():
        if pd.notna(row['X_coord']) and pd.notna(row['Y_coord']):
            key = (str(row['WATER']).strip().upper(), str(row['TOWN']).strip().upper())
            coord_lookup[key] = (float(row['X_coord']), float(row['Y_coord']))
    
    print(f"  Found coordinates for {len(coord_lookup)} unique waterbody/town combinations")
    return coord_lookup

def load_manual_coordinates(csv_path='missing_coordinates_2025.csv'):
    """Load manually added coordinates."""
    print(f"\nLoading manual coordinates from: {csv_path}")
    df_manual = pd.read_csv(csv_path)
    
    manual_coords = {}
    for _, row in df_manual.iterrows():
        if pd.notna(row['X_coord']) and pd.notna(row['Y_coord']):
            key = (str(row['WATER']).strip().upper(), str(row['TOWN']).strip().upper())
            manual_coords[key] = (float(row['X_coord']), float(row['Y_coord']))
    
    print(f"  Found {len(manual_coords)} manually added coordinates")
    return manual_coords

def merge_coordinates(df, existing_coords, manual_coords):
    """Merge coordinates into dataframe."""
    print("\nMerging coordinates...")
    df['X_coord'] = None
    df['Y_coord'] = None
    
    for idx, row in df.iterrows():
        key = (str(row['WATER']).strip().upper(), str(row['TOWN']).strip().upper())
        
        # Prioritize manual coordinates, then existing
        if key in manual_coords:
            df.at[idx, 'X_coord'] = manual_coords[key][0]
            df.at[idx, 'Y_coord'] = manual_coords[key][1]
        elif key in existing_coords:
            df.at[idx, 'X_coord'] = existing_coords[key][0]
            df.at[idx, 'Y_coord'] = existing_coords[key][1]
    
    # Count coordinates
    has_coords = df['X_coord'].notna() & df['Y_coord'].notna()
    print(f"  Rows with coordinates: {has_coords.sum()}")
    print(f"  Rows missing coordinates: {(~has_coords).sum()}")
    
    return df

def get_permanent_species(df_current_path='df_updated.csv'):
    """Get permanent species data (pike and char) to keep."""
    print(f"\nLoading permanent species data from: {df_current_path}")
    df_current = pd.read_csv(df_current_path)
    
    permanent_species = ['NORTHERN PIKE', 'ARCTIC CHAR']
    permanent_data = df_current[df_current['SPECIES'].isin(permanent_species)].copy()
    
    print(f"  Found {len(permanent_data)} rows of permanent species data")
    print(f"  Species: {sorted(permanent_data['SPECIES'].unique())}")
    
    return permanent_data

def combine_data(df_2025, permanent_data):
    """Combine 2025 data with permanent species data."""
    print("\nCombining 2025 data with permanent species data...")
    
    # Ensure both have same columns
    all_columns = set(df_2025.columns) | set(permanent_data.columns)
    
    # Add missing columns
    for col in all_columns:
        if col not in df_2025.columns:
            df_2025[col] = None
        if col not in permanent_data.columns:
            permanent_data[col] = None
    
    # Column order: COUNTY, DATE, WATER, TOWN, SPECIES, QTY, SIZE (inch), X_coord, Y_coord, ABUNDANCE
    column_order = ['COUNTY', 'DATE', 'WATER', 'TOWN', 'SPECIES', 'QTY', 'SIZE (inch)', 'X_coord', 'Y_coord', 'ABUNDANCE']
    available_columns = [col for col in column_order if col in all_columns]
    remaining_columns = [col for col in all_columns if col not in available_columns]
    final_column_order = available_columns + remaining_columns
    
    # Combine
    combined = pd.concat([df_2025, permanent_data], ignore_index=True)
    combined = combined[final_column_order]
    
    print(f"  Combined dataset has {len(combined)} rows")
    print(f"  Species breakdown:")
    print(combined['SPECIES'].value_counts().to_string())
    
    return combined

def create_coordinate_reference(df):
    """Create coordinate reference file with all unique coordinates."""
    print("\nCreating coordinate reference file...")
    
    # Get all unique locations with coordinates
    coord_ref = df[df['X_coord'].notna() & df['Y_coord'].notna()][
        ['WATER', 'TOWN', 'COUNTY', 'X_coord', 'Y_coord']
    ].drop_duplicates(subset=['WATER', 'TOWN', 'COUNTY'])
    
    # Sort by county, town, water
    coord_ref = coord_ref.sort_values(['COUNTY', 'TOWN', 'WATER']).reset_index(drop=True)
    
    print(f"  Created reference with {len(coord_ref)} unique locations")
    
    return coord_ref

def main():
    """Main function to update data."""
    print("=" * 80)
    print("UPDATING DATA WITH 2025 STOCKING DATA")
    print("=" * 80)
    
    # Load 2025 data
    df_2025 = load_2025_data('2025_Stocking.xlsx')
    
    # Load coordinates
    existing_coords = load_existing_coordinates('df_updated.csv')
    manual_coords = load_manual_coordinates('missing_coordinates_2025.csv')
    
    # Merge coordinates
    df_2025_with_coords = merge_coordinates(df_2025, existing_coords, manual_coords)
    
    # Get permanent species
    permanent_data = get_permanent_species('df_updated.csv')
    
    # Combine data
    df_updated = combine_data(df_2025_with_coords, permanent_data)
    
    # Create coordinate reference
    coord_reference = create_coordinate_reference(df_updated)
    
    # Save files
    print("\n" + "=" * 80)
    print("SAVING FILES")
    print("=" * 80)
    
    output_csv = 'df_updated.csv'
    print(f"\nSaving updated data to: {output_csv}")
    df_updated.to_csv(output_csv, index=False)
    print(f"  ✅ Saved {len(df_updated)} rows")
    
    coord_ref_csv = 'coordinate_reference.csv'
    print(f"\nSaving coordinate reference to: {coord_ref_csv}")
    coord_reference.to_csv(coord_ref_csv, index=False)
    print(f"  ✅ Saved {len(coord_reference)} unique locations")
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE!")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Total rows in df_updated.csv: {len(df_updated)}")
    print(f"  Unique locations with coordinates: {len(coord_reference)}")
    print(f"  Rows missing coordinates: {len(df_updated[df_2025_with_coords['X_coord'].isna()])}")
    
    return df_updated, coord_reference

if __name__ == "__main__":
    df_updated, coord_reference = main()


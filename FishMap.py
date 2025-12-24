#Libraries
import pandas as pd
import folium
import random
import streamlit as st
from streamlit_folium import st_folium

# Load the dataframe in FishMap.py
df_updated = pd.read_csv("df_updated.csv")

map_center = [44.6939, -69.3815]
m = folium.Map(location=map_center, zoom_start=7)

# Function to create and cache the base map
@st.cache_data
def create_base_map():
    return folium.Map(location=map_center, zoom_start=7)

# Function to filter data based on criteria
@st.cache_data
def filter_data(selected_species, show_spring, show_fall, search_term, min_qty):
    # Group data by water body, town, and county
    grouped = df_updated.groupby(['WATER', 'TOWN', 'COUNTY'])
    
    filtered_groups = []
    for (water_name, town_name, county_name), group in grouped:
        # Check if the search term is in any of the fields (water, town, or county)
        if (search_term.lower() in water_name.lower() or
            search_term.lower() in town_name.lower() or
            search_term.lower() in county_name.lower()):
            
            # Filter data by species and date (Spring/Fall)
            filtered_rows = []
            for _, row in group.iterrows():
                # Handle empty DATE for non-stocked species (like pike)
                date_str = str(row['DATE']).strip()
                has_date = date_str != '' and date_str.lower() != 'nan'
                
                # Check season filter (only applies if date exists)
                season_match = True
                if has_date and (show_spring or show_fall):  # Only apply season filter if at least one is selected and date exists
                    try:
                        month = pd.to_datetime(row['DATE']).month
                        season_match = (show_spring and month <= 6) or (show_fall and month >= 7)
                    except:
                        season_match = True  # If date parsing fails, show the record
                
                # Handle empty QTY for non-stocked species (like pike)
                qty_value = row['QTY']
                if pd.isna(qty_value) or str(qty_value).strip() == '':
                    qty_value = 0  # Default to 0 for empty quantities
                else:
                    try:
                        qty_value = float(qty_value)
                    except:
                        qty_value = 0
                
                # Check species and quantity filters
                if (row['SPECIES'] in selected_species and 
                    qty_value >= min_qty and 
                    season_match):
                    filtered_rows.append({
                        'species': row['SPECIES'],
                        'qty': qty_value if qty_value > 0 else 'N/A',
                        'size': row['SIZE (inch)'] if pd.notna(row['SIZE (inch)']) and str(row['SIZE (inch)']).strip() != '' else 'N/A',
                        'date': row['DATE'] if has_date else 'N/A (Not Stocked)'
                    })
            
            # Only include groups that have filtered data
            if filtered_rows:
                filtered_groups.append({
                    'water_name': water_name,
                    'town_name': town_name,
                    'county_name': county_name,
                    'group': group,
                    'filtered_rows': filtered_rows
                })
    
    return filtered_groups

# Function to update the map based on selected species, date filters (Spring/Fall), and search
def update_map(selected_species, show_spring, show_fall, search_term, min_qty):
    # Get cached base map
    m = create_base_map()
    
    # Get filtered data
    filtered_groups = filter_data(selected_species, show_spring, show_fall, search_term, min_qty)
    
    # Add markers to the map
    for group_data in filtered_groups:
        water_name = group_data['water_name']
        town_name = group_data['town_name']
        county_name = group_data['county_name']
        group = group_data['group']
        filtered_rows = group_data['filtered_rows']
        
        # Create popup text
        popup_text = f"""
        <b>Water Body:</b> {water_name}<br>
        <b>Town:</b> {town_name}<br>
        <b>County:</b> {county_name}<br>
        <b>Stocking Data:</b><br>
        <ul>
        """
        for row in filtered_rows:
            # Format the popup text based on whether it's stocked or naturally occurring
            if row['date'] == 'N/A (Not Stocked)':
                popup_text += f"""
            <li><b>{row['species']}</b> - Naturally occurring (not stocked)</li>
            """
            else:
                popup_text += f"""
            <li><b>{row['species']}</b> - {row['qty']} fish, Size: {row['size']} inches, Date: {row['date']}</li>
            """
        popup_text += "</ul>"

        # Use the average coordinates of the water body/town combination
        avg_x = group['X_coord'].mean()
        avg_y = group['Y_coord'].mean()

        # Offset coordinates slightly if there are multiple towns associated with the same water body
        offset_x = random.uniform(-0.001, 0.001)  # Random offset for longitude
        offset_y = random.uniform(-0.001, 0.001)  # Random offset for latitude

        # Add a single marker for the water body/town combo with grouped popup data
        folium.Marker(
            location=[avg_y + offset_y, avg_x + offset_x],  # Apply offset to average coordinates
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='green')  # Popup with the grouped stocking data
        ).add_to(m)

    return m

# List of unique species in your dataset
species_list = df_updated['SPECIES'].unique()

# Streamlit Widgets
st.title("Fish Stocking Data Visualization")

# map_center = [44.6939, -69.3815]
# m_test = folium.Map(location=map_center, zoom_start=6)

# st_folium(m_test, width=800, height=600)

# Create checkboxes for each species
selected_species = st.multiselect(
    'Select Species:', species_list, default=species_list.tolist())  # Start with all species selected

# Create checkboxes for Spring and Fall Stocking
show_spring = st.checkbox('Spring Stocking (Jan-Jun)', value=False)
show_fall = st.checkbox('Fall Stocking (Jul-Dec)', value=False)

# Add info text about season filtering
if not show_spring and not show_fall:
    st.info("💡 Select Spring or Fall to filter by season, or leave both unchecked to show all data.")

# Create a search bar to filter by water body, town, or county
search_term = st.text_input('Search by Water Body, Town, or County:', '')

# Create a text box for users to enter the minimum quantity of fish
min_qty_text = st.text_input('Enter Minimum Quantity of Fish:', '0')  # Default to 0 if not entered

# Convert min_qty_text to integer, ensuring it's valid
try:
    min_qty = int(min_qty_text)
except ValueError:
    min_qty = 0  # If the input is not a number, default to 0

# Generate and display the map with better caching
@st.cache_data
def get_cached_map(selected_species_tuple, show_spring, show_fall, search_term, min_qty):
    return update_map(list(selected_species_tuple), show_spring, show_fall, search_term, min_qty)

# Convert to tuple for caching
selected_species_tuple = tuple(selected_species)

# Get cached map
cached_map = get_cached_map(selected_species_tuple, show_spring, show_fall, search_term, min_qty)

# Display the map
st_folium(cached_map, width=800, height=600, returned_objects=[])

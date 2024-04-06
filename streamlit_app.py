import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static  
import numpy as np

# Assuming 'test.json' is loaded into 'df'
# Load data
df = pd.read_json('test.json')

# Convert 'Month' from name to number for consistency
df['Month'] = pd.to_datetime(df['Month'], format='%B').dt.month

# Ensure 'Day' and 'Year' are zero-padded and handled correctly
df['Day'] = df['Day'].apply(lambda x: f"{x:02d}")
df['Year'] = df['Year'].apply(lambda x: f"{x}" if len(str(x)) == 4 else f"20{x}")

# Attempt to combine and parse the DateTime column
try:
    df['DateTime'] = pd.to_datetime(df[['Year', 'Month', 'Day']].astype(str).agg('-'.join, axis=1) + ' ' + df['Time'])
except ValueError as e:
    st.error(f"Error parsing DateTime: {e}")

# Sidebar for event selection
option = st.sidebar.radio('Choose an event:', df['BattleName'].unique())

# Filter data based on the selected event
filtered_data = df[df['BattleName'] == option]

# Function to display the map with markers and lines for each RouteID
def display_map(data):
    m = folium.Map(location=[20, -100], zoom_start=4)
    
    # Different colors for different RouteIDs
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
              'gray', 'black', 'lightgray']

    # Group by RouteID and draw lines
    for route_id, group in data.groupby('RouteID'):
        color = colors[route_id % len(colors)]  # Cycle through colors if more RouteIDs than colors
        locations = group[['Latitude', 'Longitude']].values
        folium.PolyLine(locations, color=color, weight=2.5, opacity=1).add_to(m)
        
        # Add markers
        for _, row in group.iterrows():
            folium.Marker([row['Latitude'], row['Longitude']],
                          popup=f"{row['KeyEventNotes']}",
                          tooltip=f"Time: {row['DateTime']}").add_to(m)

    if not data.empty:
        locations = data[['Latitude', 'Longitude']]
        m.fit_bounds([[locations['Latitude'].min(), locations['Longitude'].min()],
                      [locations['Latitude'].max(), locations['Longitude'].max()]])

    folium_static(m)

# Handling different functionalities based on user selection
view_option = st.sidebar.radio("View Options:", ["Select KeyEventNote", "Show All KeyEventNotes", "Select Time"], key='view_option')

if view_option == "Select KeyEventNote":
    key_event_note_select = st.sidebar.selectbox("Select KeyEventNote:", filtered_data['KeyEventNotes'].unique(), key='key_event_select')
    selected_data = filtered_data[filtered_data['KeyEventNotes'] == key_event_note_select]
    display_map(selected_data)
elif view_option == "Show All KeyEventNotes":
    display_map(filtered_data)   
elif view_option == "Select Time":
    time_options = filtered_data['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S').sort_values().unique()
    selected_time = st.sidebar.select_slider('Select Time:', options=time_options, key='time_select')
    selected_data = filtered_data[filtered_data['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S') == selected_time]
    display_map(selected_data)

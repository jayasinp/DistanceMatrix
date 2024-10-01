import geopandas as gpd
import pandas as pd
import requests

# Step 1: Load the polling place data
polling_places_shapefile = 'Data/final_polling_places_with_sa1.shp'
polling_place_data = gpd.read_file(polling_places_shapefile)

# Step 2: Extract Fitzroy polling places using case-insensitive matching
fitzroy_polling_places = polling_place_data[polling_place_data['Suburb'].str.upper() == 'FITZROY']

# Step 3: Define the central point for the 3065 postcode (approximate center of Fitzroy)
postcode_center_lat = -37.8044  # Example latitude of 3065
postcode_center_lon = 144.9784  # Example longitude of 3065

# Step 4: Prepare Google Distance Matrix API request
api_key = 'AIzaSyBGKZ-ES236NXh6qcZO2uCRjDpS1d66f3A'  # Replace with your actual API key
base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

# Collect the polling place coordinates
polling_coords = [(row.geometry.y, row.geometry.x) for idx, row in fitzroy_polling_places.iterrows()]

# Step 5: Calculate distances and travel times using Google Distance Matrix API
distances = []
durations = []
for lat, lon in polling_coords:
    # Format the destination as a string
    destination = f"{lat},{lon}"
    
    # Define parameters for the API request
    params = {
        'origins': f"{postcode_center_lat},{postcode_center_lon}",
        'destinations': destination,
        'key': api_key,
        'mode': 'walking'  # Can change to 'driving', 'bicycling', or 'transit'
    }
    
    # Send the API request
    response = requests.get(base_url, params=params)
    result = response.json()
    
    # Print the full response for debugging purposes
    if response.status_code != 200:
        print(f"Error: Received response status code {response.status_code}")
    print(f"API Response for destination ({lat}, {lon}): {result}")

    # Extract the distance and duration from the response
    try:
        distance_text = result['rows'][0]['elements'][0]['distance']['text']
        distance_value = result['rows'][0]['elements'][0]['distance']['value']
        duration_text = result['rows'][0]['elements'][0]['duration']['text']
        duration_value = result['rows'][0]['elements'][0]['duration']['value']
        
        # Store the extracted data
        distances.append((distance_text, distance_value))
        durations.append((duration_text, duration_value))
        
        # Print the travel time information to the terminal
        print(f"Destination ({lat}, {lon}):")
        print(f"  Distance: {distance_text} ({distance_value} meters)")
        print(f"  Travel Time: {duration_text} ({duration_value} seconds)")
    except (KeyError, IndexError):
        # Handle cases where the API response is not as expected
        distances.append((None, None))
        durations.append((None, None))
        print(f"Destination ({lat}, {lon}): Error retrieving data")

# Step 6: Save the polling place, distance, and travel time data to a CSV file
output_csv_path = 'generated/fitzroy_polling_places_distances_times.csv'
output_data = pd.DataFrame({
    'Polling_Place_ID': fitzroy_polling_places.index,
    'Polling_Place_PostCode': fitzroy_polling_places['PostCode'],
    'Polling_Place_Name': fitzroy_polling_places['PollNm'],
    'Polling_Place_Address': fitzroy_polling_places['Addr1'],
    'Polling_Place_Lat': [lat for lat, lon in polling_coords],
    'Polling_Place_Lon': [lon for lat, lon in polling_coords],
    'Distance_Text': [dist[0] for dist in distances],
    'Distance_Value': [dist[1] for dist in distances],  # Distance in meters
    'Duration_Text': [dur[0] for dur in durations],
    'Duration_Value': [dur[1] for dur in durations]  # Duration in seconds
})

# Save to CSV
output_data.to_csv(output_csv_path, index=False)
print(f"\nCSV file with distances and travel times exported successfully to: {output_csv_path}")

import marimo

__generated_with = "0.8.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import geopandas as gpd
    return gpd, mo


@app.cell
def __(gpd):
    # Load the SA1 shapefile (one with all the SA1 boundaries)
    sa1_data = gpd.read_file('Data/SA1_2021_AUST_GDA2020.shp')
    print(sa1_data.columns)
    return sa1_data,


@app.cell
def __(gpd):
    # Load the polling place data (one with all the dots of polling places)
    polling_place_data = gpd.read_file('Data/final_polling_places_with_sa1.shp')
    print(polling_place_data.columns)
    return polling_place_data,


@app.cell
def __(polling_place_data):
    # Extract the Melbourne CBD polling places
    melbourne_cbd_postcodes = [3032, 3051, 3052, 3004, 3207, 3003, 3050, 3053, 3005, 3006, 3054, 3008, 3000, 3010, 3141, 3002, 3031]
    # Filter the polling places
    melbourne_cbd_polling_places = polling_place_data[polling_place_data['PostCode'].isin(melbourne_cbd_postcodes)]
    print(melbourne_cbd_polling_places.head())
    return melbourne_cbd_polling_places, melbourne_cbd_postcodes


@app.cell
def __(melbourne_cbd_polling_places, sa1_data):
    # Quick visualisation
    import matplotlib.pyplot as plt
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 10))
    sa1_data.plot(ax=ax, color='lightgrey')  # SA1 boundaries in light grey
    melbourne_cbd_polling_places.plot(ax=ax, markersize=5, color='red')  # Polling places in red

    ax.set_title('Polling Places in Melbourne CBD Over SA1 Boundaries')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    plt.show()
    # pretty worthless visualisation, I'll use QGIS instead
    return ax, fig, plt


@app.cell
def __(melbourne_cbd_polling_places):
    # QGIS shapefile exporter to visualise the CBD booths
    # Export melbourne CBD polling booths as shapefile
    import os 

    output_directory = 'generated'
    # Define the path where you want to save the shapefile
    output_path = 'generated/melbourne_cbd_polling_places.shp'

    # Export the data
    melbourne_cbd_polling_places.to_file(output_path, driver='ESRI Shapefile')

    print("Shapefile exported successfully to:", output_path)
    return os, output_directory, output_path


@app.cell
def __(gpd):
    # Do a spatial join between the CBD polling places post codes and the SA1 regions
    import pandas as pd
    from shapely.geometry import Point

    # Load postcode data
    postcode_data = pd.read_csv('Data/postcodes.csv')
    postcode_data[['Latitude', 'Longitude']] = postcode_data['Geo Point'].str.split(',', expand=True).astype(float)

    # Convert postcode data into a GeoDataFrame
    geometry = [Point(xy) for xy in zip(postcode_data['Longitude'], postcode_data['Latitude'])]
    postcode_gdf = gpd.GeoDataFrame(postcode_data, geometry=geometry, crs='EPSG:4326')

    # Convert to a projected CRS (UTM zone 55S) before calculating centroids
    postcode_gdf = postcode_gdf.to_crs(epsg=32755)  # Change CRS to a suitable UTM zone
    postcode_gdf['centroid'] = postcode_gdf['geometry'].centroid  # Calculate centroids in the UTM zone

    # Convert centroids back to geographic coordinates (Lat/Long) for further use with APIs etc.
    postcode_gdf['centroid'] = postcode_gdf['centroid'].to_crs(epsg=4326)

    print(postcode_gdf[['centroid']])
    return Point, geometry, pd, postcode_data, postcode_gdf


@app.cell
def __(GeoDataFrame, Point, centroids_coords, pd, polling_coords):
    # Convert the centroid coordinates and polling booth coordinates into GeoSeries
    centroids_geom = GeoDataFrame(geometry=[Point(x, y) for y, x in centroids_coords], crs='EPSG:4326')
    polling_geom = GeoDataFrame(geometry=[Point(x, y) for y, x in polling_coords], crs='EPSG:4326')

    # Convert both to a common projected CRS for accurate distance calculations
    centroids_geom = centroids_geom.to_crs(epsg=32755)  # Use UTM zone 55S
    polling_geom = polling_geom.to_crs(epsg=32755)

    # Initialize an empty list to store distances
    distances_list = []

    # Iterate over each centroid and polling place, calculating the distance
    for centroid_index, centroid in centroids_geom.iterrows():
        for polling_index, polling_place in polling_geom.iterrows():
            distance = centroid.geometry.distance(polling_place.geometry)
            distances_list.append({
                'Centroid_ID': centroid_index,
                'Polling_Place_ID': polling_index,
                'Distance_m': distance  # Distance in meters
            })

    # Convert the list of distances to a DataFrame
    distances_df = pd.DataFrame(distances_list)

    # Save to CSV
    output_csv_path = 'generated/distances_between_centroids_and_polling_booths.csv'
    distances_df.to_csv(output_csv_path, index=False)

    print(f"CSV file with distances exported successfully to: {output_csv_path}")
    return (
        centroid,
        centroid_index,
        centroids_geom,
        distance,
        distances_df,
        distances_list,
        output_csv_path,
        polling_geom,
        polling_index,
        polling_place,
    )


@app.cell
def __():
    # Google API 
    import requests

    def build_distance_matrix_url(origins, destinations, api_key):
        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        origins_param = '|'.join([f"{lat},{lon}" for lon, lat in origins])
        destinations_param = '|'.join([f"{lat},{lon}" for lon, lat in destinations])
        params = {
            'origins': origins_param,
            'destinations': destinations_param,
            'key': api_key
        }
        response = requests.get(base_url, params=params)
        return response.json()
    return build_distance_matrix_url, requests


@app.cell
def __(melbourne_cbd_polling_places, postcode_gdf):
    # Extracting centroid coordinates
    centroids_coords = [(row.geometry.y, row.geometry.x) for idx, row in postcode_gdf.iterrows()]

    # Extracting polling place coordinates
    polling_coords = [(row.Lat, row.Long) for idx, row in melbourne_cbd_polling_places.iterrows()]
    return centroids_coords, polling_coords


@app.cell
def __(build_distance_matrix_url, centroids_coords, polling_coords):
    # make API call
    api_key = 'AIzaSyDDA6VE9XoVgDdnhm2N7WT_TO3zrvVzXmU'  # Use your actual API key
    results = build_distance_matrix_url(centroids_coords, polling_coords, api_key)
    print(results)
    return api_key, results


@app.cell
def __(results):
    def parse_distance_results(results):
        distances = []
        for origin_idx, origin in enumerate(results['rows']):
            row = []
            for dest_idx, destination in enumerate(origin['elements']):
                if destination['status'] == 'OK':
                    row.append(destination['distance']['value'])  # Change 'distance' to 'duration' if time is needed
                else:
                    row.append(None)
            distances.append(row)
        return distances

    distances = parse_distance_results(results)
    return distances, parse_distance_results


if __name__ == "__main__":
    app.run()

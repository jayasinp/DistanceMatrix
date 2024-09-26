import marimo

__generated_with = "0.8.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Point
    import os

    # Load the SA1 shapefile (one with all the SA1 boundaries)
    sa1_data = gpd.read_file('Data/SA1_2021_AUST_GDA2020.shp')
    print(sa1_data.columns)

    # Load the polling place data (one with all the dots of polling places)
    polling_place_data = gpd.read_file('Data/final_polling_places_with_sa1.shp')
    print(polling_place_data.columns)

    # Extract the Melbourne CBD polling places
    melbourne_cbd_postcodes = [3032, 3051, 3052, 3004, 3207, 3003, 3050, 3053, 3005, 3006, 3054, 3008, 3000, 3010, 3141, 3002, 3031]
    # Filter the polling places
    melbourne_cbd_polling_places = polling_place_data[polling_place_data['PostCode'].isin(melbourne_cbd_postcodes)]
    print(melbourne_cbd_polling_places.head())

    # Export Melbourne CBD polling booths as shapefile for QGIS
    output_directory = 'generated'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_path = os.path.join(output_directory, 'melbourne_cbd_polling_places.shp')
    melbourne_cbd_polling_places.to_file(output_path, driver='ESRI Shapefile')
    print("Shapefile exported successfully to:", output_path)

    # Load postcode data and convert to GeoDataFrame
    postcode_data = pd.read_csv('Data/postcodes.csv')
    postcode_data[['Latitude', 'Longitude']] = postcode_data['Geo Point'].str.split(',', expand=True).astype(float)
    geometry = [Point(xy) for xy in zip(postcode_data['Longitude'], postcode_data['Latitude'])]
    postcode_gdf = gpd.GeoDataFrame(postcode_data, geometry=geometry, crs='EPSG:4326')

    # Convert to a projected CRS (UTM zone 55S) before calculating centroids
    postcode_gdf = postcode_gdf.to_crs(epsg=32755)
    postcode_gdf['centroid'] = postcode_gdf['geometry'].centroid

    # Convert centroids back to geographic coordinates (Lat/Long)
    postcode_gdf['centroid'] = postcode_gdf['centroid'].to_crs(epsg=4326)
    print(postcode_gdf[['centroid']])

    # Convert the centroid coordinates and polling booth coordinates into GeoDataFrames
    centroids_geom = gpd.GeoDataFrame(postcode_gdf[['name', 'geometry', 'centroid']], geometry=postcode_gdf['centroid'], crs='EPSG:4326')
    polling_geom = gpd.GeoDataFrame(melbourne_cbd_polling_places[['PostCode', 'PremNm', 'Addr1', 'geometry']], geometry=melbourne_cbd_polling_places['geometry'], crs='EPSG:4326')

    # Convert both to a common projected CRS for accurate distance calculations
    centroids_geom = centroids_geom.to_crs(epsg=32755)
    polling_geom = polling_geom.to_crs(epsg=32755)

    # Initialize an empty list to store distances
    distances_list = []

    # Iterate over each centroid and polling place, calculating the distance
    for centroid_index, centroid in centroids_geom.iterrows():
        for polling_index, polling_place in polling_geom.iterrows():
            distance = centroid.geometry.distance(polling_place.geometry)
            distances_list.append({
                'Centroid_ID': centroid_index,
                'Centroid_Name': centroid['name'],
                'Centroid_Lat': centroid['centroid'].y,
                'Centroid_Lon': centroid['centroid'].x,
                'Polling_Place_ID': polling_index,
                'Polling_Place_PostCode': polling_place['PostCode'],
                'Polling_Place_Name': polling_place['PremNm'],
                'Polling_Place_Address': polling_place['Addr1'],
                'Distance_m': distance  # Distance in meters
            })

    # Convert the list of distances to a DataFrame
    distances_df = pd.DataFrame(distances_list)

    # Save to CSV
    output_csv_path = os.path.join(output_directory, 'distances_between_centroids_and_polling_booths.csv')
    distances_df.to_csv(output_csv_path, index=False)

    print(f"CSV file with distances exported successfully to: {output_csv_path}")
    return (
        Point,
        centroid,
        centroid_index,
        centroids_geom,
        distance,
        distances_df,
        distances_list,
        geometry,
        gpd,
        melbourne_cbd_polling_places,
        melbourne_cbd_postcodes,
        mo,
        os,
        output_csv_path,
        output_directory,
        output_path,
        pd,
        polling_geom,
        polling_index,
        polling_place,
        polling_place_data,
        postcode_data,
        postcode_gdf,
        sa1_data,
    )


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()

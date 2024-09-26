import marimo

__generated_with = "0.8.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import pandas as pd 
    import googlemaps

    file_path = 'generated/distances_between_centroids_and_polling_booths.csv'
    data = pd.read_csv(file_path)

    api_key = 'AIzaSyBGKZ-ES236NXh6qcZO2uCRjDpS1d66f3A'
    gmaps = googlemaps.Client(key=api_key)

    def get_travel_time(lat, lon, address):
        origin = f"{lat},{lon}"
        try:
            result = gmaps.distance_matrix(origins=origin, destinations=address, mode='driving')
            # Print the entire result for debugging
            print(result)
            
            # Check if the status of the request is OK
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                travel_time = result['rows'][0]['elements'][0]['duration']['value']
                return travel_time / 60  # Convert seconds to minutes
            else:
                print(f"Error in API response: {result['rows'][0]['elements'][0]['status']}")
                return None
        except Exception as e:
            print(f"Error calculating travel time: {e}")
            return None
            
    data['Travel_Time_Minutes'] = data.apply(lambda row: get_travel_time(row['Centroid_Lat'], row['Centroid_Lon'], row['Polling_Place_Address']), axis=1)

    output_file_path = '/generated'
    data.to_csv(output_file_path, index=False)

    import ace_tools as tools; tools.display_dataframe_to_user(name="Travel Times Data", dataframe=data)

    return (
        api_key,
        data,
        file_path,
        get_travel_time,
        gmaps,
        googlemaps,
        mo,
        output_file_path,
        pd,
        tools,
    )


if __name__ == "__main__":
    app.run()

import geopandas as gpd
import os
import sys

def extract_postcode_data(shapefile_path, postcode, output_dir="generated"):
    # Load the shapefile using GeoPandas
    gdf = gpd.read_file(shapefile_path)
    
    # List the columns in the shapefile for inspection
    print("Columns in the shapefile:", gdf.columns)

    # Replace 'postcode' with the appropriate column name
    postcode_column = 'postcode'  # Replace with the correct column name, e.g., 'POSTCODE', 'SA1_MAINCODE', etc.
    
    # Check if the column exists in the shapefile
    if postcode_column not in gdf.columns:
        print(f"Error: The column '{postcode_column}' does not exist in the shapefile.")
        return

    # Filter for the specified postcode
    postcode_data = gdf[gdf[postcode_column] == str(postcode)]
    
    # Create the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the extracted data to a CSV file in the specified output directory
    output_filename = os.path.join(output_dir, f"{postcode}postcode.csv")
    postcode_data.to_csv(output_filename, index=False)
    print(f"Postcode data for {postcode} saved to {output_filename}")

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python postcode_data_extractor.py <shapefile_path> <postcode>")
        sys.exit(1)
    
    # Get the shapefile path and postcode from command line arguments
    shapefile_path = sys.argv[1]
    postcode = sys.argv[2]

    # Extract and save the postcode data
    extract_postcode_data(shapefile_path, postcode)


"""
usage in terminal is:
python postcode_data_extractor.py <path_to_shapefile> <postcode>
"""
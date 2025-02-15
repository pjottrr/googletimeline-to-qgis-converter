# googletimeline-to-qgis-converter
converting the google json data exported from timeline data ( from your device) to something usefull to import as vectorlayer in qgis

# Location History to GeoJSON Converter  

This script was developed to address the challenge of visualizing Google Timeline data on maps, particularly in software like QGIS. Google Timeline exports are no longer directly compatible with many mapping tools, prompting the creation of this converter.

## Purpose

The primary goal of this script is to convert location data exported from Google Timeline (in JSON format) into a GeoJSON file. This allows users to load the data into QGIS or other GIS software for further analysis and visualization.
There used to be options to export data via google-out but since the locationhistory is now only available on your device, and the storage type has changed much compared the old data from google-out , i decided to create this script.


## Features

- Extracts points and lines from Google Timeline JSON exports.
- Converts the extracted data into GeoJSON format.
- Handles timestamps for both points and lines, ensuring temporal accuracy.
- Supports debugging to inspect JSON structure during processing.

## Requirements

- Python 3.6 or later
- No additional libraries are required (relies on Python's standard library).

## Usage

1. **Export your location history** from your Android device:
   - Navigate to **Settings > Location > Location Services > Timeline > Export Timeline Data**, or a similar path depending on your device.
   - This will save a JSON file containing your timeline data to your device.

2. **Transfer the file to your computer** for processing.

3. **Run the script**:
   ```bash
   python location_history_json_converter.py <input_file.json> <output_file.geojson>
   ```
   Replace `<input_file.json>` with the path to your Google Timeline JSON file and `<output_file.geojson>` with the desired output path for the GeoJSON file.

4. **Load the GeoJSON in QGIS**:
   - Open QGIS.
   - Go to "Layer" > "Add Layer" > "Add Vector Layer".
   - Select the generated GeoJSON file and load it into the map.


```bash
python location_history_json_converter.py LocationHistory.json LocationHistory.geojson 
```

This command processes the `LocationHistory.json` file, and generates a `LocationHistory.geojson` file.

## License

This script is released under the [MIT License](LICENSE).

## Credits

- **Peter Huiskens**: Concept, development. 
- **OpenAI (ChatGPT)**: Collaborative programming support.
- some credits need to go to Scarygami  ( https://github.com/Scarygami/location-history-json-converter ) 
This script started out with the script from Scarygami, but since a lot has changed in 3 years and the google takeout data is quite different to what is exported
from your phone, the script had to be changed. It has changed irrecogniable , yet some of the programming and programmingstyle might have survived the dozens of chatgpt itterations of the code 




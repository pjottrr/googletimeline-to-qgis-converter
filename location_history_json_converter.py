# MIT License
# 
# Copyright (c) 2025 Peter Huiskens, OpenAI (ChatGPT) 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import division
import sys
import json
from argparse import ArgumentParser
from datetime import datetime
import re
import os

def _get_year_from_timestamp(timestamp):
    """Extracts the year from a timestamp, defaults to 1970 if invalid or missing."""
    try:
        if timestamp:
            return datetime.fromtimestamp(int(timestamp) / 1000).year
    except ValueError:
        pass
    return 1970

def _parse_latlng(latlng):
    """Parses a latLng string like '53.2035733°, 5.7900171°' into latitude and longitude floats."""
    try:
        # Remove any invalid characters and ensure proper format
        latlng_cleaned = re.sub(r'[^\d.,\-]', '', latlng.replace('°', ''))
        parts = latlng_cleaned.split(',')
        if len(parts) != 2:
            raise ValueError(f"Unexpected format: {latlng_cleaned}")
        lat, lng = map(float, parts)
        return lat, lng
    except Exception as e:
        print(f"Error parsing latLng: {latlng} ({e})")
        return None, None

def _log_keys(data, level=0, debug=False):
    """Logs all keys in the JSON structure for debugging purposes."""
    if not debug:
        return
    if isinstance(data, dict):
        for key, value in data.items():
            print("  " * level + f"Key: {key}")
            _log_keys(value, level + 1, debug)
    elif isinstance(data, list):
        for item in data:
            _log_keys(item, level + 1, debug)

def _extract_locations(data):
    """Recursively extracts locations from various potential keys."""
    points = []
    lines = []

    def _traverse(obj):
        if isinstance(obj, dict):
            # Check for known location structures
            if "latitudeE7" in obj and "longitudeE7" in obj:
                points.append({
                    "type": "Point",
                    "coordinates": [obj["longitudeE7"] / 1e7, obj["latitudeE7"] / 1e7],
                    "timestamp": obj.get("timestampMs", "1970-01-01T00:00:00Z")
                })
            elif "placeLocation" in obj and "latLng" in obj["placeLocation"]:
                lat, lng = _parse_latlng(obj["placeLocation"]["latLng"])
                if lat is not None and lng is not None:
                    points.append({
                        "type": "Point",
                        "coordinates": [lng, lat],
                        "timestamp": obj.get("startTime", "1970-01-01T00:00:00Z")
                    })
            elif "timelinePath" in obj:
                line_points = []
                timestamps = {
                    "startTime": obj.get("startTime", "1970-01-01T00:00:00Z"),
                    "endTime": obj.get("endTime", "1970-01-01T00:00:00Z")
                }
                for path in obj["timelinePath"]:
                    if "point" in path:
                        lat, lng = _parse_latlng(path["point"])
                        if lat is not None and lng is not None:
                            line_points.append([lng, lat])
                    if "time" in path:
                        points.append({
                            "type": "Point",
                            "coordinates": [lng, lat],
                            "timestamp": path.get("time", "1970-01-01T00:00:00Z")
                        })
                if line_points:
                    lines.append({
                        "type": "LineString",
                        "coordinates": line_points,
                        "timestamps": timestamps
                    })

            # Traverse nested dictionaries
            for value in obj.values():
                _traverse(value)

        elif isinstance(obj, list):
            # Traverse lists
            for item in obj:
                _traverse(item)

    _traverse(data)
    return points, lines

def convert_to_geojson(points, lines, output):
    """Converts the provided locations and lines to a GeoJSON format."""
    features = []

    # Add points as GeoJSON features
    for point in points:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": point["type"],
                "coordinates": point["coordinates"]
            },
            "properties": {
                "timestamp": point.get("timestamp", "1970-01-01T00:00:00Z")
            }
        })

    # Add lines as GeoJSON features
    for line in lines:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": line["type"],
                "coordinates": line["coordinates"]
            },
            "properties": {
                "startTime": line["timestamps"]["startTime"],
                "endTime": line["timestamps"]["endTime"]
            }
        })

    # Write the GeoJSON output
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    json.dump(geojson, output, indent=2)

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("input", help="Input File (Location History.json)")
    arg_parser.add_argument("output", help="Output File (will be overwritten!)")
    arg_parser.add_argument("--debug", help="Enable debug logging", action="store_true")

    args = arg_parser.parse_args()

    if args.input == args.output:
        arg_parser.error("Input and output files must be different")
        return

    try:
        with open(args.input, "r") as f:
            json_data = f.read()
    except OSError as error:
        print(f"Error opening input file {args.input}: {error}")
        return

    try:
        data = json.loads(json_data)
    except ValueError as error:
        print(f"Error decoding JSON: {error}")
        return

    print("Logging JSON keys for debugging:")
    _log_keys(data, debug=args.debug)

    points, lines = _extract_locations(data)

    if not points and not lines:
        print("Error: No recognizable keys found in the JSON file.")
        return

    try:
        with open(args.output, "w") as f_out:
            convert_to_geojson(points, lines, f_out)
    except OSError as error:
        print(f"Error creating output file {args.output}: {error}")
        return

if __name__ == "__main__":
    sys.exit(main())

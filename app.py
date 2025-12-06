from flask import Flask, render_template, request, redirect
import csv
import os
import urllib
import json
import math

from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

app = Flask(__name__)

CSV_FILE = "trips.csv"


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["start_place", "end_place", "start_time", "end_time", "description"])


def read_trips():
    trips = []
    if not os.path.exists(CSV_FILE):
        return trips

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = dict(row)  # make sure it's mutable
            row["map_url"] = generate_mapbox_map(
                row.get("start_place", ""),
                row.get("end_place", "")
            )
            lat1, lon1 = geocode(row.get("start_place", ""))
            lat2, lon2 = geocode(row.get("end_place", ""))

            if None not in (lat1, lon1, lat2, lon2):
                row["distance_km"] = calculate_distance(lat1, lon1, lat2, lon2)
            else:
                row["distance_km"] = None

            trips.append(row)

    return trips


def add_trip(start_place, end_place, start_time, end_time, description):
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        
        # If writing for first time, write header
        if not file_exists:
            writer.writerow(["start_place", "end_place", "start_time", "end_time", "description"])
        
        writer.writerow([start_place, end_place, start_time, end_time, description])

def geocode(place):
    """
    Converts a place name string into (latitude, longitude) coordinates
    using the Mapbox Geocoding API.
    """
    if not MAPBOX_TOKEN:
        print("Error: MAPBOX_TOKEN not set.")
        return None, None

    # URL-encode the place name for the API query
    query = urllib.parse.quote(place)

    url = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{query}.json?access_token={MAPBOX_TOKEN}&limit=1"
    )

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            # Check if features were returned
            if data["features"]:
                # Mapbox returns coordinates as [longitude, latitude]
                lon, lat = data["features"][0]["center"]
                return lat, lon
            else:
                print(f"Warning: Could not geocode place: {place}")
                return None, None
    except Exception as e:
        print(f"Error during geocoding for {place}: {e}")
        return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lon points."""
    R = 6371  # Earth's radius in km

    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    lon1_r = math.radians(lon1)
    lon2_r = math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_km = R * c
    return round(distance_km, 2)


def generate_mapbox_map(start_place, end_place):
    """Build a Mapbox Static Maps URL with pins + line between start and end."""
    if not MAPBOX_TOKEN:
        return None

    start_lat, start_lon = geocode(start_place)
    end_lat, end_lon = geocode(end_place)

    if None in (start_lat, start_lon, end_lat, end_lon):
        return None

    overlays = (
        # f"path-4+ff0000({start_lon},{start_lat};{end_lon},{end_lat}),"
        f"pin-l-s+285A98({start_lon},{start_lat}),"
        f"pin-l-e+ff7f0e({end_lon},{end_lat})"
    )

    url = (
        "https://api.mapbox.com/styles/v1/mapbox/outdoors-v12/static/"
        f"{overlays}/auto/500x300"
        f"?access_token={MAPBOX_TOKEN}"
    )
    return url


@app.route("/")
def index():
    trips = read_trips()
    return render_template("index.html", trips=trips)


@app.route("/new", methods=["GET", "POST"])
def new_trip():
    if request.method == "POST":
        start_place = request.form.get("start_place")
        end_place = request.form.get("end_place")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        description = request.form.get("description")

        add_trip(start_place, end_place, start_time, end_time, description)
        return redirect("/")

    return render_template("new_trip.html")


if __name__ == "__main__":
    init_csv()
    app.run(debug=True)

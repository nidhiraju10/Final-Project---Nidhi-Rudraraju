from flask import Flask, render_template, request, redirect
import csv
import os
import urllib

from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

app = Flask(__name__)

CSV_FILE = "trips.csv"


def init_csv():
    # Create CSV file if missing
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

def geocode(place_name):
    """Use Mapbox to turn a place string into (lat, lon)."""
    if not MAPBOX_TOKEN or not place_name:
        return None, None

    encoded = urllib.parse.quote(place_name)
    url = (
        f"https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{encoded}.json?access_token={MAPBOX_TOKEN}"
    )

    try:
        resp = requests.get(url)
        data = resp.json()
    except Exception:
        return None, None

    features = data.get("features", [])
    if not features:
        return None, None

    lon, lat = features[0]["center"]
    return lat, lon


def generate_mapbox_map(start_place, end_place):
    """Build a Mapbox Static Maps URL with pins + line between start and end."""
    if not MAPBOX_TOKEN:
        return None

    start_lat, start_lon = geocode(start_place)
    end_lat, end_lon = geocode(end_place)

    # If we can't geocode either, skip the map
    if None in (start_lat, start_lon, end_lat, end_lon):
        return None

    # Path (red line) + blue 'S' pin at start, orange 'E' pin at end
    overlays = (
        f"path-4+ff0000({start_lon},{start_lat};{end_lon},{end_lat}),"
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

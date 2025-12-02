from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

CSV_FILE = "trips.csv"


def init_csv():
    # Create the CSV file with the correct header if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "date",
                "start_place",
                "end_place",
                "start_time",
                "end_time",
                "description",
            ])


def read_trips():
    trips = []
    if not os.path.exists(CSV_FILE):
        return trips

    with open(CSV_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trips.append(row)

    print("DEBUG trips from CSV:", trips)  # <- this will show in the terminal
    return trips


def add_trip(date, start_place, end_place, start_time, end_time, description):
    trips = read_trips()
    new_id = len(trips) + 1

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            new_id,
            date,
            start_place,
            end_place,
            start_time,
            end_time,
            description,
        ])


@app.route("/")
def index():
    trips = read_trips()
    return render_template("index.html", trips=trips)


@app.route("/new", methods=["GET", "POST"])
def new_trip():
    if request.method == "POST":
        date = request.form.get("date")
        start_place = request.form.get("start_place")
        end_place = request.form.get("end_place")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        description = request.form.get("description")

        add_trip(date, start_place, end_place, start_time, end_time, description)
        return redirect("/")

    return render_template("new_trip.html")


if __name__ == "__main__":
    init_csv()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
from helpers import get_db, init_db

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    print(">>> index() was called")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM trips ORDER BY id DESC")
    trips = cur.fetchall()
    conn.close()
    return render_template("index.html", trips=trips)

@app.route("/new", methods=["GET", "POST"])
def new_trip():
    if request.method == "POST":
        start_place = request.form.get("start_place")
        end_place = request.form.get("end_place")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        description = request.form.get("description")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO trips (start_place, end_place, start_time, end_time, description) VALUES (?, ?, ?, ?, ?)",
            (start_place, end_place, start_time, end_time, description)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("new_trip.html")

if __name__ == "__main__":
    app.run(debug=True)

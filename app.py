from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

TOTAL_SLOTS = 10


# ---------------- DATABASE ---------------- #

import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT UNIQUE,
        owner_name TEXT,
        slot_number TEXT,
        entry_time TEXT,
        exit_time TEXT,
        status TEXT,
        parking_fee REAL DEFAULT 0

    )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ---------------- #

@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE status='Parked'
        ORDER BY slot_number
    """)

    parked = cursor.fetchall()

    occupied_slots = []

    for vehicle in parked:
        occupied_slots.append(vehicle["slot_number"])

    slots = []

    for i in range(1, TOTAL_SLOTS + 1):

        slot_name = f"P{i}"

        if slot_name in occupied_slots:

            slots.append({
                "name": slot_name,
                "status": "Occupied"
            })

        else:

            slots.append({
                "name": slot_name,
                "status": "Free"
            })

    available = TOTAL_SLOTS - len(occupied_slots)
    occupied = len(occupied_slots)

    conn.close()

    return render_template(
        "index.html",
        slots=slots,
        total=TOTAL_SLOTS,
        available=available,
        occupied=occupied
    )


# ---------------- ADD VEHICLE ---------------- #

@app.route("/add_vehicle", methods=["POST"])
def add_vehicle():

    vehicle_number = request.form["vehicle_number"].upper().strip()
    owner_name = request.form["owner_name"].strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE vehicle_number=? AND status='Parked'
    """, (vehicle_number,))

    existing = cursor.fetchone()

    if existing:

        conn.close()
        return "Vehicle already parked."

    cursor.execute("""
        SELECT slot_number
        FROM vehicles
        WHERE status='Parked'
    """)

    occupied = []

    for row in cursor.fetchall():
        occupied.append(row["slot_number"])

    slot_number = None

    for i in range(1, TOTAL_SLOTS + 1):

        slot = f"P{i}"

        if slot not in occupied:
            slot_number = slot
            break

    if slot_number is None:

        conn.close()
        return "Parking Full!"

    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO vehicles
        (
            vehicle_number,
            owner_name,
            slot_number,
            entry_time,
            exit_time,
            status,
            parking_fee
        )
        VALUES(?,?,?,?,?,?,?)
    """,
    (
        vehicle_number,
        owner_name,
        slot_number,
        entry_time,
        "",
        "Parked",
        0
    ))

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- SEARCH VEHICLE ---------------- #

@app.route("/search", methods=["GET", "POST"])
def search():

    vehicle = None

    if request.method == "POST":

        number = request.form["vehicle_number"].upper().strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM vehicles
            WHERE vehicle_number=?
        """, (number,))

        vehicle = cursor.fetchone()

        conn.close()

    return render_template(
        "search.html",
        vehicle=vehicle
    )


# ---------------- VIEW VEHICLES ---------------- #

@app.route("/vehicles")
def vehicles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM vehicles
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "vehicles.html",
        vehicles=data
    )


# ---------------- EXIT VEHICLE ---------------- #

@app.route("/exit_vehicle/<int:id>")
def exit_vehicle(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM vehicles
        WHERE id=?
    """, (id,))

    vehicle = cursor.fetchone()

    if vehicle is None:

        conn.close()
        return redirect("/vehicles")

    exit_time = datetime.now()

    entry_time = datetime.strptime(
        vehicle["entry_time"],
        "%Y-%m-%d %H:%M:%S"
    )

    total_hours = (exit_time - entry_time).total_seconds() / 3600

    if total_hours < 1:
        total_hours = 1

    parking_fee = round(total_hours * 50, 2)

    cursor.execute("""
        UPDATE vehicles
        SET
            exit_time=?,
            status=?,
            parking_fee=?
        WHERE id=?
    """,
    (
        exit_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Exited",
        parking_fee,
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/vehicles")
# ---------------- DELETE VEHICLE ---------------- #

@app.route("/delete/<int:id>")
def delete_vehicle(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM vehicles WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/vehicles")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM vehicles"
    )
    total_vehicles = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM vehicles WHERE status='Parked'"
    )
    parked = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM vehicles WHERE status='Exited'"
    )
    exited = cursor.fetchone()[0]

    cursor.execute(
        "SELECT SUM(parking_fee) FROM vehicles"
    )

    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    conn.close()

    return render_template(
        "dashboard.html",
        total=total_vehicles,
        parked=parked,
        exited=exited,
        revenue=revenue
    )


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    create_table()

    app.run(
        debug=True
    )
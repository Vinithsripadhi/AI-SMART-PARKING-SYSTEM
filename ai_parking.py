import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")

TOTAL_SLOTS = 10


def park_vehicle(vehicle_number):

    vehicle_number = vehicle_number.upper().strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if vehicle already exists
    cursor.execute("""
        SELECT id, status
        FROM vehicles
        WHERE vehicle_number=?
    """, (vehicle_number,))

    existing = cursor.fetchone()

    # If already parked, don't insert again
    if existing and existing[1] == "Parked":
        print("Vehicle already parked.")
        conn.close()
        return

    # Find occupied slots
    cursor.execute("""
        SELECT slot_number
        FROM vehicles
        WHERE status='Parked'
    """)

    occupied = [row[0] for row in cursor.fetchall()]

    slot = None

    for i in range(1, TOTAL_SLOTS + 1):
        s = f"P{i}"
        if s not in occupied:
            slot = s
            break

    if slot is None:
        print("Parking Full")
        conn.close()
        return

    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if existing:

        # Vehicle existed before and had exited
        cursor.execute("""
            UPDATE vehicles
            SET
                owner_name=?,
                slot_number=?,
                entry_time=?,
                exit_time='',
                status='Parked',
                parking_fee=0
            WHERE vehicle_number=?
        """,
        (
            "AI Camera",
            slot,
            entry_time,
            vehicle_number
        ))

    else:

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
            "AI Camera",
            slot,
            entry_time,
            "",
            "Parked",
            0
        ))

    conn.commit()

    print("===================================")
    print("Vehicle :", vehicle_number)
    print("Slot    :", slot)
    print("Status  : Parked Successfully")
    print("===================================")

    conn.close()
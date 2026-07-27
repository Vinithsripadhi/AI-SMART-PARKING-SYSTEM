import sqlite3

conn = sqlite3.connect("parking.db")
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

print("Database Ready!")
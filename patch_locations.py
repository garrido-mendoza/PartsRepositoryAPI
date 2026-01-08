import sqlite3

conn = sqlite3.connect("parts_inventory.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE locations ADD COLUMN description TEXT")
    print("Column 'description' added successfully.")
except sqlite3.OperationalError as e:
    print("Error:", e)

conn.commit()
conn.close()


# To run this script, execute: python patch_locations.py

# SQLlite commands: 
# .help to get help
# .tables to see tables
# PRAGMA table_info(locations); to see columns in locations table   
# ALTER TABLE locations ADD COLUMN description TEXT; to add the column
# .quit to exit

# Note: This script assumes the database file is named 'parts_inventory.db' and is located in the same directory as the script.
# Make sure to back up your database before running schema-altering scripts.
# This script adds a 'description' column to the 'locations' table in the SQLite database.
# If the column already exists, an error message will be printed.
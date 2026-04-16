import sqlite3
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import database as db


def reset_database():
    print("Resetting database...")

    conn = sqlite3.connect('store.db')
    cur = conn.cursor()

    # Disable foreign keys temporarily
    cur.execute("PRAGMA foreign_keys = OFF;")

    # Get all tables
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)

    tables = cur.fetchall()

    # Drop all tables
    for table in tables:
        print(f"Dropping table: {table[0]}")
        cur.execute(f"DROP TABLE IF EXISTS {table[0]}")

    conn.commit()
    conn.close()

    print("All tables dropped")

    # Reinitialize database
    db.init_db()

    print("Database reset complete")


if __name__ == "__main__":
    reset_database()
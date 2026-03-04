import sqlite3

conn = sqlite3.connect('store.db')
cur = conn.cursor()

# Delete all users/customers
cur.execute("DELETE FROM customers")

# Reset auto-increment counter
cur.execute("DELETE FROM sqlite_sequence WHERE name='customers'")

conn.commit()
conn.close()

print("All users removed, auto-increment reset")
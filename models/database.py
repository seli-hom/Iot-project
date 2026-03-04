import sqlite3

def getDB():
    # allow SQLite to be used safely in Flask dev mode threads
    conn = sqlite3.connect('store.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    storeDb = getDB()
    
    # Create the customers table if it doesn't exist
    storeDb.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        address TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    # For when we need to add more tables we would put the here with the databse. execute sameway as the customers table :)) BEFORE THE COMMIT!!
      
    # Adding 'verified' column if missing (catch error if it already exists)
    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN verified INTEGER DEFAULT 0")
        print("Added 'verified' column to customers table")
    except sqlite3.OperationalError:
        pass

    # Adding 'password' column if missing (can be NULL)
    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN password TEXT")
        print("Added 'password' column to customers table (NULL allowed)")
    except sqlite3.OperationalError:
        pass

    # Adding 'role' column if missing, default = 'customer'
    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN role TEXT DEFAULT 'customer'")
        print("Added 'role' column to customers table (default='customer')")
    except sqlite3.OperationalError:
        pass

    storeDb.commit()
    storeDb.close()
    print("Database has started and tables have been made / updated")
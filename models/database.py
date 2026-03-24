import sqlite3

def getDB():
    conn = sqlite3.connect('store.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    storeDb = getDB()

    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT CHECK(type IN ('email','system','alert')) NOT NULL,
            title TEXT NOT NULL,
            msg_summary TEXT NOT NULL,
            msg_extended TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN verified INTEGER DEFAULT 0")
        print("Added 'verified'")
    except sqlite3.OperationalError:
        pass

    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN password TEXT")
        print("Added 'password'")
    except sqlite3.OperationalError:
        pass

    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN role TEXT DEFAULT 'customer'")
        print("Added 'role'")
    except sqlite3.OperationalError:
        pass

    try:
        storeDb.execute("ALTER TABLE customers ADD COLUMN user_id INTEGER")
        print("Added 'user_id'")
    except sqlite3.OperationalError:
        pass

    storeDb.commit()
    storeDb.close()

    print("Database has started and tables have been made / updated")
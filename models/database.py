import sqlite3

def getDB():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn

def start_database():
    storeDb = getDB()
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
      
    storeDb.commit()
    storeDb.close()
    print ("Database has started and tables have n=been made")
    return 
      
      
#hellloooooo why is is not transferring?

    

import sqlite3
import gpio_blue_red as gpr


def create_customer_table():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE NOT NULL,
                        address TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()
    print("Customer table has been created successfully.")

def add_customer(first_name, last_name, email, phone, address):
    try:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO customers (first_name, last_name, email, phone, address) 
                          VALUES (?, ?, ?, ?, ?)''', 
                          (first_name, last_name, email, phone, address))
        conn.commit()
        conn.close()
        print("Customer added to database successfully.")
        gpr.new_customer_success()
        return True
    except sqlite3.IntegrityError as e:
        gpr.new_customer_fail()
        print(f"Database error: {e}")
        return False
    
def select_customers():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    conn.close()
    return customers
import sqlite3
import gpio_blue_red as gpr
import database as db

def add_new_customer(first_name, last_name, email, phone, address):
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
    storeDb = db.getDB()
    customers = storeDb.execute('SELECT * FROM customers').fetchall()
    storeDb.close()
    return customers

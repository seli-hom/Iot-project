import sqlite3
try:
    from scripts import gpio_blue_red as gpr
except ModuleNotFoundError:
    gpr = None #for development purposes only
    print("[ERROR] DPIO module not found")

from models import database as db

def add_new_customer(first_name, last_name, email, phone, address):
    try:
        store = db.getDB()
        store.execute('''INSERT INTO customers (first_name, last_name, email, phone, address) 
                          VALUES (?, ?, ?, ?, ?)''', 
                          (first_name, last_name, email, phone, address))
        store.commit()
        store.close()
        print("Customer added to database successfully.")
        if gpr:
            gpr.new_customer_success()
        return True
    except sqlite3.IntegrityError as e:
        if gpr:
            gpr.new_customer_fail()
        print(f"Database error: {e}")
        return False
    
def select_customers():
    storeDb = db.getDB()
    customers = storeDb.execute('SELECT * FROM customers').fetchall()
    storeDb.close()
    return customers

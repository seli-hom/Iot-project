import sqlite3
import bcrypt
try:
    from scripts import gpio_blue_red as gpr
except ModuleNotFoundError:
    gpr = None  # for development purposes only
    print("[ERROR] DPIO module not found")

from models import database as db

def add_new_customer(first_name, last_name, email, phone, address, password=None, role='customer'):
    """
    Adds a new customer to the database
    Returns the new customer's ID if successful, False otherwise
    """
    store = db.getDB()
    try:
        # hashing the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        # insert into users table
        cur = store.execute('''
            INSERT INTO customers 
            (first_name, last_name, email, phone, address, password, role, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', 
        (first_name, last_name, email, phone, address, hashed_pw, role, 0 if password is None else 1))

        user_id = cur.lastrowid  

        store.commit()

        print("Customer added to database successfully.")
        if gpr:
            gpr.new_customer_success()

        return user_id

    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")
        if gpr:
            gpr.new_customer_fail()
        return False
    finally:
        store.close() 


def select_customers():
    storeDb = db.getDB()
    try:
        customers = storeDb.execute('''
            SELECT * FROM customers
        ''').fetchall()
        return customers
    finally:
        storeDb.close()
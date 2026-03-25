import sqlite3
from models import database as db
try:
    from scripts import gpio_blue_red as gpr
except ModuleNotFoundError:
    gpr = None  # for development purposes only
    print("[ERROR] DPIO module not found")

def add_new_customer(user_id, phone, address):
    """
    Adds a new customer profile linked to a user
    Returns the new customer ID if successful, False otherwise
    """
    store = db.getDB()
    try:
        cur = store.execute('''
            INSERT INTO customers (user_id, phone, address)
            VALUES (?, ?, ?)
        ''', (user_id, phone, address))

        store.commit()
        customer_id = cur.lastrowid

        print(f"Customer profile added successfully: user_id={user_id}, customer_id={customer_id}")
        if gpr:
            gpr.new_customer_success()

        return customer_id

    except sqlite3.IntegrityError as e:
        print(f"[ERROR] Database integrity error: {e}")
        if gpr:
            gpr.new_customer_fail()
        return False
    finally:
        store.close()


def select_customers():
    """
    Returns a list of all customers, joined with their user info
    """
    storeDb = db.getDB()
    try:
        customers = storeDb.execute('''
            SELECT customers.*, users.first_name, users.last_name, users.email, users.role, users.verified
            FROM customers
            JOIN users ON customers.user_id = users.id
        ''').fetchall()
        return customers
    finally:
        storeDb.close()


def update_customer_role(user_id, new_role):
    """
    Update a user's role (customer, employee, admin)
    """
    storeDb = db.getDB()
    try:
        storeDb.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
        storeDb.commit()
        print(f"Updated role for user_id={user_id} to '{new_role}'")
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to update role: {e}")
        return False
    finally:
        storeDb.close()


def delete_customer(user_id):
    """
    Deletes a user and associated customer profile
    """
    storeDb = db.getDB()
    try:
        storeDb.execute('DELETE FROM users WHERE id = ?', (user_id,))
        storeDb.commit()
        print(f"Deleted user and associated customer profile: user_id={user_id}")
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to delete customer: {e}")
        return False
    finally:
        storeDb.close()
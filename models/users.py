import sqlite3
import bcrypt
try:
    from scripts import gpio_blue_red as gpr
except ModuleNotFoundError:
    gpr = None  # for development purposes only
    print("[ERROR] DPIO module not found")

from models import database as db

def add_new_user(first_name, last_name, email, phone, address, password=None, role='customer'):
    """
    Adds a new user to the database.
    Returns the new user's ID if successful, False otherwise.
    """
    store = db.getDB()
    try:
        # hashing the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) if password else None

        # insert into users table
        cur = store.execute('''
            INSERT INTO users
            (first_name, last_name, email, phone, address, password, role, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', 
        (first_name, last_name, email, phone, address, hashed_pw, role, 0 if password is None else 1))

        user_id = cur.lastrowid  
        store.commit()

        print("User added to database successfully.")
        if gpr:
            gpr.new_customer_success()  # you can rename this to new_user_success if desired

        return user_id

    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")
        if gpr:
            gpr.new_customer_fail()
        return False
    finally:
        store.close()


def select_users():
    """
    Returns all users from the database.
    """
    storeDb = db.getDB()
    try:
        users = storeDb.execute('''
            SELECT * FROM users
        ''').fetchall()
        return users
    finally:
        storeDb.close()


def update_user_role(user_id, role):
    """
    Updates the role of a user (customer, employee, admin)
    """
    storeDb = db.getDB()
    try:
        storeDb.execute('UPDATE users SET role = ? WHERE id = ?', (role, user_id))
        storeDb.commit()
        return True
    except Exception as e:
        print("Failed to update user role:", e)
        return False
    finally:
        storeDb.close()
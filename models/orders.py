import sqlite3
from models import database as db

def select_orders():
    """
    Returns all orders from the database.
    """
    storeDb = db.getDB()
    try:
        users = storeDb.execute('''
            SELECT * FROM orders
        ''').fetchall()
        return users
    finally:
        storeDb.close()



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
        
        
def view_specific_order_details(order_id):
    """
    Returns details for a specific order.
    """
    storeDb = db.getDB()
    try:
        orders = storeDb.execute('''
            SELECT * FROM orders_products WHERE order_id = ?
        ''', (order_id,)).fetchall()
        return orders
    finally:
        storeDb.close()
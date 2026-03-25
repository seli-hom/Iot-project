from models import database as db

def add_notification(type_, title, summary, extended, user_id=None):
    storeDb = db.getDB()
    storeDb.execute('''
        INSERT INTO notifications (type, title, msg_summary, msg_extended, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (type_, title, summary, extended, user_id))
    storeDb.commit()
    storeDb.close()

def get_store_notifications(limit=5):
    storeDb = db.getDB()
    rows = storeDb.execute('''
        SELECT * FROM notifications
        WHERE type IN ('system', 'email')
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    storeDb.close()
    return rows

def get_admin_notifications(limit=5):
    storeDb = db.getDB()
    rows = storeDb.execute('''
        SELECT * FROM notifications
        WHERE type = 'user'
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    storeDb.close()
    return rows
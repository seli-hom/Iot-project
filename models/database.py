import sqlite3

def getDB():
    """
    Returns a database connection object
    SQLite connections are allowed in multiple threads safely
    """
    conn = sqlite3.connect('store.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database:
    - Creates tables if they don't exist
    - Adds missing columns
    """
    storeDb = getDB()

    # Initializing users table
    # ? should we update the user_verified to make use of a bool, or stick with the bits?
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_fname TEXT NOT NULL,
            user_lname TEXT NOT NULL,
            user_email TEXT UNIQUE NOT NULL,
            user_password TEXT,
            user_role TEXT DEFAULT 'customer',
            user_verified INTEGER DEFAULT 0,
            user_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Customers table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            membership_number TEXT UNIQUE,
            customer_phone TEXT,
            customer_address TEXT,
            customer_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    # Initializing customer loyalty table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS customer_loyalty (
            loyalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER UNIQUE NOT NULL,
            loyalty_points INTEGER DEFAULT 0,
            loyalty_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            loyalty_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )
    ''')

    # Initializing loyalty transactions table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS loyalty_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('EARN','SPEND','ADJUST')) NOT NULL,
            transaction_points INTEGER NOT NULL,
            transaction_description TEXT,
            transaction_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )
    ''')

    # Initializing notifications table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
            notif_type TEXT CHECK(notif_type IN ('email','system','alert')) NOT NULL,
            notif_title TEXT NOT NULL,
            notif_msg_summary TEXT NOT NULL,
            notif_msg_extended TEXT NOT NULL,
            notif_user_id INTEGER,
            notif_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(notif_user_id) REFERENCES users(user_id)
        )
    ''')

    # Initializing categories table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_type TEXT NOT NULL,
            category_desc_summary TEXT NOT NULL,
            category_desc_extended TEXT NOT NULL,
            category_created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Initializing products table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER DEFAULT NULL,
            product_name TEXT NOT NULL,
            product_description TEXT DEFAULT NULL,
            product_price REAL NOT NULL,
            producer_company TEXT,
            product_stock_quantity INTEGER DEFAULT 0,
            product_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            product_updated_at DATETIME,
            FOREIGN KEY(category_id) REFERENCES categories(category_id)
        )
    ''')

    # Initializing product barcode table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS product_barcode (
            barcode_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            barcode_num TEXT UNIQUE NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')

    # Initializing product RFID table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS product_rfid (
            rfid_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            rfid_tag TEXT UNIQUE NOT NULL,
            rfid_status TEXT DEFAULT 'ACTIVE',
            rfid_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')

    # Initializing self checkout sessions table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS self_checkout_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_status TEXT DEFAULT 'ACTIVE',
            session_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # Initializing orders table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_total REAL NOT NULL,
            payment_method TEXT,
            order_status TEXT DEFAULT 'PENDING',
            order_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # Initializing order products table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS order_products (
            order_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            order_product_quantity INTEGER NOT NULL,
            order_product_unit_price REAL DEFAULT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')

    # Initializing cart table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cart_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # Initializing cart products table
    storeDb.execute('''
        CREATE TABLE IF NOT EXISTS cart_products (
            cart_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            cart_product_quantity INTEGER NOT NULL,
            cart_product_price REAL,
            FOREIGN KEY(cart_id) REFERENCES cart(cart_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
    ''')

    # Populating the database


    storeDb.commit()
    storeDb.close()

    print("Database initialized: tables created / updated")
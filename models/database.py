import sqlite3
import bcrypt

def getDB():
    """
    Returns a database connection object
    SQLite connections are allowed in multiple threads safely
    """
    conn = sqlite3.connect('store.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
def add_column_safe(table_name, column_name, column_type, default_value=None):
    # Checks if column exists before adding it to the table
    storeDb = getDB()
    cursor = storeDb.execute(f"PRAGMA table_info({table_name})")
    columns = [col['name'] for col in cursor.fetchall()]
    if column_name not in columns:
        if default_value is not None:
            storeDb.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
        else:
            storeDb.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    storeDb.commit()
    # storeDb.close() 
    # !! closed the db before



def add_column_if_not_exists(table_name, column_name, column_type, default_value=None):
    """
    Adds a column to a table if it doesn't already exist
    """
    storeDb = getDB()
    # Check if the column already exists
    existing_columns = storeDb.execute(f"PRAGMA table_info({table_name})").fetchall()
    column_names = [col['name'] for col in existing_columns]

    if column_name not in column_names:
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            alter_query += f" DEFAULT {default_value}"
        storeDb.execute(alter_query)
        storeDb.commit()
        print(f"Column '{column_name}' added to '{table_name}'")
    else:
        print(f"Column '{column_name}' already exists in '{table_name}'")

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

    add_column_if_not_exists('users', 'user_loyalty_points', 'INTEGER', default_value=0)


    # storeDb.execute('''
    #     ALTER TABLE users ADD COLUMN user_loyalty_points INTEGER DEFAULT 0
    # ''')
    add_column_safe('users', 'user_loyalty_points', 'INTEGER', default_value=0)
    
# !I think we will need to scratch this after since we are using the users table for registration and such
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
    
    # !Not needed as loyalty points can be added to users table as a column
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
            category_type TEXT UNIQUE NOT NULL,
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
            product_company TEXT,
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
            user_id INTEGER,
            order_total REAL NOT NULL,
            payment_method TEXT,
            order_status TEXT DEFAULT 'PENDING',
            order_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    add_column_if_not_exists('orders', 'customer_email', 'TEXT')

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

    # INSERT OR IGNORE for categories if they already exist
    # To be safest, we check if they exist first
    categories = ['Makeup', 'Fragrance', 'Lip Sets']
    for cat in categories:
        storeDb.execute("INSERT OR IGNORE INTO categories (category_type) VALUES (?)", (cat,))
    
    # Refresh the map dynamically so IDs are always correct
    cat_rows = storeDb.execute("SELECT category_id, category_type FROM categories").fetchall()
    cat_map = {row['category_type']: row['category_id'] for row in cat_rows}

    products_to_add = [
        ("Solo Shadow Cream Eyeshadow", "Makeup", 35.00, "Merit Beauty", "6989880828680", "A00000000000000000004954"),
        ("Apple Love Eau de Parfum", "Fragrance", 161.00, "Ellis Brooklyn", "3063474108488", "A00000000000000000004955"),
        ("Dew Blush Liquid Blush", "Makeup", 35.00, "Saie", "4565162111323", "A00000000000000000004953"),
        ("The Sweet Pink Duo", "Lip Sets", 52.00, "Summer Fridays", "3898267675041", "A00000000000000000004959")
    ]

    for name, cat_name, price, company, barcode, rfid in products_to_add:
        category_id = cat_map.get(cat_name)

        # Look for the specific product/company combo
        existing = storeDb.execute(
            "SELECT product_id FROM products WHERE product_name = ? AND product_company = ?", 
            (name, company)
        ).fetchone()

        if not existing:
            # Only insert if it's actually missing
            cursor = storeDb.execute('''
                INSERT INTO products (product_name, product_price, product_company, category_id, product_stock_quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, price, company, category_id, 1))
            new_id = cursor.lastrowid
            
            # Since the product is new, add the identifiers
            storeDb.execute('INSERT OR IGNORE INTO product_barcode (product_id, barcode_num) VALUES (?, ?)', (new_id, barcode))
            storeDb.execute('INSERT OR IGNORE INTO product_rfid (product_id, rfid_tag) VALUES (?, ?)', (new_id, rfid))
        else:
            pass

    # Hash the password
    password = "123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    storeDb.execute('''
        INSERT OR IGNORE INTO users (user_fname, user_lname, user_email, user_password, user_role)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Admin", "User", "admin@gmail.com", hashed, "admin"))

    # print("Database checked: New items added or existing items skipped.")

    # storeDb.execute('''
    #     INSERT INTO products (product_name, product_price, product_company, product_stock_quantity)
    #     VALUES 
    #         ("Solo Shadow Cream Eyeshadow", "Makeup", 35.00, "Merit Beauty", "6989880828680", "A00000000000000000004954"),
    #         ("Apple Love Eau de Parfum", "Fragrance", 161.00, "Ellis Brooklyn", "3063474108488", "A00000000000000000004955"),
    #         ("Dew Blush Liquid Blush", "Makeup", 35.00, "Saie", "4565162111323", "A00000000000000000004953"),
    #         ("The Sweet Pink Duo", "Lip Sets", 52.00, "Summer Fridays", "3898267675041", "A00000000000000000004959")
    # ''')

    storeDb.commit()
    storeDb.close()

    print("Database initialized: tables created / updated")
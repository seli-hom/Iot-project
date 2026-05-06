from flask import render_template, request, Blueprint, session, redirect, url_for, flash, jsonify
import bcrypt

import json
import datetime
# Models & Database
from models import database as db
from models import customers, users

# Hardware & Scripts
# from scripts import gpio_blue_red as gpr

# Services
from services import email_service
from services.rfid_service import RFIDService
from services.receipt_service import EmailAlertSystem
from services.hardware import hardware_status, motor_control

# Blueprint Setup
app = Blueprint('store', __name__)

# -----------------------------
# STORE HOME / DASHBOARD
# -----------------------------
@app.route('/')
def storeIndex():
    return render_template('index.html')



@app.route('/store-dashboard')
def storeDashboard():
    storeDb = db.getDB()
    # notifications = storeDb.execute('''
    #     SELECT * FROM notifications
    #     ORDER BY notif_created_at DESC
    #     LIMIT 5
    # ''').fetchall()
    # notifications = storeDb.execute('''
    #     SELECT * FROM notifications
    #     ORDER BY notif_created_at DESC
    #     LIMIT 5
    # ''').fetchall()
    storeDb.close()
    return render_template(
        'storeDashboard.html',
        # notifications=notifications,
        # notifications=notifications,
        temp=4,
        hm=65,
        type="Notice",
        kitchen_temp=kitchen_temp,
        kitchen_hum=kitchen_hum,
        room_temp=room_temp,
        room_hum=room_hum,
    )


# -----------------------------
# NOTIFICATIONS API
# -----------------------------
@app.route('/api/notifications')
def get_notifications():
    storeDb = db.getDB()
    try:
        notifications = storeDb.execute('''
            SELECT notif_id, notif_type, notif_title, notif_msg_summary, notif_msg_extended, notif_created_at
            FROM notifications
            ORDER BY notif_created_at DESC
            LIMIT 10
        ''').fetchall()

        notif_list = [
            {

                "id": n["notif_id"],
                "type": n["notif_type"],
                "title": n["notif_title"],
                "summary": n["notif_msg_summary"],
                "extended": n["notif_msg_extended"],
                "created_at": n["notif_created_at"]
            } for n in notifications
        ]
        return jsonify(notif_list)
    except Exception as e:
        print("Error fetching notifications:", e)
        return jsonify([]), 500
    finally:
        storeDb.close()

# -----------------------------
# CUSTOMER ROUTES
# -----------------------------
@app.route('/customers')
def customersList():
    all_customers = customers.select_customers()
    print(all_customers)
    return render_template('customersList.html', customers=all_customers)

@app.route('/productList')
def productList():
    storeDb = db.getDB()
    # You need a JOIN or a subquery to count how many RFID tags exist for each product
    query = """
        SELECT p.*, COUNT(r.rfid_tag) as stock_quantity
        FROM products p
        LEFT JOIN product_barcode r ON p.product_id = r.product_id
        GROUP BY p.product_id
    """
    products = storeDb.execute(query).fetchall()
    return render_template('productsList.html', products=products)

@app.route('/admin-dashboard/products/<int:product_id>/Tags')
def TagsList(product_id):
    storeDb = db.getDB()
    tags = storeDb.execute(
        '''SELECT * from product_rfid where product_id = ?;
'''
    ,(product_id,)).fetchall()
    return render_template('TagsList.html', tags=tags,product_id=product_id)

@app.route('/admin-dashboard/products/<int:product_id>/update',methods = ['GET','POST'])
def productUpdate(product_id):
    if request.method == 'POST':
        storeDb = db.getDB()
        storeDb.execute('''
                    UPDATE products SET product_name = ? , category_id = ?, product_price = ?, product_company = ?, product_description = ?, product_stock_quantity = ?
                                WHERE product_id = ?
                ''', (request.form['product_name'],request.form['product_category'], request.form['product_price'], request.form['product_company'], request.form['product_description'],request.form['product_stock'],product_id))        
        storeDb.execute('''
                    UPDATE product_barcode SET  barcode_num = ?
                        WHERE product_id = ?
                ''', ( request.form['product_barcode'],product_id))
        stock =  storeDb.execute('''
                    SELECT product_stock_quantity FROM products
                        WHERE product_id = ?
                ''', (product_id,)).fetchone()
        
        if stock['product_stock_quantity'] != request.form['product_stock']:
            storeDb.execute('''
                        UPDATE products 
                        SET product_updated_at = CURRENT_TIMESTAMP 
                        WHERE product_id = ?;
                    ''', (product_id,))
        
        storeDb.commit()
        return redirect(url_for('store.productsList'))
    storeDb = db.getDB()
    product = storeDb.execute(
        '''SELECT p.*,pb.*,STRING_AGG(pr.rfid_tag,' / ') as rfid_tag FROM products p  
            LEFT JOIN product_rfid pr on pr.product_id = p.product_id
            LEFT JOIN product_barcode pb on   pb.product_id= p.product_id
            WHERE p.product_id = ? GROUP BY p.product_id''',
    (product_id,)).fetchone()
    return render_template('productUpdate.html', product=product)



@app.route('/admin-dashboard/products/create')
def productCreate():
    return render_template('productCreation.html')

@app.route('/admin-dashboard/products/<int:product_id>/Tags/create')
def tagCreate(product_id):
    return render_template('tagCreation.html',product_id=product_id)


@app.route('/admin-dashboard/products/<int:product_id>/addRFID',  methods=['POST'])
def addRFID(product_id):
    storeDb = db.getDB()
    storeDb.execute('''
                INSERT INTO product_rfid (product_id, rfid_tag, rfid_status)
                VALUES (?, ?, ?)
            ''', (product_id, request.form['product_rfid'],'ACTIVE'))
    storeDb.commit()
    return redirect(url_for('store.TagsList',product_id=product_id))

@app.route('/admin-dashboard/products/<int:rfid_id>/removeRFID',  methods=['GET'])
def removeRFID(rfid_id):
    storeDb = db.getDB()
    data = storeDb.execute('''
            DELETE FROM product_rfid where rfid_id = ?
             ''', (rfid_id,))
    storeDb.commit()
    return redirect(url_for('store.productsList'))

@app.route('/admin-dashboard/products/add', methods=['POST'])
def productAdd():

    storeDb = db.getDB()
    product = storeDb.execute('''
                INSERT INTO products (product_name, category_id, product_price, product_company, product_description,product_stock_quantity)
                VALUES (?, ?, ?, ?, ?,?)
            ''', (request.form['product_name'],request.form['product_category'], request.form['product_price'], request.form['product_company'], request.form['product_description'],request.form['stock']))
    
    storeDb.execute('''
                INSERT INTO product_barcode (product_id, barcode_num)
                VALUES (?, ?)
            ''', (product.lastrowid, request.form['product_barcode']))

    storeDb.commit()
    return redirect(url_for('store.productsList'))

@app.route('/admin-dashboard/products/<int:product_id>/delete', methods=['POST', 'GET'])
def productDelete(product_id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    storeDb.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
    storeDb.execute('DELETE FROM product_barcode WHERE product_id = ?', (product_id,))
    storeDb.execute('DELETE FROM product_rfid WHERE product_id = ?', (product_id,))
    storeDb.commit()
    storeDb.close()

    flash("User deleted successfully.", "success")
    return redirect(url_for('store.productsList'))


@app.route('/customers/registration', methods=['GET', 'POST'])
def customersRegistration():
    message = None
    success = None
    if request.method == 'POST':
        storeDb = db.getDB()
        # print(...) removed for brevity
        try:
            cur = storeDb.execute('''
            INSERT INTO users (user_fname, user_lname, user_email, user_password, user_role, user_verified)
            VALUES (?, ?, ?, ?, 'customer', 0)
            ''', (request.form['fname'], request.form['lname'], request.form['email'], bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())))
            storeDb.commit()
            
            new_user_id = cur.lastrowid
            int_id = (int)(new_user_id)
            storeDb.execute('''UPDATE users SET user_loyalty_points = 5 WHERE user_id = ?''', (int_id,))
            storeDb.commit()
            
            print(f"DEBUG: User {new_user_id} saved to DB. Triggering Blue LED...")
            
            # --- TRIGGER BLUE LED HERE ---
            from scripts import gpio_blue_red as gpr
            gpr.blink_blue() 

            # Send verification email logic...
            try:
                # from services.email_service import send_registration_email
                # send_registration_email(request.form['fname'], request.form['lname'], request.form['email'], new_user_id)
                message = "Customer account created successfully."
                success = True
            except Exception as e:
                print("Email sending failed:", e)
                message = "User created, but email failed."
                success = True # Set to True because the DB part succeeded

        except Exception as e:
            print("Error creating user:", e)
            message = "Error creating user"
            success = False
            
            # --- TRIGGER RED LED HERE ---
            from scripts import gpio_blue_red as gpr
            gpr.blink_red()

        finally:
            storeDb.close()

    return render_template('customersRegistration.html', message=message, success=success)




@app.route('/verify/<int:user_id>', methods=['GET', 'POST'])
def customerVerification(user_id):
    storeDb = db.getDB()
    user = storeDb.execute(
        'SELECT * FROM users WHERE user_id = ?',
        (user_id,)
    ).fetchone()

    user = storeDb.execute(
        'SELECT * FROM users WHERE user_id = ?',
        (user_id,)
    ).fetchone()

    message = None
    success = None

    if not user:
        message = "Invalid verification link."
        success = False
        storeDb.close()
        return render_template(
            'customersVerification.html',
            message=message,
            success=success
        )

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            message = "Please fill in both password fields."
            success = False
        elif password != confirm_password:
            message = "Passwords do not match."
            message = "Passwords do not match."
            success = False
        else:
            try:
                hashed_pw = bcrypt.hashpw(
                    password.encode('utf-8'),
                    bcrypt.gensalt()
                )

                storeDb.execute('''
                    UPDATE users 
                    SET user_password = ?, user_verified = 1 
                    WHERE user_id = ?
                ''', (hashed_pw, user_id))

                customers.add_new_customer(user_id, None, None)
                storeDb.commit()

                message = "Your account has been verified!"
                success = True

                try:
                    from services.email_service import send_new_customer_notification
                    send_new_customer_notification(
                        user['user_fname'],
                        user['user_lname'],
                        user['user_email']
                    )
                except Exception as e:
                    print("Admin notification email failed:", e)

                try:
                    from services.email_service import send_new_customer_notification
                    send_new_customer_notification(
                        user['user_fname'],
                        user['user_lname'],
                        user['user_email']
                    )
                except Exception as e:
                    print("Admin notification email failed:", e)

            except Exception as e:
                print("Verification error:", e)
                message = "Error verifying account."
                success = False
                print("Verification error:", e)
                message = "Error verifying account."
                success = False

    storeDb.close()
    return render_template(
        'customersVerification.html',
        message=message,
        success=success
    )
    return render_template(
        'customersVerification.html',
        message=message,
        success=success
    )


# -----------------------------
# LOGIN / LOGOUT
# -----------------------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('user_email')
    password = request.form.get('user_password')

    storeDb = db.getDB()
    user = storeDb.execute('''
        SELECT users.*
        FROM users
        WHERE user_email = ?
    ''', (email,)).fetchone()
    storeDb.close()


    if not user:
        flash("Invalid credentials.", "danger")
        return redirect(url_for('store.customersList'))

    if bcrypt.checkpw(password.encode('utf-8'), user['user_password']):
        session['user_email'] = user['user_email']
        session['user_first_name'] = user['user_fname']
        session['user_role'] = user['user_role']
        return redirect(url_for('store.storeIndex'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('store.storeIndex'))

@app.route('/admin-dashboard/orders')
def customerOrders():   
    storeDb = db.getDB() 
    orders = storeDb.execute('SELECT * FROM orders ORDER BY order_created_at DESC').fetchall()
    return render_template("CustomerOrders.html", orders=orders) 


@app.route('/admin-dashboard/orders/<int:order_id>')
def orderDetails(order_id):   
    storeDb = db.getDB() 
    order = storeDb.execute('''SELECT * FROM orders where order_id = ?''', (order_id,)).fetchone()
    return render_template("OrderDetails.html",  order=order) 
# -----------------------------
# FAN / THRESHOLD ROUTES
# -----------------------------
@app.route('/fan', methods=['POST'])
def toggle_fan():
    data = request.get_json()
    if not data or "state" not in data:
        return jsonify({"status": "error", "msg": "Missing 'state' in request"}), 400

    state = data["state"]
    storeDb = db.getDB()
    title = "Fan Update"
    summary = f"Fan {'ON' if state else 'OFF'}"
    extended = f"The fan was turned {'ON' if state else 'OFF'} via the store dashboard."

    storeDb.execute('''
        INSERT INTO notifications (notif_type, notif_title, notif_msg_summary, notif_msg_extended)
        VALUES (?, ?, ?, ?)
    ''', ("system", title, summary, extended))
    storeDb.commit()
    storeDb.close()

    try:
        email_service.send_fan_toggle_email(state)
    except Exception as e:
        print("Fan email failed:", e)

    return jsonify({"status": "ok", "summary": summary})



@app.route('/threshold/update', methods=['POST'])
def update_threshold():
    data = request.get_json()
    fridge = data.get("fridge")
    t_min = data.get("tempMin")
    t_max = data.get("tempMax")
    h_min = data.get("humMin")
    h_max = data.get("humMax")

    title = f"Fridge {fridge} Threshold Updated"
    summary = f"Temp: {t_min}-{t_max}°C | Humidity: {h_min}-{h_max}%"
    extended = f"Thresholds updated for Fridge {fridge}:\nTemperature: {t_min}-{t_max} °C\nHumidity: {h_min}-{h_max} %"

    storeDb = db.getDB()
    storeDb.execute('''
        INSERT INTO notifications (notif_type, notif_title, notif_msg_summary, notif_msg_extended)
        VALUES (?, ?, ?, ?)
    ''', ("system", title, summary, extended))
    storeDb.commit()
    storeDb.close()

    try:
        from services.email_service import send_system_alert_email
        send_system_alert_email(title, extended)
    except Exception as e:
        print("Threshold email failed:", e)

    return jsonify({"status": "ok", "summary": summary})


# -----------------------------
# INBOX
# -----------------------------
@app.route("/inbox", endpoint='viewInbox')

# -----------------------------
# INBOX
# -----------------------------
@app.route("/inbox", endpoint='viewInbox')
def storeInbox():
    try:
        emails = email_service.fetch_store_emails()
        print("Fetched emails:", len(emails))
    except Exception as e:
        print("Inbox error:", e)
        emails = []

    return render_template("viewInbox.html", emails=emails)


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
    return render_template("viewInbox.html", emails=emails)


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route('/admin-dashboard')
def adminDashboard():
    if session.get('user_role') != 'admin':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    all_users = storeDb.execute('SELECT * FROM users ORDER BY user_created_at DESC').fetchall()
    staff = storeDb.execute('SELECT * FROM users WHERE user_role IN ("admin","employee")').fetchall()
    user_notifications = storeDb.execute('''
        SELECT * FROM notifications
        WHERE notif_id IS NOT NULL
        ORDER BY notif_created_at DESC
        LIMIT 5
    ''').fetchall()
    total_users = storeDb.execute('SELECT COUNT(*) as cnt FROM users').fetchone()['cnt']
    verified_users = storeDb.execute('SELECT COUNT(*) as cnt FROM users WHERE user_verified=1').fetchone()['cnt']
    latest_user = storeDb.execute('SELECT * FROM users ORDER BY user_created_at DESC LIMIT 1').fetchone()
    popular_user = storeDb.execute('''
        SELECT users.*, COUNT(customers.customer_id) as posts
        FROM users
        LEFT JOIN customers ON users.user_id = customers.user_id
        GROUP BY users.user_id
        ORDER BY posts DESC
        LIMIT 1
    ''').fetchone()
    storeDb.close()

    db_stats = {
        "total_users": total_users,
        "verified_users": verified_users,
        "latest_user": latest_user,
        "most_popular_user": popular_user
    }

    return render_template(
        'adminDashboard.html',
        all_users=all_users,
        staff=staff,
        notifications=user_notifications,
        db_stats=db_stats
    )

# -----------------------------
# ADMIN USER UPDATE / DELETE
# -----------------------------
@app.route('/admin/user/<int:user_id>/update', methods=['POST'])
def adminUpdateUser(user_id):
        if session.get('user_role') != 'admin':
            flash("Unauthorized.", "danger")
            return redirect(url_for('store.storeIndex'))

        role = request.form.get('role')
        verified = request.form.get('verified') == 'on'

        storeDb = db.getDB()
        storeDb.execute(
            'UPDATE users SET user_role = ?, user_verified = ? WHERE user_id = ?',
            (role, verified, user_id)
        )
        storeDb.commit()
        storeDb.close()

        flash("User updated successfully.", "success")
        return redirect(url_for('store.adminDashboard'))


@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
def adminDeleteUser(user_id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    storeDb.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    storeDb.commit()
    storeDb.close()

    flash("User deleted successfully.", "success")
    return redirect(url_for('store.adminDashboard'))

@app.route('/admin-dashboard/reports/customers')
def reportCustomers():   
    storeDb = db.getDB() 
    date = datetime.datetime.today() -  datetime.timedelta(weeks=1)
    new_customer = storeDb.execute('''SELECT users.*, COUNT(users.user_id) as customers FROM users where user_role = 'customer' AND DATE(user_created_at) >  ?''',(date.date(),)).fetchone()
    all_customers = storeDb.execute('''SELECT users.*, COUNT(users.user_id) as customers FROM users where user_role = 'customer' ''').fetchone()
    old_customers = new_customer = storeDb.execute('''SELECT users.*, COUNT(users.user_id) as customers FROM users where user_role = 'customer' AND DATE(user_created_at) <  ?''',(date.date(),)).fetchone()
    return render_template("customerReport.html",new_customers=new_customer,all_customers=all_customers,old_customers=old_customers) 

@app.route('/admin-dashboard/reports/customers/fetch')
def reportCustomersFetch():   
    storeDb = db.getDB() 
    date = request.args.get('start')
    date = request.args.get('end')
    query = '''
    SELECT DATE(user_created_at) as date,COUNT(user_id) as customer_count from users
    WHERE user_role  = 'customer'
    '''
    params = []
    if request.args.get('start') is not None:
        query = query +' AND DATE(date) > ?'
        params.append(request.args.get('start'))
    if request.args.get('end') is not None:
        params.append(request.args.get('end'))
        query = query + ' AND DATE(date) < ?'

    query = query + ' GROUP BY date'
    customers = storeDb.execute(query,params).fetchall()

    json_data = json.dumps( [dict(ix) for ix in customers] )
    if(customers.__sizeof__() < 50):
        json_data = '[{"customers": 0}]'
    
    return json_data

@app.route('/admin-dashboard/reports/inventory')
def reportInventory():   
    storeDb = db.getDB() 
    products = storeDb.execute('''
        SELECT p.*,DATE(p.product_updated_at) as last_restock, c.category_type
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
    ''').fetchall()

    return render_template("inventoryReport.html",products=products ) 

@app.route('/admin-dashboard/reports/inventory/fetch')
def reportInventoryFetch():   
    storeDb = db.getDB() 
    products = storeDb.execute('''
        SELECT p.*, c.category_type
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
    ''').fetchall()
    json_data = json.dumps( [dict(ix) for ix in products] )
    return json_data

@app.route('/admin-dashboard/reports/sales')
def reportSales():   
    storeDb = db.getDB() 
    products = storeDb.execute('''
       SELECT  p.* ,SUM(op.order_product_quantity) as quantity_sold  FROM orders o
 LEFT JOIN order_products op on o.order_id = op.order_id
 LEFT JOIN products p on op.product_id = p.product_id
GROUP BY p.product_id
    ''').fetchall()
    return render_template("salesReport.html", products=products ) 

@app.route('/admin-dashboard/reports/sales/fetch')
def reportSalesFetch():   

    storeDb = db.getDB() 
    params= []
    query = '''
       SELECT  p.* ,SUM(op.order_product_quantity) as quantity_sold  FROM orders o
     LEFT JOIN order_products op on o.order_id = op.order_id
     LEFT JOIN products p on op.product_id = p.product_id WHERE 1=1
    '''
    print(request.args.get('start'))
    if request.args.get('start') is not None:
        query = query +' AND DATE(o.order_created_at) > ?'
        params.append(request.args.get('start'))
    if request.args.get('end') is not None:
        params.append(request.args.get('end'))
        query = query + ' AND DATE(o.order_created_at) < ?'
    query = query + 'GROUP BY p.product_id Order BY quantity_sold'
    products = storeDb.execute(query,params).fetchall()
    json_data = json.dumps( [dict(ix) for ix in products] )
    return json_data

# -----------------------------
# PRODUCTS / CART / CHECKOUT
# -----------------------------
@app.route('/products-gallery')
def productGallery():
    storeDb = db.getDB()
    products = storeDb.execute('''
        SELECT p.*, c.category_type
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
    ''').fetchall()
    categories = [row['category_type'] for row in storeDb.execute('SELECT DISTINCT category_type FROM categories').fetchall()]
    storeDb.close()
    return render_template('productGallery.html', products=products, categories=categories)


@app.route('/cart')
def cartPage():
    if 'user_email' not in session:
        flash("You need to log in to view your cart.", "warning")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    user = storeDb.execute("SELECT user_id FROM users WHERE user_email = ?", (session['user_email'],)).fetchone()
    cart_items = []

    if user:
        cart = storeDb.execute("SELECT * FROM cart WHERE user_id = ?", (user['user_id'],)).fetchone()
        if cart:
            cart_items = storeDb.execute("""
                SELECT cp.cart_product_id, cp.cart_product_quantity, cp.cart_product_price, p.product_name, p.product_id
                FROM cart_products cp
                JOIN products p ON cp.product_id = p.product_id
                WHERE cp.cart_id = ?
            """, (cart['cart_id'],)).fetchall()

    cart_total = sum(item['cart_product_quantity'] * item['cart_product_price'] for item in cart_items)
    storeDb.close()
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)


@app.route('/cart/add', methods=['POST'])
def addToCart():
    if 'user_email' not in session:
        flash("Please log in to add items to cart.", "warning")
        return redirect(url_for('store.storeIndex'))

    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    storeDb = db.getDB()
    user = storeDb.execute("SELECT user_id FROM users WHERE user_email = ?", (session['user_email'],)).fetchone()

    if not user:
        storeDb.close()
        flash("User not found.", "danger")
        return redirect(url_for('store.storeIndex'))

    cart = storeDb.execute("SELECT * FROM cart WHERE user_id = ?", (user['user_id'],)).fetchone()
    if not cart:
        cur = storeDb.execute("INSERT INTO cart (user_id) VALUES (?)", (user['user_id'],))
        storeDb.commit()
        cart_id = cur.lastrowid
    else:
        cart_id = cart['cart_id']

    cart_product = storeDb.execute("""
        SELECT * FROM cart_products
        WHERE cart_id = ? AND product_id = ?
    """, (cart_id, product_id)).fetchone()

    if cart_product:
        new_qty = cart_product['cart_product_quantity'] + quantity
        storeDb.execute("""
            UPDATE cart_products
            SET cart_product_quantity = ?
            WHERE cart_product_id = ?
        """, (new_qty, cart_product['cart_product_id']))
    else:
        product_price = storeDb.execute("SELECT product_price FROM products WHERE product_id = ?", (product_id,)).fetchone()['product_price']
        storeDb.execute("""
            INSERT INTO cart_products (cart_id, product_id, cart_product_quantity, cart_product_price)
            VALUES (?, ?, ?, ?)
        """, (cart_id, product_id, quantity, product_price))

    storeDb.commit()
    storeDb.close()
    flash("Product added to cart!", "success")
    return redirect(request.referrer or url_for('store.productGallery'))


# @app.route('/self-checkout')
# def selfCheckout():
#     storeDb = db.getDB()
#     cart_items = []
#     cart_total = 0.0
#     storeDb.close()
#     return render_template('selfCheckout.html', cart_items=cart_items, cart_total=cart_total)
@app.route('/self-checkout')
def selfCheckout():
    # Pull data from session instead of triggering a new hardware scan
    cart_items = session.get('cart_items', [])
    cart_total = session.get('cart_total', 0.0)

    return render_template('selfCheckout.html', 
                           cart_items=cart_items, 
                           cart_total=cart_total)

@app.route('/self-checkout/submit', methods=['POST'])
def selfCheckoutSubmit():
    storeDb = db.getDB()
    customer_email = request.form.get('email')
    payment_method = request.form.get('payment_method')
    
    # 1. Check if they WANT to use their points (checkbox from our previous step)
    use_discount = request.form.get('use_discount') == 'true'
    
    # 2. Basic Cart Validation
    rfid_items = session.get('cart_items', [])
    manual_items = session.get('manual_items', [])
    all_items = rfid_items + manual_items

    if not all_items:
        flash("No items found in basket.", "danger")
        return redirect(url_for('store.selfCheckout'))

    # Initialize variables for the flow
    subtotal = sum(item['product_price'] for item in all_items)
    user_id = None
    current_points = 0
    discount_applied_msg = ""

    # 3. User Lookup (Check if they are a loyalty member)
    try:
        user = storeDb.execute('SELECT * FROM users WHERE user_email = ?', (customer_email,)).fetchone()
        if user:
            user_id = int(user['user_id'])
            current_points = user['user_loyalty_points'] or 0
            print(f"DEBUG: Found User {user_id} with {current_points} points.")
    except Exception as e:
        print(f"DEBUG: User lookup failed: {e}")

    # 4. Handle $5 Discount Logic (Redemption)
    # Only applies if user exists, has 50+ points, AND checked the box
    if use_discount and user_id and current_points >= 50:
        print("DEBUG: Redeeming 50 points for $5 discount.")
        discount_applied_msg = f"Subtotal before discount: ${subtotal:.2f}\nCongrats! $5.00 discount applied from loyalty points!"
        
        subtotal -= 5.0
        current_points -= 50  # Deduct the points immediately
        
        # Update DB for the deduction
        storeDb.execute('UPDATE users SET user_loyalty_points = ? WHERE user_id = ?', (current_points, user_id))
        storeDb.commit()
    else:
        print("DEBUG: No discount applied (Either opted out or insufficient points).")

    # 5. Calculate Final Financials
    gst = round(subtotal * 0.05, 2)
    qst = round(subtotal * 0.09975, 2)
    total = round(subtotal + gst + qst, 2)

    try:
        # 6. Create the Order Record
        cur = storeDb.execute('''
            INSERT INTO orders (order_total, payment_method, order_status, customer_email)
            VALUES (?, ?, ?, ?)
        ''', (total, payment_method, 'COMPLETED', customer_email))
        order_id = cur.lastrowid

        # 7. Add Products to order_products table
        for item in all_items:
            pid = item.get('product_id')
            # Fallback if product_id is missing from session
            if not pid:
                res = storeDb.execute('SELECT product_id FROM products WHERE product_name = ?', (item['product_name'],)).fetchone()
                pid = res['product_id'] if res else None
            
            if pid:
                storeDb.execute('''
                    INSERT INTO order_products (order_id, product_id, order_product_quantity, order_product_unit_price)
                    VALUES (?, ?, 1, ?)
                ''', (order_id, pid, item['product_price']))
                storeDb.execute('''
                        UPDATE products 
                        SET product_stock_quantity = product_stock_quantity - 1
                        WHERE product_id = ?
                        AND product_stock_quantity > 0
                         ''', (pid,))

        # 8. Calculate and Add Points Earned from THIS purchase
        # Points are usually earned on the subtotal AFTER discounts
        points_earned = int(subtotal // 10) 
        total_points_final = current_points # Default if guest
        
        if user_id:
            total_points_final = current_points + points_earned
            storeDb.execute('UPDATE users SET user_loyalty_points = ? WHERE user_id = ?', (total_points_final, user_id))
            print(f"DEBUG: User earned {points_earned}. New Balance: {total_points_final}")

        storeDb.commit()

        # 9. Prepare and Send Receipt
        receipt_data = {
            'discount' : discount_applied_msg,
            'items': all_items,
            'total': total,
            'subtotal': subtotal,
            'gst': gst,
            'qst': qst,
            'timestamp': session.get('cart_timestamp', 'N/A'),
            'purchase_points': points_earned, # MUST be 'purchase_points' to match your Class
            'total_points': total_points_final      # This matches your if/else in the Class
        }

        # Send via your Email Service
        receipt_sender = EmailAlertSystem(
            sender_email="taliamuro3@gmail.com",
            password="hapc ypha dcwh ewbc", # Note: Usually better in environment variables!
            receiver_email=customer_email
        )
        receipt_sender.send_receipt_email(customer_email, receipt_data)

        # 10. Clean up Session
        session.pop('cart_items', None)
        session.pop('manual_items', None)
        session.pop('current_points', None)
        session.modified = True

        flash(f"Success! Order #{order_id} complete. Receipt sent to {customer_email}", "success")

    except Exception as e:
        storeDb.rollback()
        print(f"CRITICAL ERROR during checkout: {e}")
        flash("There was an error processing your order. Please contact staff.", "danger")
    finally:
        storeDb.close()

    return redirect(url_for('store.storeIndex'))

@app.route('/api/check-loyalty/<email>') 
def check_loyalty(email):
    try:
        storeDb = db.getDB()
        # Use .fetchone() so we get a dictionary-like object
        user = storeDb.execute('SELECT user_loyalty_points FROM users WHERE user_email = ?', (email,)).fetchone()
        storeDb.close()
        
        if user:
            # Safely handle None values for points
            pts = user['user_loyalty_points'] if user['user_loyalty_points'] is not None else 0
            return jsonify({
                "exists": True, 
                "points": pts, 
                "eligible": pts >= 50
            })
        
        return jsonify({"exists": False})
    except Exception as e:
        print(f"LOYALTY ERROR: {e}")
        return jsonify({"exists": False, "error": str(e)}), 500
# -----------------------------
# RFID ROUTES
# -----------------------------

# Test function
rfid_service = RFIDService()

@app.route('/api/scan-rfid', methods=['GET'])
def scan_rfid():
    raw_tags = ["A00000000000000000004954", "A00000000000000000004955", "A00000000000000000004953", "A00000000000000000004959"] 
    
    # Process the scan
    products = rfid_service.get_products_from_scan(raw_tags)
    
    # Return the shopping list
    return jsonify({
        "items": products,
        "count": len(products)
    })

@app.route('/api/scan-basket')
def scan_basket():
    tags = rfid_service.perform_basket_scan(scan_duration=2.0)
    
    # Get the product data
    receipt = rfid_service.manager.process_simultaneous_scan(tags)
    
    if receipt:
        session['cart_items'] = receipt['items']
        session['cart_subtotal'] = receipt['subtotal']
        session['cart_total'] = receipt['total']
        session['cart_gst'] = receipt['gst']
        session['cart_qst'] = receipt['qst']
        session['cart_total'] = receipt['total']
        session['cart_timestamp'] = receipt['timestamp']

        # Ensures flask saves
        session.modified = True
    else:
        # Clear session if the basket is empty
        keys_to_clear = ['cart_items', 'cart_subtotal', 'cart_gst', 'cart_qst', 'cart_total']
        for key in keys_to_clear:
            session.pop(key, None)
        
    return jsonify(receipt if receipt else {"item_count": 0})

rfid_service = RFIDService()

@app.route('/api/add-barcode/<code>', methods=['POST'])
def add_barcode(code):
    # Change getDB() to db.getDB()
    storeDb = db.getDB() 
    
    query = '''
        SELECT p.product_name, p.product_price, p.product_company,p.product_stock_quantity
        FROM products p
        JOIN product_barcode pb ON p.product_id = pb.product_id
        WHERE pb.barcode_num = ?
    '''


    
    product = storeDb.execute(query, (code,)).fetchone()
    storeDb.close()


    if product:
        if product['product_stock_quantity'] == 0:
           return jsonify({"status": "Out_of_Stock"}), 418
        # different session key for barcode scans
        manual_cart = session.get('manual_items', [])
        manual_cart.append({
            'product_name': product['product_name'],
            'product_price': product['product_price'],
            'product_company': product['product_company'],
            'source': 'barcode' # Helpful for debugging
        })
        session['manual_items'] = manual_cart
        session.modified = True
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "not_found"}), 404

@app.route('/api/remove-barcode/<int:index>', methods=['POST'])
def remove_barcode(index):
    manual_cart = session.get('manual_items', [])
    
    # Check if the index is valid
    if 0 <= index < len(manual_cart):
        manual_cart.pop(index)
        session['manual_items'] = manual_cart
        session.modified = True
        return jsonify({"status": "success"}), 200
        
    return jsonify({"status": "error", "message": "Item not found"}), 404

# -----------------------------
# TEMPERATURE & HARDWARE ROUTES
# -----------------------------

# 1. The main page route
@app.route('/admin-dashboard/temperature')
def temperatureMonitor():
    """
    Renders the dedicated IoT monitoring page.
    This page contains the JavaScript and Gauges.
    """
    return render_template('temperature.html')

# 2. The Data API (The "Pulse")
@app.route('/api/temp-data')
def get_temp_data():
    """
    The frontend JavaScript polls this endpoint every 2 seconds.
    It returns the latest values from the background MQTT thread.
    """
    return hardware_status

# 3. The Hardware Action API
@app.route('/api/fan/<state>')
def set_fan(state):
    if state == "on":
        motor_control("on")
    else:
        motor_control("off")
    
    # Return the new state so the dashboard stays in sync
    return {"status": "success", "fan_on": hardware_status["fan_on"]}

# BLE sensor data reading route
@app.route('/ble-scan')
def ble_scan():
    from scripts import BLEsensor
    import logging

# This silences the specific logger for Werkzeug (Flask's server)
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)
    data = BLEsensor.get_data()
    print(data)
    # Extract values for the response
    ht = data["HT"]
    ps = data["light"]
    batteryState = data["batteryState"]
    
    # Fix the PIR list issue here
    motion = data["motion"]
    if isinstance(motion, list):
        motion = motion[0]

    
    return jsonify({
        "PS": ps, 
        "HT": {"temperature": ht["temperature"], "humidity": ht["humidity"]}, 
        "PIR": motion, 
        "batteryState": batteryState
    })
    
@app.route('/admin-dashboard/ble-scan-view')
def ble_scan_view():
    return render_template('BLESensorData.html')

# Get scan for adding new product
@app.route('/api/scan-single-tag')
def scan_single_tag():
    try:
        # This calls your specific logic from rfid_service.py
        tags = rfid_svc.perform_basket_scan(scan_duration=1.5)
        if tags and len(tags) > 0:
            return jsonify({"success": True, "tag": tags[0]})
        return jsonify({"success": False, "error": "No tag found in range"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
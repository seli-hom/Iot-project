from flask import render_template, request, Blueprint, session, redirect, url_for, flash, jsonify
from models import database as db
from models import customers, users
from services import email_service
import bcrypt
from services.rfid_service import RFIDService
from services.receipt_service import EmailAlertSystem
from services.rfid_service import RFIDService
from services.receipt_service import EmailAlertSystem

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

@app.route('/admin-dashboard/products')
def productsList():
    storeDb = db.getDB()
    products = storeDb.execute(
        'SELECT * FROM products '
    ).fetchall()
    return render_template('productsList.html', products=products)

@app.route('/admin-dashboard/products/create')
def productCreate():
    return render_template('productCreation.html')

@app.route('/admin-dashboard/products/add', methods=['POST'])
def productAdd():

    storeDb = db.getDB()
    test = storeDb.execute('''
                INSERT INTO products (product_name, category_id, product_price, product_company, product_description)
                VALUES (?, ?, ?, ?, ?)
            ''', (request.form['product_name'],request.form['product_category'], request.form['product_price'], request.form['product_company'], request.form['product_description']))
    storeDb.commit()
    print(test.lastrowid)
    return redirect(url_for('store.productsList'))

@app.route('/admin-dashboard/products/<int:product_id>/delete', methods=['POST', 'GET'])
def productDelete(product_id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    storeDb.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
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
        try:
            cur = storeDb.execute('''
                INSERT INTO users (user_fname, user_lname, user_email, user_password, user_role, user_verified)
                VALUES (?, ?, ?, ?, 'customer', 0)
            ''', (request.form['fname'], request.form['lname'], request.form['email'], bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())))
   
            storeDb.commit()
            new_user_id = cur.lastrowid
    
            # Then create the customer profile
           # from models import customers
            #customer_id = customers.add_new_customer(
              #  new_user_id,
              #  request.form['phone'],
              #  request.form['address']
            #)
           # from models import customers
            #customer_id = customers.add_new_customer(
              #  new_user_id,
              #  request.form['phone'],
              #  request.form['address']
            #)

          #  if not customer_id:
             #   raise Exception("Failed to create customer profile")
          #  if not customer_id:
             #   raise Exception("Failed to create customer profile")

            # Send verification email
            try:
                # -------------------------------
                # Send registration email
                # -------------------------------
                from services.email_service import send_registration_email
                send_registration_email(
                    request.form['fname'],
                    request.form['lname'],
                    request.form['email'],
                    new_user_id
                )
                message = "Customer invited successfully. Verification email sent!"
                success = True


            except Exception as e:
                import traceback
                print("Email sending failed:", e)
                traceback.print_exc()
                message = "User created, but email failed."
                success = False

        except Exception as e:
            print("Error creating user:", e)
            message = "Error creating user"
            success = False


        finally:
            storeDb.close()

    return render_template(
        'customersRegistration.html',
        message=message,
        success=success
    )


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
    customer_email = request.form.get('email')
    payment_method = request.form.get('payment_method')
    
    rfid_items = session.get('cart_items', [])
    manual_items = session.get('manual_items', [])
    all_items = rfid_items + manual_items

    if not all_items:
        flash("No items found in basket.", "danger")
        return redirect(url_for('store.selfCheckout'))

    # Calculate and round taxes/total
    subtotal = sum(item['product_price'] for item in all_items)
    gst = round(subtotal * 0.05, 2)
    qst = round(subtotal * 0.09975, 2)
    total = round(subtotal + gst + qst, 2)

    storeDb = db.getDB()
    try:
        # 1. ATTEMPT TO FIND THE USER
        user = storeDb.execute('SELECT user_id FROM users WHERE user_email = ?', (customer_email,)).fetchone()
        user_id = user['user_id'] if user else None # for unregistered users

        # Create the order
        # user_id will be NULL for guest checkout
        cur = storeDb.execute('''
            INSERT INTO orders (user_id, order_total, payment_method, order_status)
            VALUES (?, ?, ?, 'COMPLETED')
        ''', (user_id, total, payment_method))
        order_id = cur.lastrowid

        # 3. add products to order table
        for item in all_items:
            pid = item.get('product_id') 
            if not pid:
                res = storeDb.execute('SELECT product_id FROM products WHERE product_name = ?', (item['product_name'],)).fetchone()
                pid = res['product_id'] if res else None
            
            if pid:
                storeDb.execute('''
                    INSERT INTO order_products (order_id, product_id, order_product_quantity, order_product_unit_price)
                    VALUES (?, ?, 1, ?)
                ''', (order_id, pid, item['product_price']))

        # Loylaty logic if user exists
        if user_id:
            points_earned = int(subtotal)
            customer = storeDb.execute('SELECT customer_id FROM customers WHERE user_id = ?', (user_id,)).fetchone()
            
            if customer:
                cid = customer['customer_id']
                storeDb.execute('''
                    UPDATE customer_loyalty 
                    SET loyalty_points = loyalty_points + ?, loyalty_updated_at = CURRENT_TIMESTAMP
                    WHERE customer_id = ?
                ''', (points_earned, cid))
                
                storeDb.execute('''
                    INSERT INTO loyalty_transactions (customer_id, transaction_type, transaction_points, transaction_description)
                    VALUES (?, 'EARN', ?, ?)
                ''', (cid, points_earned, f"Points earned from Order #{order_id}"))

        storeDb.commit()

        # send email receipt
        receipt_data = {
            'items': all_items,
            'total': total,
            'subtotal': subtotal,
            'gst': gst,
            'qst': qst,
            'timestamp': session.get('cart_timestamp', 'N/A')
        }
        receipt_sender = EmailAlertSystem(
            sender_email="taliamuro3@gmail.com",
            password="hapc ypha dcwh ewbc",
            receiver_email=customer_email
        )
        receipt_sender.send_receipt_email(customer_email, receipt_data)
        
        # Clear session
        session.pop('cart_items', None)
        session.pop('manual_items', None)
        session.modified = True
        
        message = "Success! Receipt sent."
        if user_id:
            message = f"Success! {points_earned} points added and receipt sent."
        
        flash(message, "success")
        
    except Exception as e:
        storeDb.rollback()
        print(f"Checkout Database Error: {e}")
        flash("Order completed, but there was an error updating your profile.", "warning")
    finally:
        storeDb.close()

    return redirect(url_for('store.storeIndex'))

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
        SELECT p.product_name, p.product_price, p.product_company 
        FROM products p
        JOIN product_barcode pb ON p.product_id = pb.product_id
        WHERE pb.barcode_num = ?
    '''
    
    product = storeDb.execute(query, (code,)).fetchone()
    storeDb.close()

    if product:
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

from flask import render_template, request, Blueprint, session, redirect, url_for, flash, jsonify
from models import database as db
from models import customers
from services import email_service
import bcrypt 
from scripts import getTemp

app = Blueprint('store', __name__)

@app.route('/')
def storeIndex():
    return render_template('index.html')

@app.route('/store-dashboard')
def storeDashboard():
    storeDb = db.getDB()

    notifications = storeDb.execute('''
        SELECT * FROM notifications
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()

    storeDb.close()

    return render_template(
        'storeDashboard.html',
        notifications=notifications,
        temp=4,
        hm=65,
        type="Notice"
    )

@app.route('/api/notifications')
def get_notifications():
    storeDb = db.getDB()
    try:
        notifications = storeDb.execute('''
            SELECT id, type, title, msg_summary, msg_extended, created_at
            FROM notifications
            ORDER BY created_at DESC
            LIMIT 10
        ''').fetchall()

        notif_list = [
            {
                "id": n["id"],
                "type": n["type"],
                "title": n["title"],
                "summary": n["msg_summary"],
                "extended": n["msg_extended"],
                "created_at": n["created_at"]
            } for n in notifications
        ]

        return jsonify(notif_list)
    except Exception as e:
        print("Error fetching notifications:", e)
        return jsonify([]), 500
    finally:
        storeDb.close()
        
@app.route('/customers')
def customersList():
    all_customers = customers.select_customers()
    return render_template('customersList.html', customers=all_customers)

@app.route('/temp')
def get_temp():
    data = getTemp.get_temp()
    print(data)
    return  data

@app.route('/customers/registration', methods=['GET', 'POST'])
def customersRegistration():
    message = None
    success = None
    if request.method == 'POST':
        new_customer_id = customers.add_new_customer(
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form['phone'],
            request.form['address']
        )
        
        if new_customer_id:
            try:
                from services.email_service import send_registration_email
                send_registration_email(
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    new_customer_id
                )
                message = "Customer added successfully. Verification email sent!"
                success = True
            except Exception as e:
                print("Email sending failed:", e)
                message = "Customer added, but failed to send verification email."
                success = False
        else:
            message = "Error: Customer could not be added."
            success = False
            
    return render_template('customersRegistration.html', message=message, success=success)

@app.route('/verify/<int:customer_id>', methods=['GET', 'POST'])
def customerVerification(customer_id):
    storeDb = db.getDB()

    user = storeDb.execute('SELECT * FROM users WHERE id = ?', (customer_id,)).fetchone()
    
    message = None
    success = None

    if not user:
        message = "Invalid verification link."
        success = False
        storeDb.close()
        return render_template('customersVerification.html', message=message, success=success)

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            message = "Please fill in both password fields."
            success = False
        elif password != confirm_password:
            message = "Passwords do not match. Please try again."
            success = False
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            storeDb.execute(
                'UPDATE users SET password = ?, verified = 1 WHERE id = ?', 
                (hashed_pw, customer_id)
            )
            storeDb.commit()

            message = "Your account has been verified!"
            success = True

            try:
                from services.email_service import send_new_customer_notification
                send_new_customer_notification(
                    user['first_name'],
                    user['last_name'],
                    user['email']
                )
            except Exception as e:
                print("Email fail:", e)

    storeDb.close()
    return render_template('customersVerification.html', message=message, success=success)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    storeDb = db.getDB()

    user = storeDb.execute('''
        SELECT users.*, customers.phone, customers.address
        FROM users
        JOIN customers ON users.id = customers.user_id
        WHERE users.email = ?
    ''', (email,)).fetchone()

    storeDb.close()

    if not user:
        return redirect(url_for('store.storeIndex'))

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['user_email'] = user['email']
        session['user_first_name'] = user['first_name']

    return redirect(url_for('store.storeIndex'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('store.storeIndex'))

<<<<<<< Updated upstream
@app.route('/fan/<int:id>', methods=['POST'])
def toggle_fan(id):
=======
@app.route('/admin-dashboard/orders')
def customerOrders():   
    storeDb = db.getDB() 
    orders = storeDb.execute('''SELECT  SUM(order_total) as total,DATE(order_created_at) as date, op.* FROM orders o
        LEFT JOIN order_products op  on op.order_id = o.order_id
        GROUP BY DATE(order_created_at)
     ORDER BY o.order_created_at DESC''').fetchall()
    return render_template("CustomerOrders.html", orders=orders) 


@app.route('/admin-dashboard/report/<int:id>')
def orderDetails(id):   
    storeDb = db.getDB() 
    orders = storeDb.execute('''SELECT * FROM orders where user_id = ?''', (id,)).fetchall()
    return render_template("OrderDetails.html",  orders=orders) 

@app.route('/admin-dashboard/orders/<string:date>')
def orderData(date):   
    storeDb = db.getDB() 
    orders = storeDb.execute('''SELECT * FROM orders where DATE(order_created_at) = ?''', (date,)).fetchall()
    json_data = json.dumps( [dict(ix) for ix in orders] )
    
    return  json_data


@app.route('/admin-dashboard/orders/<int:id>')
def orderClientData(id):   
    storeDb = db.getDB() 
    orders = storeDb.execute('''SELECT * FROM orders WHERE user_id = ?''', (id,)).fetchall()
    json_data = json.dumps( [dict(ix) for ix in orders] )
    
    return  json_data


@app.route('/admin-dashboard/orders/<string:date>/download')
def downloadReport(date):   
    storeDb = db.getDB() 
    orders = storeDb.execute('''SELECT * FROM orders where DATE(order_created_at) = ?''', (date,)).fetchall()
    with open("reports/"+date+".csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(orders)
    return redirect(url_for('store.customerOrders'))
# -----------------------------
# FAN / THRESHOLD ROUTES
# -----------------------------
@app.route('/fan', methods=['POST'])
def toggle_fan():
>>>>>>> Stashed changes
    data = request.get_json()
    state = data.get("state")  

    title = "Fan Update"
    summary = f"Fan {'ON' if state else 'OFF'}"
    extended = f"The fan with ID {id} was turned {'ON' if state else 'OFF'} via the store dashboard."

    storeDb = db.getDB()
    storeDb.execute('''
        INSERT INTO notifications (type, title, msg_summary, msg_extended)
        VALUES (?, ?, ?, ?)
    ''', ("system", title, summary, extended))
    storeDb.commit()
    storeDb.close()

    try:
        from services.email_service import send_system_alert_email
        send_system_alert_email(title, extended)
    except Exception as e:
        print("System alert email failed:", e)

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
        INSERT INTO notifications (type, title, msg_summary, msg_extended)
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

@app.route('/store-inbox')
def storeInbox():
    emails = email_service.fetch_store_emails()
    return render_template('viewInbox.html', emails=emails)
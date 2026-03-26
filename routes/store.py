from flask import render_template, request, Blueprint, session, redirect, url_for, flash, jsonify
from models import database as db
from models import customers, users
from services import email_service
import bcrypt
from public.assets.python import phase_2

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
        type="Notice",
        kitchen_temp=kitchen_temp,
        kitchen_hum=kitchen_hum,
        room_temp=room_temp,
        room_hum=room_hum,
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

@app.route('/customers/registration', methods=['GET', 'POST'])
def customersRegistration():
    message = None
    success = None
    if request.method == 'POST':
        # First, create the user
        storeDb = db.getDB()
        try:
            cur = storeDb.execute('''
                INSERT INTO users (first_name, last_name, email, role, verified)
                VALUES (?, ?, ?, 'customer', 0)
            ''', (request.form['first_name'], request.form['last_name'], request.form['email']))
            storeDb.commit()
            new_user_id = cur.lastrowid

            # Then create the customer profile
            from models import customers
            customer_id = customers.add_new_customer(
                new_user_id,
                request.form['phone'],
                request.form['address']
            )

            if not customer_id:
                raise Exception("Failed to create customer profile")

            # Send verification email
            try:
                from services.email_service import send_registration_email
                send_registration_email(
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    new_user_id
                )
                message = "Customer added successfully. Verification email sent!"
                success = True
            except Exception as e:
                print("Email sending failed:", e)
                message = "Customer added, but failed to send verification email."
                success = False

        except Exception as e:
            print("Error creating customer:", e)
            message = "Error: Customer could not be added."
            success = False
        finally:
            storeDb.close()

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
        JOIN customers ON users.id = customers.id
        WHERE users.email = ?
    ''', (email,)).fetchone()
    storeDb.close()

    if not user:
        return redirect(url_for('store.storeIndex'))

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['user_email'] = user['email']
        session['user_first_name'] = user['first_name']
        session['user_role'] = user['role']

    return redirect(url_for('store.storeIndex'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('store.storeIndex'))

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
        INSERT INTO notifications (type, title, msg_summary, msg_extended)
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

@app.route("/inbox", endpoint='viewInbox')  # Route is /inbox, endpoint is viewInbox
def storeInbox():
    try:
        emails = email_service.fetch_store_emails()
        print("Fetched emails:", len(emails))
    except Exception as e:
        print("Inbox error:", e)
        emails = []

    return render_template(
        "viewInbox.html",
        emails=emails
    )

@app.route('/admin-dashboard')
def adminDashboard():
    # if session.get('user_role') != 'admin':
    #     flash("Unauthorized access.", "danger")
    #     return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    all_users = storeDb.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    staff_users = storeDb.execute('SELECT * FROM users WHERE role IN ("admin","employee")').fetchall()

    user_notifications = storeDb.execute('''
        SELECT * FROM notifications
        WHERE id IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 5
    ''').fetchall()

    total_users = storeDb.execute('SELECT COUNT(*) as cnt FROM users').fetchone()['cnt']
    verified_users = storeDb.execute('SELECT COUNT(*) as cnt FROM users WHERE verified=1').fetchone()['cnt']
    latest_user = storeDb.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT 1').fetchone()
    popular_user = storeDb.execute('''
        SELECT users.*, COUNT(customers.id) as posts
        FROM users
        LEFT JOIN customers ON users.id = customers.id
        GROUP BY users.id
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
        staff=staff_users,
        notifications=user_notifications,
        db_stats=db_stats
    )

@app.route('/admin/user/<int:id>/update', methods=['POST'])
def adminUpdateUser(id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('store.storeIndex'))

    role = request.form.get('role')
    verified = request.form.get('verified') == 'on'

    storeDb = db.getDB()
    storeDb.execute(
        'UPDATE users SET role = ?, verified = ? WHERE id = ?',
        (role, verified, id)
    )
    storeDb.commit()
    storeDb.close()

    flash("User updated successfully.", "success")
    return redirect(url_for('store.adminDashboard'))

@app.route('/admin/user/<int:id>/delete', methods=['POST'])
def adminDeleteUser(id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized.", "danger")
        return redirect(url_for('store.storeIndex'))

    storeDb = db.getDB()
    storeDb.execute('DELETE FROM users WHERE id = ?', (id,))
    storeDb.commit()
    storeDb.close()

    flash("User deleted successfully.", "success")
    return redirect(url_for('store.adminDashboard'))
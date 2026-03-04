from flask import render_template, request, Blueprint, session, redirect, url_for, flash
from models import database as db
from models import customers
from services import email_service
import bcrypt 
# from app import app

# blueprint for store routes
app = Blueprint('store', __name__)

@app.route('/')
def storeIndex():
    return render_template('index.html')

@app.route('/customers')
def customersList():
    all_customers = customers.select_customers()
    return render_template('customersList.html', customers=all_customers)

@app.route('/customers/registration', methods=['GET', 'POST'])
def customersRegistration():
    message = None
    success = None
    if request.method == 'POST':
        # adding the customer to the database
        new_customer_id = customers.add_new_customer(
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form['phone'],
            request.form['address']
        )
        
        if new_customer_id:
            # sending verification email to the newly registered customer
            try:
                from services.email_service import send_registration_email
                send_registration_email(
                    request.form['first_name'],
                    request.form['last_name'],
                    request.form['email'],
                    new_customer_id  # passing the customer ID to build the verify link
                )
                message = "Customer has been added to the store db successfully. Verification email sent!"
                success = True
            except Exception as e:
                print("Email sending failed:", e)
                message = "Customer added, but failed to send verification email. Please contact support."
                success = False
        else:
            message = "Error: Customer could not be added to the store db. Please try again."
            success = False
            
    return render_template('customersRegistration.html', message=message, success=success)

# verification route for customers
@app.route('/verify/<int:customer_id>', methods=['GET', 'POST'])
def customerVerification(customer_id):
    storeDb = db.getDB()
    customer = storeDb.execute('SELECT * FROM customers WHERE id = ?', (customer_id,)).fetchone()
    
    message = None
    success = None

    if not customer:
        message = "Invalid verification link."
        success = False
        storeDb.close()
        return render_template('customersVerification.html', message=message, success=success)

    # if POST, the user submitted the password form
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
            # hashing the password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # updating customer password and marking as verified
            storeDb.execute('UPDATE customers SET password = ?, verified = 1 WHERE id = ?', (hashed_pw, customer_id))
            storeDb.commit()
            message = "Your account has been verified and password set! You can now log in."
            success = True

            # ✅ Send notification to store/admin about the new verified user
            try:
                from services.email_service import send_new_customer_notification
                send_new_customer_notification(
                    customer['first_name'],
                    customer['last_name'],
                    customer['email']
                )
            except Exception as e:
                print("Failed to send admin notification email:", e)

    storeDb.close()
    return render_template('customersVerification.html', message=message, success=success)

# login route for navbar form
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    storeDb = db.getDB()
    customer = storeDb.execute('SELECT * FROM customers WHERE email = ?', (email,)).fetchone()
    storeDb.close()

    message = None
    success = None

    if not customer:
        message = "Invalid email or password."
        success = False
    else:
        # Check password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), customer['password']):
            session['user_email'] = customer['email']
            session['user_first_name'] = customer['first_name']
            message = f"Welcome back, {customer['first_name']}!"
            success = True
        else:
            message = "Invalid email or password."
            success = False

    return redirect(url_for('store.storeIndex'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('store.storeIndex'))

# Read Email's Inbox route
@app.route('/store-inbox')
def storeInbox():
    """
    Fetches emails from the store's Gmail inbox and displays them
    """
    # Fetch emails using the function from email_service
    emails = email_service.fetch_store_emails()

    # Render the inbox template with emails
    return render_template('viewInbox.html', emails=emails)
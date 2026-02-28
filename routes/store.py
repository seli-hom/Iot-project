from flask import render_template, request
from models import database as db
from models import customers
from app import app

@app.route('/')
def storeIndex():
    return render_template('index.html')

@app.route('/customers')
def customersList():
    all_customers = customers.select_customers()
    return render_template('customersList.html')

@app.route('/customers/registration', methods=['GET', 'POST'])
def customersRegistration():
    message = None
    success = None
    if request.method == 'POST':
        result = customers.add_new_customer(
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form['phone'],
            request.form['address']
        )
        message = "Customer hsa been added to the store db successfully"
        if not result:
            message = "Error: Customer could not be added to the store db. Please try again."
            
        success = result
    return render_template('customersRegistration.html')

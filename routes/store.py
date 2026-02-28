from flask import Flask, render_template
import database as db
import customers

app = Flask(__name__)

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

if __name__ == '__app__':
    app.run(debug=True, host= '10.0.0.186', port=5000)
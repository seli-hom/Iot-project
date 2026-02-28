from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def storeIndex():
    return render_template('index.html')

@app.route('/customers')
def customersList():
    return render_template('customers/customersList.html')

@app.route('/customers/registration')
def customersRegistration():
    return render_template('customers/customersRegistration.html')
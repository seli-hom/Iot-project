from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def storeIndex():
    return render_template('index.html')

@app.route('/customers')
def customersList():
    return render_template('customersList.html')

@app.route('/customers/registration')
def customersRegistration():
    return render_template('customersRegistration.html')
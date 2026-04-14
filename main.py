DEV_MODE = True

from flask import Flask
from flask_mail import Mail
from models import database as db
from routes.store import app as store

db.init_db()

app = Flask(__name__)
app.register_blueprint(store)

app.secret_key = "iotprojectsmartstore"

# app.config['MAIL_USERNAME'] = 'project.smartstore@gmail.com'
app.config['MAIL_USERNAME'] = 'taliamuro3@gmail.com'
# app.config['MAIL_PASSWORD'] = 'lumsadlznehrqsuv'
app.config['MAIL_PASSWORD'] = 'hapc ypha dcwh ewbc'
app.config['RECEIVER_EMAIL'] = 'efremselihom1@gmail.com'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5000)


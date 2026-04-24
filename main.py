DEV_MODE = True

from flask import Flask
from flask_mail import Mail
from models import database as db
from routes.store import app as store
from services import CheckoutManager
from services.background_tasks import start_mqtt, start_email_checker
import os
from services.receipt_service import EmailAlertSystem

db.init_db()

app = Flask(__name__)

mail_manager = EmailAlertSystem(
    sender_email="taliamuro3@gmail.com",
    password="hapc ypha dcwh ewbc",
    receiver_email="sybrouss@gmail.com"
)

# app.secret_key = "iotprojectsmartstore"
app.secret_key = os.urandom(24)

app.config['MAIL_MANAGER'] = mail_manager

app.register_blueprint(store)

# app.config['MAIL_USERNAME']# if DEV_MODE:
    #     run_rfid_backend_test() = 'project.smartstore@gmail.com'
# app.config['MAIL_PASSWORD'] = 'lumsadlznehrqsuv'
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False

# mail = Mail(app)

if __name__ == '__main__':
    # Pass the instance to the background tasks
    start_mqtt("127.0.0.1", mail_manager)
    start_email_checker(mail_manager)

    app.run(debug=True, host= '0.0.0.0', port=5000, threaded=True, use_reloader=False)
    # app.run(debug=True, host= '0.0.0.0', port=5001)
DEV_MODE = True

from flask import Flask
from flask_mail import Mail
from models import database as db
from routes.store import app as store
from services import CheckoutManager
import os

db.init_db()

app = Flask(__name__)
app.register_blueprint(store)

# app.secret_key = "iotprojectsmartstore"
app.secret_key = os.urandom(24)

app.config['MAIL_USERNAME'] = 'project.smartstore@gmail.com'
app.config['MAIL_PASSWORD'] = 'lumsadlznehrqsuv'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# def run_rfid_backend_test():
#     print("\n--- Starting RFID Backend Test ---")
    
#     # These EPCs match your seeded products in database.py
#     test_scan = [
#         "A00000000000000000004954", # Solo Shadow
#         "A00000000000000000004955", # Apple Love
#         "A00000000000000000004953", # Dew Blush
#         "A00000000000000000004959"  # Sweet Pink Duo
#     ]

#     manager = CheckoutManager(db)
#     receipt = manager.process_simultaneous_scan(test_scan)

#     if receipt:
#         print(f"Items Found: {receipt['item_count']}")
#         for item in receipt['items']:
#             name = item['product_name']
#             brand = item['product_company']
#             price = item['product_price']
#             print(f"  - {name} ({brand}): $ {price}")
        
#         print(f"Subtotal: ${receipt['subtotal']}")
#         print(f"Tax (GST+QST): ${round(receipt['gst'] + receipt['qst'], 2)}")
#         print(f"Total Amount: ${receipt['total']}")
#         print(f"Scan Time: {receipt['timestamp']}")
#     else:
#         print("[ERROR] No products found for the scanned EPCs.")
#     print("--- Test Complete ---\n")

if __name__ == '__main__':
    # if DEV_MODE:
    #     run_rfid_backend_test()

    app.run(debug=True, host= '0.0.0.0', port=5000, threaded=True)
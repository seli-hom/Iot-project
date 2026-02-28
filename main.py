from flask import Flask
from models import database as db
db.init_db()
app = Flask(__name__)
from routes.store import app as store
app.register_blueprint(store)

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5000)
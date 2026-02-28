from flask import Flask
from models import database as db


db.init_db()

from routes.store import *


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5000)
from flask import Flask
import database as db


db.init_db()

from routes import store


if __name__ == '__main__':
    store.app.run(debug=True, host= '0.0.0.0', port=5000)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///ticketing.db'

db = SQLAlchemy(app)

from api import views

if __name__ == '__main__':
    app.run(debug=True)

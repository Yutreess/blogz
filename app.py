# Import Flask functionality
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# App Initialization
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:420Hornze!@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'YeetusYanLeetus'

db = SQLAlchemy(app)
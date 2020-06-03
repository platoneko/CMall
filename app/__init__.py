from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, static_url_path='')
app.config.from_object('config')
db = SQLAlchemy(app)
login = LoginManager(app)

from app import views, models
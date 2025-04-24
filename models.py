from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    email_sha256 = db.Column(db.String(64), nullable=True)

# ParsingResult model
class ParsingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    xpath = db.Column(db.String(200), nullable=False)
    result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now()) 
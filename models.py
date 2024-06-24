from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

# User model for authentication and user management
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(1000), nullable=True)
    eth_public_address = db.Column(db.String(255), nullable=True)
    eth_private_address = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# NFT model to store NFTs associated with users (optional)
class NFT(db.Model):
    token_id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))  # Add description column
    name = db.Column(db.String(100), nullable=False)
    stockX = db.Column(db.String(200), nullable=False)


# Function to create database tables (usually in a separate script or at app start)
def create_tables():
    db.create_all()

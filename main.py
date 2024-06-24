import json
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from auth import auth as auth_blueprint
from nft import nft as nft_blueprint
from buy_sell import buy_sell as buy_sell_blueprint
from flask_sqlalchemy import SQLAlchemy
from database import db, create_tables
from solcx import compile_standard, install_solc
from web3 import Web3

install_solc('0.8.20')

app = Flask(__name__)

nft_list = dict()
NUMBER_OF_NFT = 5
# Configuration

app.config['SECRET_KEY'] = 'a2c1860805e9db909cda982e14de5b503c2b3f423b27bf4fe371f5402ec7d1d4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sneakers_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    create_tables()

# Initialize LoginManager for handling user sessions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# Function to load the current user
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


# Register authentication blueprint
app.register_blueprint(auth_blueprint)

# Register NFT blueprint with a URL prefix
app.register_blueprint(nft_blueprint, url_prefix='/nft')
# app.register_blueprint(buy_sell_blueprint, url_prefix='/buy_sell')


# Error handling
@app.errorhandler(404)
def not_found(error):
    return "This page was not found.", 404


# Example home route
@app.route('/')
def index():
    return render_template('index.html')





# Load the contract

# Main entry point
if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')








from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User

# Create a Blueprint for authentication
auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember', False))
            return redirect(url_for('nft.list_nfts'))  # Redirect to the profile page after login
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))  # If the user doesn't exist or password is wrong, reload the page

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        public_address = request.form.get('public address')
        private_address = request.form.get('private address')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        new_user = User(email=email,name=name,eth_public_address=public_address,
                        eth_private_address=private_address,
                        password=generate_password_hash(password, method='pbkdf2:sha256'))

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')
# @auth.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # Redirect to the login page after logout

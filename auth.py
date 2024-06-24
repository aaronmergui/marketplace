from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a Blueprint for authentication
auth = Blueprint('auth', __name__)
MAX_ATTEMPTS = 10
BLOCK_DURATION = timedelta(hours=1)
CONFIRMATION_ATTEMPTS = 10
CONFIRMATION_BLOCK_DURATION = timedelta(seconds=30)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'attempts' not in session:
        session['attempts'] = 0
        session['last_attempt_time'] = datetime.min.replace(tzinfo=timezone.utc)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user is blocked
        if session['attempts'] >= MAX_ATTEMPTS:
            last_attempt_time = session['last_attempt_time']
            if datetime.now(timezone.utc) - last_attempt_time < BLOCK_DURATION:
                flash('Too many login attempts. Please try again later.')
                return redirect(url_for('auth.login'))
            else:
                # Reset attempts after block duration has passed
                session['attempts'] = 0

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember', False))
            session['attempts'] = 0  # Reset attempts on successful login
            return redirect(url_for('nft.list_nfts'))
        else:
            session['attempts'] += 1
            session['last_attempt_time'] = datetime.now(timezone.utc)
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

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
        new_user = User(email=email, name=name, eth_public_address=public_address,
                        eth_private_address=private_address,
                        password=generate_password_hash(password, method='pbkdf2:sha256'))

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # Redirect to the login page after logout

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            session['confirmation_code'] = random.randint(100000, 999999)
            session['confirmation_attempts'] = 0
            session['last_confirmation_time'] = datetime.min.replace(tzinfo=timezone.utc)
            session['reset_email'] = email  # Save the email in session
            send_confirmation_email(email, session['confirmation_code'])
            return redirect(url_for('auth.confirm_code'))
        else:
            flash('Email is not registered.')
            return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

@auth.route('/confirm_code', methods=['GET', 'POST'])
def confirm_code():
    if 'confirmation_attempts' not in session:
        session['confirmation_attempts'] = 0
        session['last_confirmation_time'] = datetime.min.replace(tzinfo=timezone.utc)

    if request.method == 'POST':
        code = request.form.get('code')

        if session['confirmation_attempts'] >= CONFIRMATION_ATTEMPTS:
            last_confirmation_time = session['last_confirmation_time']
            if datetime.now(timezone.utc) - last_confirmation_time < CONFIRMATION_BLOCK_DURATION:
                flash('Too many attempts. Please try again later.')
                return redirect(url_for('auth.confirm_code'))
            else:
                session['confirmation_attempts'] = 0

        if code == str(session['confirmation_code']):
            return redirect(url_for('auth.reset_password'))
        else:
            session['confirmation_attempts'] += 1
            session['last_confirmation_time'] = datetime.now(timezone.utc)
            flash('Incorrect code. Please try again.')
            return redirect(url_for('auth.confirm_code'))

    return render_template('confirm_code.html')

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('auth.reset_password'))

        email = session.get('reset_email')
        if email:
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Password has been reset successfully.')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html')

def send_confirmation_email(email, code):
    sender_email = 'sneakchain4@gmail.com'
    app_password = 'naaq eqiu kpcq lgvj'
    receiver_email = email  # Send email to the user who requested password reset
    subject = 'Password Reset Confirmation Code'
    body = f"Subject: Password Reset Confirmation Code\n\nYour confirmation code is {code}."
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.sendmail(sender_email, receiver_email, msg.as_string())

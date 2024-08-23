from flask import current_app as app
from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user
from random import randint
from .forms import LoginForm, SignupForm, ResetPasswordRequestForm, ResetPasswordForm
from . import db
from .models import User

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data
        user = None

        if email:
            user = User.query.filter_by(email=email).first()
        elif phone_number:
            user = User.query.filter_by(phone_number=phone_number).first()

        if user and user.check_password(password):
            if user.confirmed:
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Account not confirmed. Check your email/SMS for the confirmation code.', 'warning')
        else:
            flash('Invalid email/phone number or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data

        if email and User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        elif phone_number and User.query.filter_by(phone_number=phone_number).first():
            flash('Phone number already registered', 'danger')
        else:
            user = User(email=email, phone_number=phone_number)
            user.set_password(password)
            user.confirmation_code = str(randint(100000, 999999))

            db.session.add(user)
            db.session.commit()

            try:
                user.send_confirmation_code()
                flash('User registered, please verify your account', 'success')
            except Exception as e:
                flash(f'Error sending confirmation code: {e}', 'danger')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        phone_number = form.phone_number.data

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif phone_number:
            user = User.query.filter_by(phone_number=phone_number).first()

        if user:
            reset_token = user.generate_reset_token()
            try:
                if email:
                    # Send email with reset token
                    user._send_email()  # Replace with actual email sending logic to include reset_token
                elif phone_number:
                    # Send SMS with reset token
                    user._send_sms()  # Replace with actual SMS sending logic to include reset_token
                flash('Password reset request processed, check your email or SMS for reset instructions', 'success')
            except Exception as e:
                flash(f'Error sending reset instructions: {e}', 'danger')
        else:
            flash('User not found', 'danger')
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        reset_token = form.reset_token.data
        new_password = form.new_password.data

        user = User.verify_reset_token(reset_token)
        if not user:
            flash('Invalid or expired reset token', 'danger')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password has been reset', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

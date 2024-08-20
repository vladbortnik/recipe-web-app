from flask import Blueprint, request, jsonify
from random import randint
from .models import User
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')

    if email and User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    if phone_number and User.query.filter_by(phone_number=phone_number).first():
        return jsonify({'message': 'Phone number already registered'}), 400

    user = User(email=email, phone_number=phone_number)
    user.set_password(password)
    user.confirmation_code = str(randint(100000, 999999))

    db.session.add(user)
    db.session.commit()

    # Send confirmation code via email or SMS
    user.send_confirmation_code()

    return jsonify({'message': 'User registered, please verify your account'}), 201

@auth_bp.route('/confirm', methods=['POST'])
def confirm_registration():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phone_number')
    confirmation_code = data.get('confirmation_code')

    user = None
    if email:
        user = User.query.filter_by(email=email, confirmation_code=confirmation_code).first()
    elif phone_number:
        user = User.query.filter_by(phone_number=phone_number, confirmation_code=confirmation_code).first()

    if not user:
        return jsonify({'message': 'Invalid confirmation code'}), 400

    user.confirmed = True
    db.session.commit()

    return jsonify({'message': 'Account confirmed'}), 200

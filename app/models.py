# from datetime import datetime, timezone
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask import current_app
from flask_login import UserMixin
# from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), unique=True, nullable=False)
    # phone_number = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(256), nullable=False)
    # confirmed = db.Column(db.Boolean, default=False)
    # confirmation_code = db.Column(db.String(6), nullable=True)
    # created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.email}>'

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    # def generate_confirmation_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': self.id}).decode('utf-8')

    # def confirm(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except Exception as e:
    #         print(f"Confirmation error: {e}")
    #         return False
    #     if data.get('confirm') != self.id:
    #         return False
    #     self.confirmed = True
    #     db.session.add(self)
    #     db.session.commit()
    #     return True

    # def send_confirmation_code(self):
    #     # Dummy function for sending an email/SMS
    #     try:
    #         if self.email:
    #             self._send_email()
    #         elif self.phone_number:
    #             self._send_sms()
    #     except Exception as e:
    #         print(f"Error sending confirmation code: {e}")

    # def _send_email(self):
    #     # Implement sending email using SendGrid or another email service
    #     print(f"Sending confirmation email to {self.email}")
    #     # Replace with actual email sending logic

    # def _send_sms(self):
    #     # Implement sending SMS using Twilio or another SMS service
    #     print(f"Sending confirmation SMS to {self.phone_number}")
    #     # Replace with actual SMS sending logic

    # def generate_reset_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'reset': self.id}).decode('utf-8')

    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token.encode('utf-8'))
    #     except Exception as e:
    #         print(f"Reset token error: {e}")
    #         return None
    #     return User.query.get(data['reset'])

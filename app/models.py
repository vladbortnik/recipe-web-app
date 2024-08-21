from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import random

# from .extensions import db
from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    confirmation_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def send_confirmation_code(self):
        # Dummy function for sending an email/SMS
        if self.email:
            self._send_email()
        elif self.phone_number:
            self._send_sms()

    def _send_email(self):
        # Realistically send an email (implement using an email provider like SMTP, SendGrid, etc.)
        from smtplib import SMTP
        import os

        server = SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
        message = f'Your confirmation code is: {self.confirmation_code}'
        server.sendmail(os.getenv('SMTP_FROM'), self.email, message)
        server.quit()
        print(f'Sent email confirmation code to {self.email}')

    def _send_sms(self):
        # Realistically send an SMS (implement using an SMS provider like Twilio)
        from twilio.rest import Client
        import os

        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        message = client.messages.create(
            body=f'Your confirmation code is: {self.confirmation_code}',
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=self.phone_number
        )
        print(f'Sent SMS confirmation code to {self.phone_number}')
  
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None
        return User.query.get(data['reset'])

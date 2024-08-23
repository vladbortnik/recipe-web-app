from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number: ', validators=[Length(min=10, max=15)])
    password = PasswordField('Password: ', validators=[DataRequired(), Length(min=6, max=29)])
    confirm_password = PasswordField('Confirm Password: ', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number: ', validators=[Length(min=10, max=15)])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    reset_token = StringField('Reset Token', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')

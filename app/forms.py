from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(message='Email address is required'), 
                                         Email(message='Please enter a valid email address')])
    password = PasswordField('Password:', validators=[DataRequired(message='Password is required')])
    remember = BooleanField('Remember me')
    submit = SubmitField('LogIn')

class SignupForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(message='Email address is required'), 
                                         Email(message='Please enter a valid email address')])
    password = PasswordField('Password:', validators=[DataRequired(message='Password is required'), 
                                              Length(min=8, max=29, message='Password must be between 8 and 29 characters')])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(message='Please confirm your password'), 
                                                             EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class UploadImageForm(FlaskForm):
    images = MultipleFileField('Upload Images:', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), 
                                                        DataRequired(message='Please select at least one image')])
    submit = SubmitField('Upload')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=29, message='Password must be between 8 and 29 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

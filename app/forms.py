from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('LogIn')

class SignupForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=29)])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class UploadImageForm(FlaskForm):
    images = MultipleFileField('Upload Images:', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), DataRequired()])
    submit = SubmitField('Upload')

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    # phone = StringField('Phone number:', validators=[DataRequired(), Length(min=10, max=15)]) 
    password = PasswordField('Password:', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('LogIn')

class SignupForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    # phone_number = StringField('Phone Number: ', validators=[Length(min=10, max=15)])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=29)])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# forms.py (additions)

class UploadImageForm(FlaskForm):
    images = MultipleFileField('Upload Images:', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), DataRequired()])
    submit = SubmitField('Upload')




# class ResetPasswordRequestForm(FlaskForm):
#     email = StringField('Email: ', validators=[DataRequired(), Email()])
#     phone_number = StringField('Phone Number: ', validators=[Length(min=10, max=15)])
#     submit = SubmitField('Send Reset Link')

# class ResetPasswordForm(FlaskForm):
#     reset_token = StringField('Reset Token', validators=[DataRequired()])
#     new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
#     confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
#     submit = SubmitField('Reset Password')

# class ImageUploadForm(FlaskForm):
    # title = StringField('Book Title:', validators=[DataRequired()])
    # department = StringField('Department:', validators=[DataRequired()])
    # content = TextAreaField('Author Name & Edition:', validators=[DataRequired()])
    # image = FileField('Upload Image:', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    # image = FileField('Upload Image:', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    # image = FileField('Upload Image:', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    # submit = SubmitField('Post')
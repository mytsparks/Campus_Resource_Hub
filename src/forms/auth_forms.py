from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    name = StringField(
        'Full Name',
        validators=[DataRequired(message='Name is required.'), Length(max=120)],
    )
    email = StringField(
        'University Email',
        validators=[DataRequired(message='Email is required.'), Email()],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.'),
        ],
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.'),
        ],
    )
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('staff', 'Staff')],
        validators=[DataRequired(message='Role selection is required.')],
    )
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    identifier = StringField(
        'Email or Username',
        validators=[DataRequired(message='Please enter your email or username.')],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')],
    )
    submit = SubmitField('Log In')


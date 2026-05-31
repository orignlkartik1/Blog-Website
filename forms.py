from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Username must be between 3 and 100 characters')
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
        Regexp(r'(?=.*[A-Za-z])(?=.*\d)', 
               message='Password must contain both letters and numbers')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=120, message='Title must be between 3 and 120 characters')
    ])
    content = TextAreaField('Content', validators=[
        DataRequired(),
        Length(min=10, message='Content must be at least 10 characters')
    ])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[
        DataRequired(),
        Length(min=1, max=1000, message='Comment must be between 1 and 1000 characters')
    ])
    submit = SubmitField('Add Comment')

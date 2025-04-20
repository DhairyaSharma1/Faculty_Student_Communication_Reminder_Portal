from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_teacher = BooleanField('Register as Teacher')
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class TeacherProfileForm(FlaskForm):
    """Form for teacher profile details"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    subject = StringField('Subject', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class StudentProfileForm(FlaskForm):
    """Form for student profile details"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    section = StringField('Section', validators=[DataRequired()])
    roll_number = StringField('Roll Number')
    submit = SubmitField('Save Profile')

class AssignmentForm(FlaskForm):
    """Form for creating/editing assignments"""
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Save Assignment')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class DiscussionPostForm(FlaskForm):
    content = TextAreaField('Your Post', validators=[DataRequired()])
    submit = SubmitField('Post')
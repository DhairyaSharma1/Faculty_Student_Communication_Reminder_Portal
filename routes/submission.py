from flask import render_template, redirect, url_for, abort, request, flash
from models import Submission
from routes import submission_bp

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField, FloatField
from wtforms.validators import DataRequired, Optional, NumberRange

class SubmissionForm(FlaskForm):
    content = TextAreaField('Your Answer', validators=[Optional()])
    file = FileField('Upload File', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg'], 
                   'Allowed file types: PDF, Word, Text, ZIP, Images')
    ])
    link = TextAreaField('Or paste a link', validators=[Optional()])
    submit = SubmitField('Submit Assignment')

class GradeSubmissionForm(FlaskForm):
    grade = FloatField('Grade', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='Grade must be between 0 and 100')
    ])
    feedback = TextAreaField('Feedback', validators=[Optional()])
    submit = SubmitField('Submit Grade')
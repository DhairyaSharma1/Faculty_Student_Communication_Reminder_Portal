from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Base user model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Increased from 128 to 256
    is_teacher = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Generate a password hash using scrypt (longer but more secure)"""
        self.password_hash = generate_password_hash(
            password,
            method='scrypt', 
            salt_length=16
        )
        
    def check_password(self, password):
        """Check if the password is correct"""
        return check_password_hash(self.password_hash, password)

class Teacher(db.Model):
    """Teacher model extending User"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('teacher', uselist=False))
    
    # Relationship with Assignment model
    assignments = db.relationship('Assignment', backref='teacher', lazy='dynamic')

class Student(db.Model):
    """Student model extending User"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(20), nullable=False)
    roll_number = db.Column(db.String(20))
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('student', uselist=False))

class Assignment(db.Model):
    """Assignment model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    section = db.Column(db.String(20), nullable=False)  # To filter assignments by section
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    submissions = db.relationship('Submission', backref='assignment', lazy=True, cascade='all, delete-orphan')

    """Assignment model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    section = db.Column(db.String(20), nullable=False)  # To filter assignments by section
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    
    # Use a consistent backref name

# models.py (update the Message model)
class Message(db.Model):
    """Enhanced message model with read receipts"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)  # Only keep this one

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
class DiscussionThread(db.Model):
    """Forum discussion threads"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    section = db.Column(db.String(20), nullable=False)  # For section-specific forums
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='threads')
    posts = db.relationship('DiscussionPost', backref='thread', lazy='dynamic', cascade='all, delete-orphan')

class DiscussionPost(db.Model):
    """Posts in discussion threads"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    thread_id = db.Column(db.Integer, db.ForeignKey('discussion_thread.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    author = db.relationship('User', backref='posts')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_time = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    is_late = db.Column(db.Boolean, default=False)
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Submitted')

    # Simplified relationship definitions with unique backref names
    # No need to repeat backref in the assignment relationship as it's defined in Assignment class
    student = db.relationship('User', backref='submissions')

    def __repr__(self):
        return f"<Submission {self.id} for Assignment {self.assignment_id}>"
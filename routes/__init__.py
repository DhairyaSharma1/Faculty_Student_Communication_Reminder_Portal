from flask import Blueprint

# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
student_bp = Blueprint('student', __name__, url_prefix='/student')

# Import routes to register with blueprints
from routes import auth, teacher, student
from flask import Blueprint

# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
student_bp = Blueprint('student', __name__, url_prefix='/student')
submission_bp = Blueprint('submission', __name__, url_prefix='/submission')
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

from routes import auth, teacher, student, submission, chat


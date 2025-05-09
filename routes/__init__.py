from flask import Blueprint

# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
student_bp = Blueprint('student', __name__, url_prefix='/student')
submission_bp = Blueprint('submission', __name__, url_prefix='/submission')
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Import routes to register with blueprints
<<<<<<< HEAD
from routes import auth, teacher, student, submission, chat
=======
from routes import auth, teacher, student, submission, chat
>>>>>>> c2dd40ed88365091e1bc6fe343935fa31fd2ccf9

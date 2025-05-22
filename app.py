from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from routes import auth_bp, teacher_bp, student_bp, chat_bp
import os

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ===== Database Initialization =====
    db.init_app(app)
    
    # ===== Security Extensions =====
    csrf = CSRFProtect(app)
    
    # ===== Flask-Login Setup =====
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ===== Database Migrations =====
    migrate = Migrate(app, db)
    
    # ===== Blueprint Registration =====
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(chat_bp)

    # ===== Root Route =====
    @app.route('/')
    def index():
        """Redirect to the login page"""
        return redirect(url_for('auth.login'))
    
    # ===== Database Table Creation =====
    with app.app_context():
        if os.environ.get('FLASK_ENV') == 'development':
            db.create_all()  # Only for development (Render uses migrations)
    
    return app

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from routes import auth_bp, teacher_bp, student_bp, chat_bp

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app) 
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(chat_bp)

    # Root route
    @app.route('/')
    def index():
        """Redirect to the login page"""
        return redirect(url_for('auth.login'))
    
    with app.app_context():
        db.create_all()
    
    return app

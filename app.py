from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from routes import auth_bp, teacher_bp, student_bp, chat_bp
import os
from pathlib import Path

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Database migrations
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(chat_bp)

    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # Initialize database and folders
    with app.app_context():
        try:
            # Create required directories
            instance_path = Path(app.instance_path)
            instance_path.mkdir(exist_ok=True)
            (instance_path / 'uploads').mkdir(exist_ok=True)
            
            # Create tables
            db.create_all()
        except Exception as e:
            app.logger.error(f"Initialization error: {str(e)}")
    
    return app

# Required for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run()

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    
    # Database Configuration
    if os.environ.get('RENDER'):
        # Render-specific SQLite path
        SQLALCHEMY_DATABASE_URI = 'sqlite:////opt/render/project/src/instance/classroom_db.sqlite?check_same_thread=False'
    else:
        # Local development path
        instance_path = Path(__file__).parent / 'instance'
        instance_path.mkdir(exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{instance_path}/classroom_db.sqlite?check_same_thread=False'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'timeout': 30}  # Increased timeout for Render
    }

    # Session Security
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # Environment
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')

    # Security Headers
    CSP = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
    }

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # File Uploads
    if os.environ.get('RENDER'):
        UPLOAD_FOLDER = '/opt/render/project/src/instance/uploads'
    else:
        UPLOAD_FOLDER = str(Path(__file__).parent / 'instance' / 'uploads')
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Production Settings
    if os.environ.get('RENDER'):
        SESSION_COOKIE_SECURE = True
        PREFERRED_URL_SCHEME = 'https'

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    
    # ✅ SQLite configuration for local and Render deployment
    SQLALCHEMY_DATABASE_URI = 'sqlite:///classroom_db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # App environment and debug
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')

    # Content Security Policy (CSP) for improved security
    CSP = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
    }

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # File upload config
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

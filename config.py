import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes session timeout

    # Database Configuration (using environment variables)
    DB_USER = os.environ.get('DB_USER', 'classroom_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '12Dhairya12@')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'classroom_db')
    
    # URL-encode password for special characters
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://classroom_user:password123@localhost/classroom_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,  # Recycle connections after 5 minutes
        'pool_pre_ping': True  # Test connections for health
    }

    # Application Settings
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
    
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
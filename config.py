import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # ===== Security =====
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    # ===== Database Configuration =====
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/classroom_db.sqlite'  # Force SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===== Session Security =====
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # ===== Environment =====
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')

    # ===== Security Headers =====
    CSP = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
    }

    # ===== Rate Limiting =====
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    # ===== File Uploads =====
    UPLOAD_FOLDER = os.path.join('instance', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ===== Render-Specific Optimizations =====
    if os.environ.get('RENDER', None):
        # Production-specific settings (without PostgreSQL enforcement)
        SESSION_COOKIE_SECURE = True
        PREFERRED_URL_SCHEME = 'https'

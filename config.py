import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_SECURE_DEFAULT_KEY_FOR_DEV'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PostgreSQL connection pool settings (for production)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Verify connections before using
        'max_overflow': 20,  # Allow up to 20 additional connections
    }
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Pagination
    RESOURCES_PER_PAGE = 12
    
    # LLM Configuration (Google Gemini - Default)
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'gemini')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gemini-2.0-flash')  # Latest stable Gemini model
    # IMPORTANT: Never hardcode API keys. Set via environment variables (.env or platform env)
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')


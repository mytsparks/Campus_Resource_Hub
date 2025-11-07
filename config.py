import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_SECURE_DEFAULT_KEY_FOR_DEV'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Pagination
    RESOURCES_PER_PAGE = 12
    
    # LLM Configuration (Google Gemini - Default)
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'gemini')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'gemini-2.0-flash')  # Latest stable Gemini model
    LLM_API_KEY = os.environ.get('LLM_API_KEY', 'AIzaSyAXgN9mtjViENMwG92Ymbb749wt4Ip3bLs')
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')


"""Flask extensions module to avoid circular imports."""
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# SQLAlchemy instance - engine_options will be read from app config
# if SQLALCHEMY_ENGINE_OPTIONS is set in the Flask app config
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()


from __future__ import annotations

from flask import Flask

from config import Config
from src.controllers.admin_routes import admin_bp
from src.controllers.auth_routes import auth_bp
from src.controllers.booking_routes import booking_bp
from src.controllers.message_routes import message_bp
from src.controllers.resource_routes import resource_bp
from src.controllers.review_routes import review_bp
from src.controllers.summary_routes import summary_bp
from src.data_access.user_dal import UserDAL
from src.extensions import bcrypt, csrf, db, login_manager
from src.models import Base, User, init_db


def _seed_initial_admin() -> None:
    """Ensure an initial admin user exists for application access."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=db.engine)
    session = Session()
    try:
        dal = UserDAL(session)
        admin_email = 'admin@campushub.local'
        existing_admin = dal.get_user_by_email(admin_email) or dal.get_user_by_name('admin')
        if existing_admin:
            return

        dal.create_user(
            name='admin',
            email=admin_email,
            plaintext_password='Password1',
            role='admin',
        )
    finally:
        session.close()


def create_app(config_class: type[Config] = Config) -> Flask:
    """Initializes and configures the Flask application."""

    app = Flask(__name__, template_folder='src/views', static_folder='src/static')
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Session factory will be created when needed within app context

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            return None

        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            # Use session.get() which is simpler for primary key lookups
            return session.get(User, user_id_int)
        finally:
            session.close()

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resource_bp, url_prefix='/resources')
    app.register_blueprint(booking_bp, url_prefix='/bookings')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(review_bp, url_prefix='/reviews')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(summary_bp, url_prefix='/summaries')

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('resources.list_resources'))

    @app.context_processor
    def inject_unread_count():
        """Inject unread message count into all templates."""
        from flask_login import current_user
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        unread_count = 0
        if current_user.is_authenticated:
            try:
                Session = sessionmaker(bind=db.engine)
                session = Session()
                try:
                    # Count messages received by current user (simplified - no read status in current schema)
                    result = session.execute(
                        text("SELECT COUNT(*) FROM messages WHERE receiver_id = :user_id"),
                        {"user_id": current_user.user_id}
                    )
                    unread_count = result.scalar() or 0
                finally:
                    session.close()
            except Exception:
                # If there's any error, default to 0
                unread_count = 0
        
        return dict(unread_message_count=unread_count)

    with app.app_context():
        init_db(db.engine)
        _seed_initial_admin()

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)


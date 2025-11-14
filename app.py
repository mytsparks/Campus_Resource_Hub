from __future__ import annotations

from flask import Flask
from dotenv import load_dotenv

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

    # Load environment variables from .env if present (local dev)
    try:
        load_dotenv()
    except Exception:
        pass

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
    def inject_notifications():
        """Inject notification data into all templates."""
        from flask_login import current_user
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        from datetime import datetime, timedelta
        
        notifications = []
        unread_count = 0
        
        if current_user.is_authenticated:
            try:
                Session = sessionmaker(bind=db.engine)
                session = Session()
                try:
                    user_id = current_user.user_id
                    
                    # Get recent messages (last 7 days)
                    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                    messages_result = session.execute(
                        text("""
                            SELECT m.message_id, m.thread_id, m.sender_id, m.receiver_id, 
                                   m.content, m.timestamp, 
                                   u.name as sender_name
                            FROM messages m
                            LEFT JOIN users u ON m.sender_id = u.user_id
                            WHERE m.receiver_id = :user_id AND m.timestamp >= :week_ago
                            ORDER BY m.timestamp DESC
                            LIMIT 10
                        """),
                        {"user_id": user_id, "week_ago": week_ago}
                    )
                    
                    # Get pending booking approvals (for resource owners)
                    pending_bookings_result = session.execute(
                        text("""
                            SELECT b.*, r.title as resource_title, u.name as requester_name
                            FROM bookings b
                            JOIN resources r ON b.resource_id = r.resource_id
                            JOIN users u ON b.requester_id = u.user_id
                            WHERE r.owner_id = :user_id AND b.status = 'pending'
                            ORDER BY b.created_at DESC
                            LIMIT 5
                        """),
                        {"user_id": user_id}
                    )
                    
                    # Get booking status updates (approved/rejected)
                    booking_updates_result = session.execute(
                        text("""
                            SELECT b.*, r.title as resource_title
                            FROM bookings b
                            JOIN resources r ON b.resource_id = r.resource_id
                            WHERE b.requester_id = :user_id 
                            AND b.status IN ('approved', 'rejected')
                            AND b.updated_at >= :week_ago
                            ORDER BY b.updated_at DESC
                            LIMIT 5
                        """),
                        {"user_id": user_id, "week_ago": week_ago}
                    )
                    
                    from flask import url_for
                    
                    # Process messages
                    for row in messages_result:
                        # Get message preview (first 50 chars)
                        message_preview = row.content[:50] + '...' if row.content and len(row.content) > 50 else (row.content or 'New message')
                        # Format timestamp
                        timestamp_formatted = row.timestamp.strftime('%b %d, %Y %I:%M %p') if row.timestamp and isinstance(row.timestamp, datetime) else (str(row.timestamp) if row.timestamp else 'N/A')
                        notifications.append({
                            'type': 'message',
                            'title': f'New message from {row.sender_name or "User"}',
                            'message': message_preview,
                            'timestamp': row.timestamp,
                            'timestamp_formatted': timestamp_formatted,
                            'link': url_for('messages.view_thread', thread_id=row.thread_id) if row.thread_id else url_for('messages.inbox')
                        })
                    
                    # Process pending bookings (for owners)
                    for row in pending_bookings_result:
                        timestamp_formatted = row.created_at.strftime('%b %d, %Y %I:%M %p') if row.created_at and isinstance(row.created_at, datetime) else (str(row.created_at) if row.created_at else 'N/A')
                        notifications.append({
                            'type': 'booking_request',
                            'title': f'Booking request from {row.requester_name}',
                            'message': f'{row.resource_title} - Pending approval',
                            'timestamp': row.created_at,
                            'timestamp_formatted': timestamp_formatted,
                            'link': url_for('bookings.my_bookings')
                        })
                    
                    # Process booking updates
                    for row in booking_updates_result:
                        status_text = 'approved' if row.status == 'approved' else 'rejected'
                        timestamp_formatted = row.updated_at.strftime('%b %d, %Y %I:%M %p') if row.updated_at and isinstance(row.updated_at, datetime) else (str(row.updated_at) if row.updated_at else 'N/A')
                        notifications.append({
                            'type': 'booking_update',
                            'title': f'Booking {status_text}',
                            'message': f'{row.resource_title} - Your booking was {status_text}',
                            'timestamp': row.updated_at,
                            'timestamp_formatted': timestamp_formatted,
                            'link': url_for('bookings.my_bookings')
                        })
                    
                    # Sort by timestamp (most recent first)
                    notifications.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.min, reverse=True)
                    notifications = notifications[:10]  # Limit to 10 most recent
                    
                    # Count unread (all notifications are considered unread for now)
                    unread_count = len(notifications)
                    
                finally:
                    session.close()
            except Exception as e:
                print(f"Error loading notifications: {e}")
                unread_count = 0
        
        return dict(
            notifications=notifications,
            unread_message_count=unread_count,
            unread_notification_count=unread_count
        )

    with app.app_context():
        init_db(db.engine)
        _seed_initial_admin()

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)


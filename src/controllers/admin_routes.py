from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.user_dal import UserDAL

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('resources.list_resources'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics and approval queue."""
    with get_db_session() as session:
        # Get statistics
        from sqlalchemy import text
        
        stats = {}
        
        # Pending bookings
        result = session.execute(text("SELECT COUNT(*) FROM bookings WHERE status = 'pending'"))
        stats['pending_bookings'] = result.scalar() or 0
        
        # Total users
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        stats['total_users'] = result.scalar() or 0
        
        # Published resources
        result = session.execute(text("SELECT COUNT(*) FROM resources WHERE status = 'published'"))
        stats['published_resources'] = result.scalar() or 0
        
        # Pending reviews (for moderation)
        result = session.execute(text("SELECT COUNT(*) FROM reviews"))
        stats['total_reviews'] = result.scalar() or 0
        
        # Get pending bookings for approval queue
        booking_dal = BookingDAL(session)
        pending_bookings_result = session.execute(
            text("""
                SELECT b.*, r.title, r.location, u.name as requester_name
                FROM bookings b
                JOIN resources r ON b.resource_id = r.resource_id
                JOIN users u ON b.requester_id = u.user_id
                WHERE b.status = 'pending'
                ORDER BY b.created_at DESC
                LIMIT 10
            """)
        )
        pending_bookings = [dict(row._mapping) for row in pending_bookings_result]

    return render_template('admin/dashboard.html', stats=stats, pending_bookings=pending_bookings)


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users (view, suspend, etc.)."""
    with get_db_session() as session:
        from sqlalchemy import text
        result = session.execute(
            text("SELECT * FROM users ORDER BY created_at DESC")
        )
        users = []
        for row in result:
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[4],
                'created_at': row[7],
            })

    return render_template('admin/users.html', users=users)


@admin_bp.route('/resources')
@login_required
@admin_required
def manage_resources():
    """Manage all resources."""
    with get_db_session() as session:
        resource_dal = ResourceDAL(session)
        # Get all resources regardless of status
        from sqlalchemy import text
        result = session.execute(
            text("SELECT * FROM resources ORDER BY created_at DESC")
        )
        resources = []
        for row in result:
            resources.append({
                'resource_id': row[0],
                'title': row[2],
                'status': row[9],
                'created_at': row[10],
            })

    return render_template('admin/resources.html', resources=resources)


@admin_bp.route('/reviews')
@login_required
@admin_required
def moderate_reviews():
    """Moderate reviews (hide inappropriate content)."""
    with get_db_session() as session:
        review_dal = ReviewDAL(session)
        from sqlalchemy import text
        result = session.execute(
            text("""
                SELECT r.*, res.title as resource_title, u.name as reviewer_name
                FROM reviews r
                JOIN resources res ON r.resource_id = res.resource_id
                JOIN users u ON r.reviewer_id = u.user_id
                ORDER BY r.timestamp DESC
            """)
        )
        reviews = [dict(row._mapping) for row in result]

    return render_template('admin/reviews.html', reviews=reviews)


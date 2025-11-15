from datetime import datetime

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
        pending_bookings = []
        for row in pending_bookings_result:
            booking_dict = dict(row._mapping)
            # Convert datetime strings to datetime objects
            if isinstance(booking_dict.get('start_datetime'), str):
                try:
                    booking_dict['start_datetime'] = datetime.fromisoformat(booking_dict['start_datetime'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        booking_dict['start_datetime'] = datetime.strptime(booking_dict['start_datetime'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        booking_dict['start_datetime'] = None
            
            if isinstance(booking_dict.get('end_datetime'), str):
                try:
                    booking_dict['end_datetime'] = datetime.fromisoformat(booking_dict['end_datetime'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        booking_dict['end_datetime'] = datetime.strptime(booking_dict['end_datetime'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        booking_dict['end_datetime'] = None
            
            if isinstance(booking_dict.get('created_at'), str):
                try:
                    booking_dict['created_at'] = datetime.fromisoformat(booking_dict['created_at'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        booking_dict['created_at'] = datetime.strptime(booking_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        booking_dict['created_at'] = None
            
            pending_bookings.append(booking_dict)

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
            created_at = row[7]
            # Convert datetime string to datetime object if needed
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        created_at = None
            
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[4],
                'created_at': created_at,
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
            created_at = row[10]
            # Convert datetime string to datetime object if needed
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        created_at = None
            
            resources.append({
                'resource_id': row[0],
                'title': row[2],
                'status': row[9],
                'created_at': created_at,
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
        reviews = []
        for row in result:
            review_dict = dict(row._mapping)
            # Convert datetime string to datetime object if needed
            if isinstance(review_dict.get('timestamp'), str):
                try:
                    review_dict['timestamp'] = datetime.fromisoformat(review_dict['timestamp'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        review_dict['timestamp'] = datetime.strptime(review_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        review_dict['timestamp'] = None
            
            reviews.append(review_dict)

    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_review(review_id: int):
    """Edit a review (admin only)."""
    with get_db_session() as session:
        review_dal = ReviewDAL(session)
        review = review_dal.get_review_by_id(review_id)
        
        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('admin.moderate_reviews'))
        
        if request.method == 'POST':
            # Validate CSRF token
            from flask_wtf.csrf import validate_csrf
            try:
                validate_csrf(request.form.get('csrf_token'))
            except Exception:
                flash('Invalid security token. Please try again.', 'error')
                return redirect(url_for('admin.moderate_reviews'))
            
            rating = request.form.get('rating', type=int)
            comment = request.form.get('comment', '').strip()
            
            updated_review = review_dal.update_review(
                review_id=review_id,
                rating=rating,
                comment=comment if comment else None
            )
            
            if updated_review:
                flash('Review updated successfully.', 'success')
            else:
                flash('Failed to update review.', 'error')
            
            return redirect(url_for('admin.moderate_reviews'))
        
        # Get resource and reviewer info for display
        from sqlalchemy import text
        result = session.execute(
            text("""
                SELECT r.*, res.title as resource_title, u.name as reviewer_name
                FROM reviews r
                JOIN resources res ON r.resource_id = res.resource_id
                JOIN users u ON r.reviewer_id = u.user_id
                WHERE r.review_id = :review_id
            """),
            {"review_id": review_id}
        )
        row = result.fetchone()
        review_data = dict(row._mapping) if row else None
    
    return render_template('admin/edit_review.html', review=review_data)


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id: int):
    """Delete a review (admin only)."""
    # Validate CSRF token
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('admin.moderate_reviews'))
    
    with get_db_session() as session:
        review_dal = ReviewDAL(session)
        success = review_dal.delete_review(review_id)
        
        if success:
            flash('Review deleted successfully.', 'success')
        else:
            flash('Failed to delete review.', 'error')
    
    return redirect(url_for('admin.moderate_reviews'))
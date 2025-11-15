"""User dashboard routes for students and staff."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.booking_dal import BookingDAL
from src.data_access.review_dal import ReviewDAL
from src.data_access.resource_dal import ResourceDAL

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    """User dashboard - different views for students vs staff."""
    with get_db_session() as session:
        # Get user's bookings
        booking_dal = BookingDAL(session)
        from sqlalchemy import text
        bookings_result = session.execute(
            text("""
                SELECT b.*, r.title, r.location, r.resource_id
                FROM bookings b
                JOIN resources r ON b.resource_id = r.resource_id
                WHERE b.requester_id = :user_id
                ORDER BY b.start_datetime DESC
                LIMIT 20
            """),
            {"user_id": current_user.user_id}
        )
        bookings = []
        for row in bookings_result:
            booking_dict = dict(row._mapping)
            # Convert datetime strings to datetime objects if needed
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
            
            bookings.append(booking_dict)
        
        # Get user's reviews
        review_dal = ReviewDAL(session)
        reviews_result = session.execute(
            text("""
                SELECT r.*, res.title as resource_title, res.resource_id
                FROM reviews r
                JOIN resources res ON r.resource_id = res.resource_id
                WHERE r.reviewer_id = :user_id
                ORDER BY r.timestamp DESC
            """),
            {"user_id": current_user.user_id}
        )
        reviews = []
        for row in reviews_result:
            review_dict = dict(row._mapping)
            if isinstance(review_dict.get('timestamp'), str):
                try:
                    review_dict['timestamp'] = datetime.fromisoformat(review_dict['timestamp'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        review_dict['timestamp'] = datetime.strptime(review_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, AttributeError):
                        review_dict['timestamp'] = None
            reviews.append(review_dict)
        
        # For staff, also get their resources
        my_resources = []
        if current_user.role in ('staff', 'admin'):
            resource_dal = ResourceDAL(session)
            resources_result = session.execute(
                text("""
                    SELECT * FROM resources
                    WHERE owner_id = :owner_id
                    ORDER BY created_at DESC
                    LIMIT 20
                """),
                {"owner_id": current_user.user_id}
            )
            for row in resources_result:
                resource_dict = dict(row._mapping)
                my_resources.append(resource_dict)
    
    return render_template('user/dashboard.html', 
                         bookings=bookings, 
                         reviews=reviews,
                         my_resources=my_resources if current_user.role in ('staff', 'admin') else None)


@user_bp.route('/reviews/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_my_review(review_id: int):
    """Edit own review (users can only edit their own reviews)."""
    with get_db_session() as session:
        review_dal = ReviewDAL(session)
        review = review_dal.get_review_by_id(review_id)
        
        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        # Check ownership
        if review.reviewer_id != current_user.user_id:
            flash('You can only edit your own reviews.', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        if request.method == 'POST':
            from src.forms.resource_forms import ReviewForm
            form = ReviewForm()
            if form.validate_on_submit():
                updated_review = review_dal.update_review(
                    review_id=review_id,
                    rating=int(form.rating.data),
                    comment=form.comment.data if form.comment.data else None
                )
                
                if updated_review:
                    flash('Review updated successfully.', 'success')
                else:
                    flash('Failed to update review.', 'error')
                
                return redirect(url_for('user.user_dashboard'))
        
        # Get resource info
        from sqlalchemy import text
        result = session.execute(
            text("SELECT title FROM resources WHERE resource_id = :resource_id"),
            {"resource_id": review.resource_id}
        )
        row = result.fetchone()
        resource_title = row[0] if row else 'Unknown Resource'
        
        from src.forms.resource_forms import ReviewForm
        form = ReviewForm()
        form.rating.data = str(review.rating)
        form.comment.data = review.comment
    
    return render_template('user/edit_review.html', form=form, review=review, resource_title=resource_title)


@user_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_my_review(review_id: int):
    """Delete own review (users can only delete their own reviews)."""
    with get_db_session() as session:
        review_dal = ReviewDAL(session)
        review = review_dal.get_review_by_id(review_id)
        
        if not review:
            flash('Review not found.', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        # Check ownership
        if review.reviewer_id != current_user.user_id:
            flash('You can only delete your own reviews.', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        success = review_dal.delete_review(review_id)
        
        if success:
            flash('Review deleted successfully.', 'success')
        else:
            flash('Failed to delete review.', 'error')
    
    return redirect(url_for('user.user_dashboard'))


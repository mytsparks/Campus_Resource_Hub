from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.review_dal import ReviewDAL
from src.data_access.resource_dal import ResourceDAL
from src.forms.resource_forms import ReviewForm

review_bp = Blueprint('reviews', __name__)


@review_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create_review(resource_id: int):
    """Create a review for a resource after booking completion."""
    form = ReviewForm()

    with get_db_session() as session:
        resource_dal = ResourceDAL(session)
        resource = resource_dal.get_resource_by_id(resource_id)

        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('resources.list_resources'))

        # Check if user has completed a booking for this resource
        from sqlalchemy import text
        result = session.execute(
            text("""
                SELECT * FROM bookings
                WHERE resource_id = :resource_id
                AND requester_id = :user_id
                AND status = 'completed'
                LIMIT 1
            """),
            {"resource_id": resource_id, "user_id": current_user.user_id}
        )
        has_completed_booking = result.fetchone() is not None

        if not has_completed_booking:
            flash('You can only review resources you have booked and completed.', 'error')
            return redirect(url_for('resources.resource_detail', resource_id=resource_id))

        if request.method == 'POST' and form.validate_on_submit():
            review_dal = ReviewDAL(session)
            review = review_dal.create_review(
                resource_id=resource_id,
                reviewer_id=current_user.user_id,
                rating=int(form.rating.data),
                comment=form.comment.data,
            )

            if review:
                flash('Review submitted successfully!', 'success')
                return redirect(url_for('resources.resource_detail', resource_id=resource_id))
            else:
                flash('Failed to submit review.', 'error')

    return render_template('reviews/create.html', form=form, resource=resource)


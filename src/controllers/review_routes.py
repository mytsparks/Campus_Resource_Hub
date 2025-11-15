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
    """Create a review for a resource."""
    form = ReviewForm()

    with get_db_session() as session:
        resource_dal = ResourceDAL(session)
        resource = resource_dal.get_resource_by_id(resource_id)

        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('resources.list_resources'))

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
                # Still need to extract resource data for re-rendering
                pass
        
        # Extract resource attributes into a dictionary to avoid DetachedInstanceError
        # This ensures template rendering works after the session closes
        resource_dict = {
            'resource_id': resource.resource_id,
            'title': resource.title,
            'location': resource.location,
            'description': resource.description,
            'category': resource.category,
        }
        
        # Create a simple object for template compatibility
        class ResourceObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        resource_obj = ResourceObj(resource_dict)

    return render_template('reviews/create.html', form=form, resource=resource_obj)


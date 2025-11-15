import os
from werkzeug.utils import secure_filename

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from src.controllers.auth_routes import get_db_session
from src.data_access.resource_dal import ResourceDAL
from src.forms.resource_forms import ResourceForm
from src.models import Resource
from src.utils.storage import save_uploaded_files

resource_bp = Blueprint('resources', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@resource_bp.route('/')
def list_resources():
    search_term = request.args.get('q', '').strip() or None
    category = request.args.get('category', '').strip() or None
    location = request.args.get('location', '').strip() or None
    capacity_str = request.args.get('capacity', '').strip()
    capacity = int(capacity_str) if capacity_str and capacity_str.isdigit() else None
    sort_by = request.args.get('sort', 'name')  # name, recent, most_booked, top_rated
    use_advanced = request.args.get('advanced', 'false') == 'true'  # Enable advanced search
    show_all = request.args.get('show_all', 'false') == 'true'  # Show all resources (for owners/admins)

    with get_db_session() as session:
        dal = ResourceDAL(session)
        
        # If user is logged in and wants to see all their resources, or is admin
        if show_all and current_user.is_authenticated:
            from sqlalchemy import text
            query = "SELECT * FROM resources WHERE 1=1"
            params = {}
            
            # Non-admins only see their own resources
            if current_user.role != 'admin':
                query += " AND owner_id = :owner_id"
                params['owner_id'] = current_user.user_id
            
            if search_term:
                query += " AND (title LIKE :search_term OR description LIKE :search_term)"
                params['search_term'] = f"%{search_term}%"
            
            if category:
                query += " AND category = :category"
                params['category'] = category
            
            if location:
                query += " AND location LIKE :location"
                params['location'] = f"%{location}%"
            
            if capacity is not None and capacity > 0:
                query += " AND capacity >= :capacity"
                params['capacity'] = capacity
            
            query += " ORDER BY created_at DESC"
            
            result = session.execute(text(query), params)
            resources_list = []
            for row in result:
                # Create Resource objects for consistency
                resource_obj = Resource(
                    resource_id=row[0],
                    owner_id=row[1],
                    title=row[2],
                    description=row[3],
                    category=row[4],
                    location=row[5],
                    capacity=row[6],
                    images=row[7] if len(row) > 7 else None,
                    availability_rules=row[8] if len(row) > 8 else None,
                    status=row[9] if len(row) > 9 else 'draft',
                    created_at=row[10] if len(row) > 10 else None,
                )
                resources_list.append(resource_obj)
            resources = resources_list
        else:
            # Show only published resources for public view
            resources = dal.get_published_resources(
                search_term=search_term,
                category=category,
                location=location,
                capacity=capacity,
            )
        
        # Convert Resource objects to dictionaries for template (to avoid detached instance errors)
        # Also fetch owner information
        from src.data_access.user_dal import UserDAL
        user_dal = UserDAL(session)
        
        resources_dicts = []
        for resource in resources:
            owner = None
            if resource.owner_id:
                owner = user_dal.get_user_by_id(resource.owner_id)
            
            resources_dicts.append({
                'resource_id': resource.resource_id,
                'owner_id': resource.owner_id,
                'owner_name': owner.name if owner else 'Unknown',
                'title': resource.title,
                'description': resource.description,
                'category': resource.category,
                'location': resource.location,
                'capacity': resource.capacity,
                'images': resource.images,
                'availability_rules': resource.availability_rules,
                'status': resource.status,
                'created_at': resource.created_at,
            })
        resources = resources_dicts
        
        # Apply advanced search if enabled
        if use_advanced and search_term:
            from src.controllers.advanced_search import search_by_similarity
            # Convert back to Resource objects for search
            resource_objs = []
            for r_dict in resources:
                resource_objs.append(Resource(
                    resource_id=r_dict['resource_id'],
                    owner_id=r_dict['owner_id'],
                    title=r_dict['title'],
                    description=r_dict['description'],
                    category=r_dict['category'],
                    location=r_dict['location'],
                    capacity=r_dict['capacity'],
                    images=r_dict['images'],
                    availability_rules=r_dict['availability_rules'],
                    status=r_dict['status'],
                    created_at=r_dict['created_at'],
                ))
            resources = search_by_similarity(search_term, resource_objs, top_k=50)
            # Convert back to dicts with owner info
            resources_with_owners = []
            for r in resources:
                owner = None
                if r.owner_id:
                    owner = user_dal.get_user_by_id(r.owner_id)
                resources_with_owners.append({
                    'resource_id': r.resource_id,
                    'owner_id': r.owner_id,
                    'owner_name': owner.name if owner else 'Unknown',
                    'title': r.title,
                    'description': r.description,
                    'category': r.category,
                    'location': r.location,
                    'capacity': r.capacity,
                    'images': r.images,
                    'status': r.status,
                    'created_at': r.created_at
                })
            resources = resources_with_owners
        
        # Add aggregate ratings to all resources
        from src.data_access.review_dal import ReviewDAL
        review_dal = ReviewDAL(session)
        for resource_dict in resources:
            stats = review_dal.get_resource_rating_stats(resource_dict['resource_id'])
            resource_dict['avg_rating'] = stats['avg_rating']
            resource_dict['total_reviews'] = stats['total_reviews']
        
        # Apply sorting
        if sort_by == 'name':
            resources = sorted(resources, key=lambda r: r.get('title', '').lower())
        elif sort_by == 'most_booked':
            # Sort by number of bookings - query actual booking counts
            from sqlalchemy import text
            resources_with_counts = []
            for resource_dict in resources:
                booking_count_result = session.execute(
                    text("SELECT COUNT(*) FROM bookings WHERE resource_id = :resource_id AND status IN ('approved', 'pending', 'completed')"),
                    {"resource_id": resource_dict['resource_id']}
                )
                booking_count = booking_count_result.scalar() or 0
                resource_dict['booking_count'] = booking_count
                resources_with_counts.append(resource_dict)
            resources = sorted(resources_with_counts, key=lambda r: r.get('booking_count', 0), reverse=True)
        elif sort_by == 'top_rated':
            # Sort by average rating
            resources = sorted(resources, key=lambda r: r.get('avg_rating', 0), reverse=True)
        elif sort_by == 'recent':
            # Sort by created_at DESC (most recent first)
            resources = sorted(resources, key=lambda r: r.get('created_at') or '', reverse=True)
        # Default is already handled
        
        # Find top-rated resource for badge (highest avg_rating with at least 1 review)
        top_rated_resource_id = None
        top_rated_avg = 0
        for resource_dict in resources:
            if resource_dict.get('total_reviews', 0) > 0:
                avg_rating = resource_dict.get('avg_rating', 0)
                if avg_rating > top_rated_avg:
                    top_rated_avg = avg_rating
                    top_rated_resource_id = resource_dict['resource_id']
        
        # Mark top-rated resource
        for resource_dict in resources:
            if resource_dict['resource_id'] == top_rated_resource_id:
                resource_dict['is_top_rated'] = True
            else:
                resource_dict['is_top_rated'] = False

    return render_template(
        'index.html',
        resources=resources,
        search_term=search_term,
        category=category,
        location=location,
        capacity=capacity,
        sort_by=sort_by,
        show_all=show_all,
    )


@resource_bp.route('/api/categories')
def get_categories():
    """API endpoint to get all unique categories from published resources."""
    from flask import jsonify
    with get_db_session() as session:
        from sqlalchemy import text
        result = session.execute(
            text("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != '' AND status = 'published' ORDER BY category")
        )
        categories = [row[0] for row in result if row[0]]
        return jsonify({'categories': categories})


@resource_bp.route('/<int:resource_id>/json')
def resource_detail_json(resource_id: int):
    """API endpoint to get resource details as JSON for modal popup."""
    from flask import jsonify
    with get_db_session() as session:
        dal = ResourceDAL(session)
        resource = dal.get_resource_by_id(resource_id)

        if resource is None:
            return jsonify({'error': 'Resource not found'}), 404

        # Get owner information
        from src.data_access.user_dal import UserDAL
        user_dal = UserDAL(session)
        owner = None
        if resource.owner_id:
            owner = user_dal.get_user_by_id(resource.owner_id)
        
        # Get reviews and rating stats
        from src.data_access.review_dal import ReviewDAL
        review_dal = ReviewDAL(session)
        reviews = review_dal.get_reviews_for_resource(resource_id)
        rating_stats = review_dal.get_resource_rating_stats(resource_id)
        
        # Get equipment
        from sqlalchemy import text
        equipment_result = session.execute(
            text("SELECT name FROM equipment WHERE resource_id = :resource_id"),
            {"resource_id": resource_id}
        )
        equipment = [row[0] for row in equipment_result]
        
        # Get existing bookings
        from src.data_access.booking_dal import BookingDAL
        booking_dal = BookingDAL(session)
        existing_bookings = booking_dal.get_bookings_for_resource(resource_id)
        bookings_data = []
        for booking in existing_bookings:
            if booking.start_datetime and booking.end_datetime:
                bookings_data.append({
                    'start': booking.start_datetime.isoformat() if hasattr(booking.start_datetime, 'isoformat') else str(booking.start_datetime),
                    'end': booking.end_datetime.isoformat() if hasattr(booking.end_datetime, 'isoformat') else str(booking.end_datetime),
                    'status': booking.status
                })
        
        # Parse images
        images_list = []
        if resource.images:
            images_list = [img.strip() for img in resource.images.split(',') if img.strip()]
        
        return jsonify({
            'resource_id': resource.resource_id,
            'owner_id': resource.owner_id,
            'owner_name': owner.name if owner else 'Unknown',
            'title': resource.title,
            'description': resource.description or 'No description provided.',
            'category': resource.category,
            'location': resource.location,
            'capacity': resource.capacity,
            'images': images_list,
            'equipment': equipment,
            'rating_stats': rating_stats,
            'reviews': [
                {
                    'reviewer_id': review.reviewer_id,
                    'rating': review.rating,
                    'comment': review.comment or 'No comment provided.',
                    'timestamp': review.timestamp.isoformat() if review.timestamp and hasattr(review.timestamp, 'isoformat') else str(review.timestamp) if review.timestamp else None
                }
                for review in reviews[:5]  # Limit to 5 most recent
            ],
            'bookings': bookings_data,
            'booking_type': getattr(resource, 'booking_type', 'open'),
            'status': resource.status
        })


@resource_bp.route('/<int:resource_id>')
def resource_detail(resource_id: int):
    with get_db_session() as session:
        dal = ResourceDAL(session)
        resource = dal.get_resource_by_id(resource_id)

        if resource is None:
            abort(404)

        # Access all needed attributes while still in session context
        # This prevents DetachedInstanceError when the session closes
        # Get owner information
        from src.data_access.user_dal import UserDAL
        user_dal = UserDAL(session)
        owner = None
        if resource.owner_id:
            owner = user_dal.get_user_by_id(resource.owner_id)
        
        resource_dict = {
            'resource_id': resource.resource_id,
            'owner_id': resource.owner_id,
            'owner_name': owner.name if owner else 'Unknown',
            'owner_email': owner.email if owner else None,
            'title': resource.title,
            'description': resource.description,
            'category': resource.category,
            'location': resource.location,
            'capacity': resource.capacity,
            'images': resource.images,
            'availability_rules': resource.availability_rules,
            'status': resource.status,
            'created_at': resource.created_at,
        }

        # Get reviews for this resource
        from src.data_access.review_dal import ReviewDAL
        review_dal = ReviewDAL(session)
        reviews = review_dal.get_reviews_for_resource(resource_id)
        rating_stats = review_dal.get_resource_rating_stats(resource_id)
        
        # Get equipment
        from sqlalchemy import text
        equipment_result = session.execute(
            text("SELECT name FROM equipment WHERE resource_id = :resource_id"),
            {"resource_id": resource_id}
        )
        equipment = [row[0] for row in equipment_result]
        
        # Get existing bookings for calendar display
        from src.data_access.booking_dal import BookingDAL
        booking_dal = BookingDAL(session)
        existing_bookings = booking_dal.get_bookings_for_resource(resource_id)
        # Convert to JSON-serializable format
        bookings_data = []
        for booking in existing_bookings:
            if booking.start_datetime and booking.end_datetime:
                bookings_data.append({
                    'start': booking.start_datetime.isoformat() if hasattr(booking.start_datetime, 'isoformat') else str(booking.start_datetime),
                    'end': booking.end_datetime.isoformat() if hasattr(booking.end_datetime, 'isoformat') else str(booking.end_datetime),
                    'status': booking.status
                })

    # Create a simple object-like structure for the template
    class ResourceObj:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    resource_obj = ResourceObj(resource_dict)

    return render_template('resources/detail.html', resource=resource_obj, reviews=reviews, rating_stats=rating_stats, equipment=equipment, existing_bookings=bookings_data)


@resource_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_resource():
    # Restrict resource creation to staff and admin only
    if current_user.role == 'student':
        flash('Only staff and administrators can create resources. Students can view, book, and review resources.', 'error')
        return redirect(url_for('resources.list_resources'))
    
    form = ResourceForm()
    
    # Populate category choices dynamically from database
    with get_db_session() as session:
        from sqlalchemy import text
        result = session.execute(
            text("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != '' ORDER BY category")
        )
        existing_categories = [row[0] for row in result if row[0]]
        # Build choices: empty option + existing categories
        category_choices = [('', 'Select a category...')]
        category_choices.extend([(cat, cat) for cat in existing_categories])
        # Add "Other" option if not already present
        if 'Other' not in existing_categories:
            category_choices.append(('Other', 'Other'))
        form.category.choices = category_choices

    if form.validate_on_submit():
        # Handle file uploads
        image_paths = None
        if request.files:
            files = request.files.getlist('images')
            if files and files[0].filename:  # Check if files were actually uploaded
                image_paths = save_uploaded_files(files, allowed_file)

        # Process availability rules from calendar
        availability_rules = None
        if request.form.get('availability_rules'):
            availability_rules = request.form.get('availability_rules')
        elif request.form.get('availability_days'):
            # Convert calendar selections to JSON
            import json
            days = request.form.getlist('availability_days')
            start_time = request.form.get('availability_start_time')
            end_time = request.form.get('availability_end_time')
            if days and start_time and end_time:
                availability_rules = json.dumps({
                    'days': days,
                    'start_time': start_time,
                    'end_time': end_time
                })
        
        data = {
            'title': form.title.data,
            'description': form.description.data,
            'category': form.category.data,
            'location': form.location.data,
            'capacity': form.capacity.data,
            'images': image_paths,
            'availability_rules': availability_rules or form.availability_rules.data,
            'status': form.status.data,
            'booking_type': form.booking_type.data,
        }

        try:
            with get_db_session() as session:
                dal = ResourceDAL(session)
                resource = dal.create_resource(user_id=current_user.user_id, data=data)
                
                # Store resource_id while still in session context
                resource_id = resource.resource_id
                
                # Handle equipment list
                if form.equipment.data:
                    equipment_items = [item.strip() for item in form.equipment.data.split(',') if item.strip()]
                    from src.models import Equipment
                    for item in equipment_items:
                        equipment = Equipment(resource_id=resource_id, name=item)
                        session.add(equipment)
                # Commit will happen automatically when exiting the context manager

            if resource_id:
                flash('Resource created successfully.', 'success')
                return redirect(url_for('resources.resource_detail', resource_id=resource_id))
            else:
                flash('Failed to create resource. Please try again.', 'error')
        except Exception as e:
            flash(f'Error creating resource: {str(e)}', 'error')
            import traceback
            print(traceback.format_exc())

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'error')

    return render_template('resources/create.html', form=form)


@resource_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resource(resource_id: int):
    """Edit a resource (owner or admin only)."""
    with get_db_session() as session:
        dal = ResourceDAL(session)
        resource = dal.get_resource_by_id(resource_id)
        
        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('resources.list_resources'))
        
        # Access all needed attributes while still in session context
        owner_id = resource.owner_id
        availability_rules_str = resource.availability_rules
        
        # Permission check: owner or admin only
        if owner_id != current_user.user_id and current_user.role != 'admin':
            flash('You do not have permission to edit this resource.', 'error')
            return redirect(url_for('resources.resource_detail', resource_id=resource_id))
        
        # Create a dict for the form
        resource_dict = {
            'title': resource.title,
            'description': resource.description,
            'category': resource.category,
            'location': resource.location,
            'capacity': resource.capacity,
            'images': resource.images,
            'status': resource.status,
            'booking_type': getattr(resource, 'booking_type', 'open'),
        }
        
        # Create a simple object for form population
        class ResourceFormObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        form_obj = ResourceFormObj(resource_dict)
        form = ResourceForm(obj=form_obj)
        
        # Populate category choices dynamically from database
        from sqlalchemy import text
        result = session.execute(
            text("SELECT DISTINCT category FROM resources WHERE category IS NOT NULL AND category != '' ORDER BY category")
        )
        existing_categories = [row[0] for row in result if row[0]]
        # Build choices: empty option + existing categories
        category_choices = [('', 'Select a category...')]
        category_choices.extend([(cat, cat) for cat in existing_categories])
        # Add current category if not in list
        if resource.category and resource.category not in existing_categories:
            category_choices.append((resource.category, resource.category))
        # Add "Other" option if not already present
        if 'Other' not in existing_categories and resource.category != 'Other':
            category_choices.append(('Other', 'Other'))
        form.category.choices = category_choices
        
        # Get existing equipment
        from sqlalchemy import text
        equipment_result = session.execute(
            text("SELECT name FROM equipment WHERE resource_id = :resource_id"),
            {"resource_id": resource_id}
        )
        existing_equipment = ', '.join([row[0] for row in equipment_result])
        if existing_equipment:
            form.equipment.data = existing_equipment
        
        # Parse existing availability rules for display
        availability_data = {}
        if availability_rules_str:
            import json
            try:
                availability_data = json.loads(availability_rules_str)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Create resource object for template
        resource_dict_full = {
            'resource_id': resource.resource_id,
            'owner_id': owner_id,
            'title': resource.title,
            'description': resource.description,
            'category': resource.category,
            'location': resource.location,
            'capacity': resource.capacity,
            'images': resource.images,
            'availability_rules': availability_rules_str,
            'status': resource.status,
            'created_at': resource.created_at,
        }
        
        class ResourceObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        resource_obj = ResourceObj(resource_dict_full)
        
        if request.method == 'GET':
            return render_template('resources/edit.html', form=form, resource=resource_obj, availability_data=availability_data)
        
        if form.validate_on_submit():
            # Handle file uploads - use the stored value from earlier
            image_paths = resource_dict_full.get('images')  # Keep existing images
            if request.files:
                files = request.files.getlist('images')
                if files and files[0].filename:
                    new_image_paths = save_uploaded_files(files, allowed_file)
                    if new_image_paths:
                        image_paths = new_image_paths if not image_paths else f"{image_paths},{new_image_paths}"
            
            # Process availability rules from calendar - use stored value
            availability_rules = availability_rules_str  # Keep existing if not changed
            if request.form.get('availability_rules'):
                availability_rules = request.form.get('availability_rules')
            elif request.form.get('availability_days'):
                # Convert calendar selections to JSON
                import json
                days = request.form.getlist('availability_days')
                start_time = request.form.get('availability_start_time')
                end_time = request.form.get('availability_end_time')
                if days and start_time and end_time:
                    availability_rules = json.dumps({
                        'days': days,
                        'start_time': start_time,
                        'end_time': end_time
                    })
            
            data = {
                'title': form.title.data,
                'description': form.description.data,
                'category': form.category.data,
                'location': form.location.data,
                'capacity': form.capacity.data,
                'images': image_paths,
                'availability_rules': availability_rules or form.availability_rules.data,
                'status': form.status.data,
                'booking_type': form.booking_type.data,
            }
            
            updated_resource = dal.update_resource(resource_id, data)
            
            # Update equipment
            if form.equipment.data:
                # Delete old equipment
                session.execute(
                    text("DELETE FROM equipment WHERE resource_id = :resource_id"),
                    {"resource_id": resource_id}
                )
                # Add new equipment
                equipment_items = [item.strip() for item in form.equipment.data.split(',') if item.strip()]
                from src.models import Equipment
                for item in equipment_items:
                    equipment = Equipment(resource_id=resource_id, name=item)
                    session.add(equipment)
                session.commit()
            
            if updated_resource:
                flash('Resource updated successfully.', 'success')
                return redirect(url_for('resources.resource_detail', resource_id=resource_id))
            else:
                flash('Failed to update resource.', 'error')
    
    return render_template('resources/edit.html', form=form, resource=resource_obj, availability_data=availability_data)


@resource_bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id: int):
    """Delete a resource (owner or admin only)."""
    # Validate CSRF token
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('resources.resource_detail', resource_id=resource_id))
    
    with get_db_session() as session:
        dal = ResourceDAL(session)
        resource = dal.get_resource_by_id(resource_id)
        
        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('resources.list_resources'))
        
        # Permission check: owner or admin only
        if resource.owner_id != current_user.user_id and current_user.role != 'admin':
            flash('You do not have permission to delete this resource.', 'error')
            return redirect(url_for('resources.resource_detail', resource_id=resource_id))
        
        success = dal.delete_resource(resource_id)
        
        if success:
            flash('Resource deleted successfully.', 'success')
            return redirect(url_for('resources.list_resources'))
        else:
            flash('Failed to delete resource.', 'error')
            return redirect(url_for('resources.resource_detail', resource_id=resource_id))


from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf.csrf import validate_csrf

from src.controllers.auth_routes import get_db_session
from src.data_access.booking_dal import BookingDAL
from src.data_access.resource_dal import ResourceDAL
from src.data_access.waitlist_dal import WaitlistDAL
from src.forms.resource_forms import BookingForm

booking_bp = Blueprint('bookings', __name__)


@booking_bp.route('/create/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def create_booking(resource_id: int):
    """Create a new booking for a resource."""
    form = BookingForm()

    with get_db_session() as session:
        resource_dal = ResourceDAL(session)
        resource = resource_dal.get_resource_by_id(resource_id)

        if not resource:
            flash('Resource not found.', 'error')
            return redirect(url_for('resources.list_resources'))

        if request.method == 'POST':
            # Validate CSRF token for raw form submissions
            try:
                validate_csrf(request.form.get('csrf_token'))
            except Exception:
                flash('Invalid security token. Please try again.', 'error')
                return render_template('bookings/create.html', form=form, resource=resource)
            
            # Handle both FlaskForm and raw form data
            if form.validate_on_submit():
                # Form data from BookingForm
                start_datetime_str = form.start_datetime.data
                end_datetime_str = form.end_datetime.data
                message_content = form.message.data
            else:
                # Raw form data from resource detail page
                start_datetime_str = request.form.get('start_datetime')
                end_datetime_str = request.form.get('end_datetime')
                message_content = request.form.get('message')
            
            if not start_datetime_str or not end_datetime_str:
                flash('Start time and end time are required.', 'error')
                return render_template('bookings/create.html', form=form, resource=resource)
            
            # Parse datetime from form (datetime-local format: YYYY-MM-DDTHH:MM)
            try:
                start_time = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
                end_time = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')
            except (ValueError, AttributeError, TypeError):
                flash('Invalid date/time format. Please use the date picker.', 'error')
                return render_template('bookings/create.html', form=form, resource=resource)

            if end_time <= start_time:
                flash('End time must be after start time.', 'error')
                return render_template('bookings/create.html', form=form, resource=resource)

            booking_dal = BookingDAL(session)
            
            # Determine approval status (auto-approve for now, can be enhanced)
            initial_status = 'approved' if resource.status == 'published' else 'pending'
            
            booking = booking_dal.create_booking(
                resource_id=resource_id,
                requester_id=current_user.user_id,
                start_time=start_time,
                end_time=end_time,
                initial_status=initial_status,
            )

            if booking:
                # Create message if provided
                if message_content:
                    from src.data_access.message_dal import MessageDAL
                    message_dal = MessageDAL(session)
                    message_dal.create_message(
                        sender_id=current_user.user_id,
                        receiver_id=resource.owner_id,
                        content=message_content,
                        thread_id=booking.booking_id,
                    )

                flash(f'Booking {"approved" if initial_status == "approved" else "requested"} successfully!', 'success')
                return redirect(url_for('bookings.my_bookings'))
            else:
                # Conflict detected - offer waitlist
                flash('This time slot is already booked. You can join the waitlist below.', 'warning')
                return render_template('bookings/create.html', form=form, resource=resource, show_waitlist=True)

    return render_template('bookings/create.html', form=form, resource=resource, show_waitlist=False)


@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    """Display user's bookings."""
    with get_db_session() as session:
        booking_dal = BookingDAL(session)
        # Get user's bookings
        from sqlalchemy import text
        result = session.execute(
            text("""
                SELECT b.*, r.title, r.location
                FROM bookings b
                JOIN resources r ON b.resource_id = r.resource_id
                WHERE b.requester_id = :user_id
                ORDER BY b.start_datetime DESC
            """),
            {"user_id": current_user.user_id}
        )
        bookings = []
        for row in result:
            booking_dict = dict(row._mapping)
            # Convert datetime strings to datetime objects if they're strings
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

    return render_template('bookings/my_bookings.html', bookings=bookings)


@booking_bp.route('/approve/<int:booking_id>')
@login_required
def approve_booking(booking_id: int):
    """Approve a pending booking (staff/admin only)."""
    if current_user.role not in ('staff', 'admin'):
        flash('You do not have permission to approve bookings.', 'error')
        return redirect(url_for('bookings.my_bookings'))

    with get_db_session() as session:
        booking_dal = BookingDAL(session)
        booking = booking_dal.update_booking_status(booking_id, 'approved')
        
        if booking:
            flash('Booking approved successfully.', 'success')
        else:
            flash('Failed to approve booking.', 'error')

    return redirect(url_for('admin.admin_dashboard'))


@booking_bp.route('/cancel/<int:booking_id>')
@login_required
def cancel_booking(booking_id: int):
    """Cancel a booking."""
    with get_db_session() as session:
        booking_dal = BookingDAL(session)
        booking = booking_dal.update_booking_status(booking_id, 'cancelled')
        
        if booking:
            flash('Booking cancelled successfully.', 'success')
        else:
            flash('Failed to cancel booking.', 'error')

    return redirect(url_for('bookings.my_bookings'))


@booking_bp.route('/waitlist/<int:resource_id>', methods=['POST'])
@login_required
def join_waitlist(resource_id: int):
    """Join the waitlist for a resource."""
    # Validate CSRF token
    try:
        validate_csrf(request.form.get('csrf_token'))
    except Exception:
        flash('Invalid security token. Please try again.', 'error')
        return redirect(url_for('resources.resource_detail', resource_id=resource_id))
    
    with get_db_session() as session:
        waitlist_dal = WaitlistDAL(session)
        preferred_start = request.form.get('preferred_start')
        preferred_end = request.form.get('preferred_end')
        
        start_dt = None
        end_dt = None
        if preferred_start:
            try:
                start_dt = datetime.strptime(preferred_start, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        if preferred_end:
            try:
                end_dt = datetime.strptime(preferred_end, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        success = waitlist_dal.add_to_waitlist(
            resource_id=resource_id,
            user_id=current_user.user_id,
            preferred_start=start_dt,
            preferred_end=end_dt,
        )
        
        if success:
            flash('You have been added to the waitlist. You will be notified when a slot becomes available.', 'success')
        else:
            flash('You are already on the waitlist for this resource.', 'info')
    
    return redirect(url_for('resources.resource_detail', resource_id=resource_id))


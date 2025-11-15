from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ResourceForm(FlaskForm):
    """Form for creating and editing resources."""
    title = StringField(
        'Title',
        validators=[DataRequired(message='Title is required.'), Length(max=200)],
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=2000)],
        render_kw={'rows': 6},
    )
    category = SelectField(
        'Category',
        choices=[
            ('', 'Select a category...'),
            ('Study Room', 'Study Room'),
            ('Meeting Space', 'Meeting Space'),
            ('Lab Equipment', 'Lab Equipment'),
            ('AV Equipment', 'AV Equipment'),
            ('Event Space', 'Event Space'),
            ('Tutoring Time', 'Tutoring Time'),
            ('Other', 'Other'),
        ],
        validators=[DataRequired(message='Category is required.')],
    )
    location = StringField(
        'Location',
        validators=[DataRequired(message='Location is required.'), Length(max=200)],
    )
    capacity = IntegerField(
        'Capacity',
        validators=[Optional(), NumberRange(min=1, message='Capacity must be at least 1.')],
    )
    status = SelectField(
        'Status',
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft',
        validators=[DataRequired()],
    )
    booking_type = SelectField(
        'Booking Approval',
        choices=[
            ('open', 'Unrestricted - Auto-approved'),
            ('restricted', 'Requires Approval - Manual review'),
        ],
        default='open',
        validators=[DataRequired()],
        description='Unrestricted resources are automatically approved when booked. Resources requiring approval need manual admin/staff review.',
    )
    images = FileField(
        'Images',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed.'),
        ],
        render_kw={'multiple': True},
    )
    availability_rules = TextAreaField(
        'Availability Rules (JSON)',
        validators=[Optional()],
        render_kw={'rows': 4, 'placeholder': '{"days": ["Monday", "Wednesday"], "start_time": "09:00", "end_time": "17:00"}'},
    )
    equipment = StringField(
        'Equipment (comma-separated)',
        validators=[Optional()],
        render_kw={'placeholder': 'e.g., Projector, Whiteboard, WiFi'},
    )
    submit = SubmitField('Save Resource')


class BookingForm(FlaskForm):
    """Form for creating bookings."""
    start_datetime = StringField(
        'Start Date & Time',
        validators=[DataRequired(message='Start time is required.')],
        render_kw={'type': 'datetime-local'},
    )
    end_datetime = StringField(
        'End Date & Time',
        validators=[DataRequired(message='End time is required.')],
        render_kw={'type': 'datetime-local'},
    )
    message = TextAreaField(
        'Message to Owner (Optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'rows': 3},
    )
    submit = SubmitField('Request Booking')


class ReviewForm(FlaskForm):
    """Form for submitting reviews."""
    rating = SelectField(
        'Rating',
        choices=[(str(i), '⭐' * i) for i in range(1, 6)],
        validators=[DataRequired(message='Rating is required.')],
    )
    comment = TextAreaField(
        'Comment',
        validators=[Optional(), Length(max=1000)],
        render_kw={'rows': 4, 'placeholder': 'Share your experience...'},
    )
    submit = SubmitField('Submit Review')


class MessageForm(FlaskForm):
    """Form for sending messages."""
    content = TextAreaField(
        'Message',
        validators=[DataRequired(message='Message content is required.'), Length(max=1000)],
        render_kw={'rows': 4},
    )
    submit = SubmitField('Send Message')


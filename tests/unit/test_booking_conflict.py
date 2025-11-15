"""
Unit tests for booking conflict detection logic.
References: docs/context/PM/PRD.md - Section 4.4 Booking & Scheduling
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Resource, Booking, User
from src.data_access.booking_dal import BookingDAL


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        name='Test User',
        email='test@example.com',
        password_hash='hashed_password',
        role='student'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_resource(db_session, test_user):
    """Create a test resource."""
    resource = Resource(
        owner_id=test_user.user_id,
        title='Test Room',
        description='A test room',
        category='Study Room',
        location='Building A',
        capacity=10,
        status='published',
        booking_type='open'
    )
    db_session.add(resource)
    db_session.commit()
    return resource


def test_no_conflict_when_no_existing_bookings(db_session, test_resource, test_user):
    """Test that booking succeeds when there are no existing bookings."""
    booking_dal = BookingDAL(db_session)
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    booking = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start_time,
        end_time=end_time,
        initial_status='approved'
    )
    
    assert booking is not None
    assert booking.resource_id == test_resource.resource_id
    assert booking.requester_id == test_user.user_id


def test_conflict_when_times_overlap(db_session, test_resource, test_user):
    """Test that conflict is detected when booking times overlap."""
    booking_dal = BookingDAL(db_session)
    
    # Create first booking
    start1 = datetime.now() + timedelta(days=1, hours=10)
    end1 = start1 + timedelta(hours=2)
    booking1 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start1,
        end_time=end1,
        initial_status='approved'
    )
    assert booking1 is not None
    
    # Try to create overlapping booking
    start2 = start1 + timedelta(hours=1)  # Overlaps with first booking
    end2 = start2 + timedelta(hours=2)
    booking2 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start2,
        end_time=end2,
        initial_status='approved'
    )
    
    # Should return None due to conflict
    assert booking2 is None


def test_no_conflict_when_times_adjacent(db_session, test_resource, test_user):
    """Test that bookings can be adjacent (end time = next start time)."""
    booking_dal = BookingDAL(db_session)
    
    # Create first booking
    start1 = datetime.now() + timedelta(days=1, hours=10)
    end1 = start1 + timedelta(hours=2)
    booking1 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start1,
        end_time=end1,
        initial_status='approved'
    )
    assert booking1 is not None
    
    # Create adjacent booking (starts exactly when first ends)
    start2 = end1
    end2 = start2 + timedelta(hours=2)
    booking2 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start2,
        end_time=end2,
        initial_status='approved'
    )
    
    # Should succeed - no overlap
    assert booking2 is not None


def test_conflict_detection_ignores_cancelled_bookings(db_session, test_resource, test_user):
    """Test that cancelled bookings don't cause conflicts."""
    booking_dal = BookingDAL(db_session)
    
    # Create cancelled booking
    start1 = datetime.now() + timedelta(days=1, hours=10)
    end1 = start1 + timedelta(hours=2)
    booking1 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start1,
        end_time=end1,
        initial_status='approved'
    )
    booking1.status = 'cancelled'
    db_session.commit()
    
    # Try to book same time slot
    booking2 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start1,
        end_time=end1,
        initial_status='approved'
    )
    
    # Should succeed - cancelled booking doesn't block
    assert booking2 is not None


def test_conflict_detection_checks_pending_bookings(db_session, test_resource, test_user):
    """Test that pending bookings are considered in conflict detection."""
    booking_dal = BookingDAL(db_session)
    
    # Create pending booking
    start1 = datetime.now() + timedelta(days=1, hours=10)
    end1 = start1 + timedelta(hours=2)
    booking1 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start1,
        end_time=end1,
        initial_status='pending'
    )
    assert booking1 is not None
    
    # Try to create overlapping booking
    start2 = start1 + timedelta(minutes=30)
    end2 = start2 + timedelta(hours=1)
    booking2 = booking_dal.create_booking(
        resource_id=test_resource.resource_id,
        requester_id=test_user.user_id,
        start_time=start2,
        end_time=end2,
        initial_status='approved'
    )
    
    # Should fail - pending booking blocks
    assert booking2 is None


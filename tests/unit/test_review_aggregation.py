"""
Unit tests for review aggregation and rating calculations.
References: docs/context/PM/PRD.md - Section 4.6 Reviews & Ratings
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Resource, Review, User
from src.data_access.review_dal import ReviewDAL


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
        status='published'
    )
    db_session.add(resource)
    db_session.commit()
    return resource


def test_no_reviews_returns_zero_stats(db_session, test_resource):
    """Test that resources with no reviews return zero stats."""
    review_dal = ReviewDAL(db_session)
    stats = review_dal.get_resource_rating_stats(test_resource.resource_id)
    
    assert stats['total_reviews'] == 0
    assert stats['avg_rating'] == 0.0
    assert stats['min_rating'] == 0
    assert stats['max_rating'] == 0


def test_single_review_calculation(db_session, test_resource, test_user):
    """Test rating calculation with a single review."""
    review_dal = ReviewDAL(db_session)
    
    review = review_dal.create_review(
        resource_id=test_resource.resource_id,
        reviewer_id=test_user.user_id,
        rating=5,
        comment='Great resource!'
    )
    
    stats = review_dal.get_resource_rating_stats(test_resource.resource_id)
    
    assert stats['total_reviews'] == 1
    assert stats['avg_rating'] == 5.0
    assert stats['min_rating'] == 5
    assert stats['max_rating'] == 5


def test_multiple_reviews_average_calculation(db_session, test_resource, test_user):
    """Test that average rating is correctly calculated from multiple reviews."""
    review_dal = ReviewDAL(db_session)
    
    # Create multiple reviews
    review_dal.create_review(test_resource.resource_id, test_user.user_id, 5, 'Excellent')
    review_dal.create_review(test_resource.resource_id, test_user.user_id, 4, 'Good')
    review_dal.create_review(test_resource.resource_id, test_user.user_id, 3, 'Average')
    
    stats = review_dal.get_resource_rating_stats(test_resource.resource_id)
    
    assert stats['total_reviews'] == 3
    assert stats['avg_rating'] == 4.0  # (5+4+3)/3 = 4.0
    assert stats['min_rating'] == 3
    assert stats['max_rating'] == 5


def test_rating_stats_rounding(db_session, test_resource, test_user):
    """Test that average rating is properly rounded."""
    review_dal = ReviewDAL(db_session)
    
    # Create reviews that will result in non-integer average
    review_dal.create_review(test_resource.resource_id, test_user.user_id, 5, 'Great')
    review_dal.create_review(test_resource.resource_id, test_user.user_id, 4, 'Good')
    
    stats = review_dal.get_resource_rating_stats(test_resource.resource_id)
    
    assert stats['avg_rating'] == 4.5  # (5+4)/2 = 4.5
    assert isinstance(stats['avg_rating'], float)


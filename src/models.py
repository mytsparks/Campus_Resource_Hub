from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import inspect  # noqa: F401  # Needed for introspection, helpful for AI features
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


def init_db(engine):
    """Creates all tables defined in Base.metadata."""

    Base.metadata.create_all(engine)


class User(Base):
    """Represents a user (Student, Staff, or Admin) of the system."""

    __tablename__ = 'users'
    __allow_unmapped__ = True

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    profile_image = Column(String)
    department = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    resources_owned: List['Resource'] = relationship(
        'Resource',
        back_populates='owner',
        cascade='all, delete-orphan'
    )
    bookings_requested: List['Booking'] = relationship(
        'Booking',
        back_populates='requester'
    )
    reviews_left: List['Review'] = relationship(
        'Review',
        back_populates='reviewer'
    )
    messages_sent: List['Message'] = relationship(
        'Message',
        back_populates='sender',
        foreign_keys='Message.sender_id'
    )
    messages_received: List['Message'] = relationship(
        'Message',
        back_populates='receiver',
        foreign_keys='Message.receiver_id'
    )
    admin_actions: List['AdminLog'] = relationship(
        'AdminLog',
        back_populates='admin'
    )

    def is_active(self):
        return True

    def get_id(self):
        return str(self.user_id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return f"User(id={self.user_id}, email='{self.email}', role='{self.role}')"


class Resource(Base):
    """Represents a reservable resource (room, equipment, time, etc.)."""

    __tablename__ = 'resources'
    __allow_unmapped__ = True

    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.user_id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    location = Column(String)
    capacity = Column(Integer)
    images = Column(Text)
    availability_rules = Column(Text)
    status = Column(String, default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)

    owner: 'User' = relationship('User', back_populates='resources_owned')
    bookings: List['Booking'] = relationship(
        'Booking',
        back_populates='resource',
        cascade='all, delete-orphan'
    )
    reviews: List['Review'] = relationship(
        'Review',
        back_populates='resource',
        cascade='all, delete-orphan'
    )
    equipment: List['Equipment'] = relationship(
        'Equipment',
        back_populates='resource',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"Resource(id={self.resource_id}, title='{self.title}', status='{self.status}')"


class Booking(Base):
    """Represents a specific reservation instance for a resource."""

    __tablename__ = 'bookings'
    __allow_unmapped__ = True

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resources.resource_id'))
    requester_id = Column(Integer, ForeignKey('users.user_id'))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resource: 'Resource' = relationship('Resource', back_populates='bookings')
    requester: 'User' = relationship('User', back_populates='bookings_requested')

    def __repr__(self):
        return f"Booking(id={self.booking_id}, status='{self.status}', start='{self.start_datetime}')"


class Message(Base):
    """Represents a message within a thread between a requester and a resource owner."""

    __tablename__ = 'messages'
    __allow_unmapped__ = True

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer)
    sender_id = Column(Integer, ForeignKey('users.user_id'))
    receiver_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender: 'User' = relationship(
        'User',
        back_populates='messages_sent',
        foreign_keys=[sender_id]
    )
    receiver: 'User' = relationship(
        'User',
        back_populates='messages_received',
        foreign_keys=[receiver_id]
    )

    def __repr__(self):
        return f"Message(id={self.message_id}, thread={self.thread_id}, from={self.sender_id})"


class Review(Base):
    """Represents a rating and feedback left by a user after a completed booking."""

    __tablename__ = 'reviews'
    __allow_unmapped__ = True

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resources.resource_id'))
    reviewer_id = Column(Integer, ForeignKey('users.user_id'))
    rating = Column(Integer)
    comment = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    resource: 'Resource' = relationship('Resource', back_populates='reviews')
    reviewer: 'User' = relationship('User', back_populates='reviews_left')

    def __repr__(self):
        return f"Review(id={self.review_id}, resource={self.resource_id}, rating={self.rating})"


class AdminLog(Base):
    """Optional table for logging administrative actions (moderation, approvals, etc.)."""

    __tablename__ = 'admin_logs'
    __allow_unmapped__ = True

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('users.user_id'))
    action = Column(String)
    target_table = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    admin: 'User' = relationship('User', back_populates='admin_actions')

    def __repr__(self):
        return f"AdminLog(id={self.log_id}, action='{self.action}', target='{self.target_table}')"


class Equipment(Base):
    """Represents individual items or features associated with a Resource."""

    __tablename__ = 'equipment'
    __allow_unmapped__ = True

    equipment_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resources.resource_id'))
    name = Column(String, nullable=False)

    resource: 'Resource' = relationship('Resource', back_populates='equipment')

    def __repr__(self):
        return f"Equipment(id={self.equipment_id}, name='{self.name}')"


class Waitlist(Base):
    """Represents a user on a waitlist for a fully booked resource."""

    __tablename__ = 'waitlist'
    __allow_unmapped__ = True

    waitlist_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('resources.resource_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    preferred_start = Column(DateTime)
    preferred_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(String, default='no')  # 'no', 'yes', 'expired'

    def __repr__(self):
        return f"Waitlist(id={self.waitlist_id}, resource={self.resource_id}, user={self.user_id})"


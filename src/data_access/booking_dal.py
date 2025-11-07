from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import Booking, Resource


class BookingDAL:
    """Encapsulates all database interactions for the Booking model, including conflict detection."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def check_for_conflict(
        self,
        resource_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        from sqlalchemy import select
        stmt = select(Booking).where(
            Booking.resource_id == resource_id,
            Booking.status.in_(['pending', 'approved']),
            or_(
                and_(Booking.start_datetime <= start_time, Booking.end_datetime > start_time),
                and_(Booking.start_datetime < end_time, Booking.end_datetime >= end_time),
                and_(Booking.start_datetime >= start_time, Booking.end_datetime <= end_time),
            ),
        )
        result = self.db_session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def create_booking(
        self,
        resource_id: int,
        requester_id: int,
        start_time: datetime,
        end_time: datetime,
        initial_status: str,
    ) -> Booking | None:
        if self.check_for_conflict(resource_id, start_time, end_time):
            return None

        booking = Booking(
            resource_id=resource_id,
            requester_id=requester_id,
            start_datetime=start_time,
            end_datetime=end_time,
            status=initial_status,
        )

        try:
            self.db_session.add(booking)
            self.db_session.commit()
            return booking
        except SQLAlchemyError:
            self.db_session.rollback()
            return None

    def get_bookings_for_resource(self, resource_id: int) -> List[Booking]:
        from sqlalchemy import select
        stmt = select(Booking).where(
            Booking.resource_id == resource_id
        ).order_by(Booking.start_datetime.asc())
        result = self.db_session.execute(stmt)
        return list(result.scalars().all())

    def update_booking_status(self, booking_id: int, new_status: str) -> Booking | None:
        from sqlalchemy import select
        stmt = select(Booking).where(Booking.booking_id == booking_id)
        result = self.db_session.execute(stmt)
        booking = result.scalar_one_or_none()
        if not booking:
            return None

        booking.status = new_status

        try:
            self.db_session.commit()
            return booking
        except SQLAlchemyError:
            self.db_session.rollback()
            return None


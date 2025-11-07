from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class WaitlistDAL:
    """Encapsulates all database interactions for waitlist functionality."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_to_waitlist(
        self,
        resource_id: int,
        user_id: int,
        preferred_start: datetime | None = None,
        preferred_end: datetime | None = None,
    ) -> bool:
        """Add a user to the waitlist for a resource."""
        try:
            # Check if already on waitlist
            result = self.db_session.execute(
                text("""
                    SELECT * FROM waitlist 
                    WHERE resource_id = :resource_id AND user_id = :user_id
                """),
                {"resource_id": resource_id, "user_id": user_id}
            )
            if result.fetchone():
                return False  # Already on waitlist

            # Add to waitlist
            self.db_session.execute(
                text("""
                    INSERT INTO waitlist (resource_id, user_id, preferred_start, preferred_end, created_at)
                    VALUES (:resource_id, :user_id, :preferred_start, :preferred_end, :created_at)
                """),
                {
                    "resource_id": resource_id,
                    "user_id": user_id,
                    "preferred_start": preferred_start,
                    "preferred_end": preferred_end,
                    "created_at": datetime.utcnow(),
                }
            )
            self.db_session.commit()
            return True
        except SQLAlchemyError:
            self.db_session.rollback()
            return False

    def get_waitlist_for_resource(self, resource_id: int) -> List[dict]:
        """Get all users on waitlist for a resource, ordered by join time."""
        result = self.db_session.execute(
            text("""
                SELECT w.*, u.name, u.email
                FROM waitlist w
                JOIN users u ON w.user_id = u.user_id
                WHERE w.resource_id = :resource_id
                ORDER BY w.created_at ASC
            """),
            {"resource_id": resource_id}
        )
        return [dict(row._mapping) for row in result]

    def remove_from_waitlist(self, resource_id: int, user_id: int) -> bool:
        """Remove a user from the waitlist."""
        try:
            self.db_session.execute(
                text("""
                    DELETE FROM waitlist 
                    WHERE resource_id = :resource_id AND user_id = :user_id
                """),
                {"resource_id": resource_id, "user_id": user_id}
            )
            self.db_session.commit()
            return True
        except SQLAlchemyError:
            self.db_session.rollback()
            return False


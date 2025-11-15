from __future__ import annotations

from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import Resource, User


class ResourceDAL:
    """Encapsulates all database interactions for the Resource model."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_resource(self, user_id: int, data: dict) -> Resource:
        resource = Resource(
            owner_id=user_id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            location=data.get('location'),
            capacity=data.get('capacity'),
            images=data.get('images'),
            availability_rules=data.get('availability_rules'),
            status=data.get('status', 'draft'),
            booking_type=data.get('booking_type', 'open'),
        )

        self.db_session.add(resource)
        self.db_session.flush()  # Flush to get the ID without committing
        self.db_session.refresh(resource)  # Refresh to ensure all attributes are loaded
        # Don't commit here - let the context manager handle it
        return resource

    def get_resource_by_id(self, resource_id: int) -> Resource | None:
        # Use session.get() for proper ORM binding instead of raw SQL
        try:
            return self.db_session.get(Resource, resource_id)
        except Exception as e:
            # If booking_type column doesn't exist, use raw SQL query
            # This handles the case where migration hasn't been run yet
            if 'booking_type' in str(e) or 'no such column' in str(e).lower():
                from sqlalchemy import text
                result = self.db_session.execute(
                    text("""
                        SELECT resource_id, owner_id, title, description, category, 
                               location, capacity, images, availability_rules, status, created_at
                        FROM resources
                        WHERE resource_id = :resource_id
                    """),
                    {"resource_id": resource_id}
                )
                row = result.fetchone()
                if row:
                    # Create Resource object without booking_type
                    resource = Resource(
                        resource_id=row[0],
                        owner_id=row[1],
                        title=row[2],
                        description=row[3],
                        category=row[4],
                        location=row[5],
                        capacity=row[6],
                        images=row[7],
                        availability_rules=row[8],
                        status=row[9],
                        created_at=row[10] if len(row) > 10 else None,
                    )
                    # Set booking_type attribute manually (won't be in DB but code can use getattr)
                    resource.booking_type = 'open'  # Default value
                    return resource
                return None
            raise

    def get_published_resources(
        self,
        search_term: str | None = None,
        category: str | None = None,
        location: str | None = None,
        capacity: int | None = None,
    ) -> List[Resource]:
        from sqlalchemy import text
        query = "SELECT * FROM resources WHERE status = 'published'"
        params = {}
        
        if search_term:
            query += " AND (title LIKE :search_term OR description LIKE :search_term)"
            params['search_term'] = f"%{search_term}%"
        
        if category:
            query += " AND category = :category"
            params['category'] = category
        
        if location:
            query += " AND location = :location"
            params['location'] = location
        
        if capacity is not None:
            query += " AND capacity >= :capacity"
            params['capacity'] = capacity
        
        query += " ORDER BY created_at DESC"
        
        result = self.db_session.execute(text(query), params)
        resources = []
        for row in result:
            resources.append(Resource(
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
            ))
        return resources

    def update_resource(self, resource_id: int, data: dict) -> Resource | None:
        resource = self.get_resource_by_id(resource_id)
        if not resource:
            return None

        for field, value in data.items():
            if hasattr(resource, field) and value is not None:
                setattr(resource, field, value)

        self.db_session.commit()
        self.db_session.refresh(resource)  # Refresh to ensure object is properly bound
        return resource

    def delete_resource(self, resource_id: int) -> bool:
        resource = self.get_resource_by_id(resource_id)
        if not resource:
            return False

        try:
            # Ensure resource is bound to session before deletion
            if resource not in self.db_session:
                self.db_session.merge(resource)
            self.db_session.delete(resource)
            self.db_session.commit()
            return True
        except SQLAlchemyError:
            self.db_session.rollback()
            return False


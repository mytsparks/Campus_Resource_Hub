from __future__ import annotations

from typing import List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import Review


class ReviewDAL:
    """Encapsulates all database interactions for the Review model."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_review(
        self,
        resource_id: int,
        reviewer_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        review = Review(
            resource_id=resource_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment,
        )

        try:
            self.db_session.add(review)
            self.db_session.commit()
            return review
        except SQLAlchemyError:
            self.db_session.rollback()
            raise

    def get_reviews_for_resource(self, resource_id: int) -> List[Review]:
        result = self.db_session.execute(
            text("SELECT * FROM reviews WHERE resource_id = :resource_id ORDER BY timestamp DESC"),
            {"resource_id": resource_id}
        )
        reviews = []
        for row in result:
            reviews.append(Review(
                review_id=row[0],
                resource_id=row[1],
                reviewer_id=row[2],
                rating=row[3],
                comment=row[4],
                timestamp=row[5],
            ))
        return reviews

    def get_resource_rating_stats(self, resource_id: int) -> dict:
        """Get aggregate rating statistics for a resource."""
        result = self.db_session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as avg_rating,
                    MIN(rating) as min_rating,
                    MAX(rating) as max_rating
                FROM reviews
                WHERE resource_id = :resource_id
            """),
            {"resource_id": resource_id}
        )
        row = result.fetchone()
        if row and row[0]:
            return {
                'total_reviews': row[0],
                'avg_rating': round(float(row[1] or 0), 1),
                'min_rating': row[2] or 0,
                'max_rating': row[3] or 0,
            }
        return {'total_reviews': 0, 'avg_rating': 0.0, 'min_rating': 0, 'max_rating': 0}

    def get_review_by_id(self, review_id: int) -> Review | None:
        """Get a review by its ID."""
        result = self.db_session.execute(
            text("SELECT * FROM reviews WHERE review_id = :review_id"),
            {"review_id": review_id}
        )
        row = result.fetchone()
        if row:
            return Review(
                review_id=row[0],
                resource_id=row[1],
                reviewer_id=row[2],
                rating=row[3],
                comment=row[4],
                timestamp=row[5],
            )
        return None

    def update_review(self, review_id: int, rating: int | None = None, comment: str | None = None) -> Review | None:
        """Update a review (admin can edit any review)."""
        review = self.get_review_by_id(review_id)
        if not review:
            return None
        
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        
        try:
            self.db_session.commit()
            self.db_session.refresh(review)
            return review
        except SQLAlchemyError:
            self.db_session.rollback()
            return None

    def delete_review(self, review_id: int) -> bool:
        """Delete a review (admin can delete any review)."""
        review = self.get_review_by_id(review_id)
        if not review:
            return False
        
        try:
            self.db_session.delete(review)
            self.db_session.commit()
            return True
        except SQLAlchemyError:
            self.db_session.rollback()
            return False


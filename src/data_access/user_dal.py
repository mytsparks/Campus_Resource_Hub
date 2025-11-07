from __future__ import annotations

from flask_bcrypt import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import User


class UserDAL:
    """Encapsulates all database interactions for the User model."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.generate_password_hash = generate_password_hash
        self.check_password_hash = check_password_hash

    def create_user(
        self,
        name: str,
        email: str,
        plaintext_password: str,
        role: str,
    ) -> User | None:
        email = email.strip().lower()
        hashed_password = self.generate_password_hash(plaintext_password)
        if isinstance(hashed_password, bytes):
            hashed_password = hashed_password.decode('utf-8')

        if self.get_user_by_email(email):
            return None

        user = User(
            name=name.strip(),
            email=email,
            password_hash=hashed_password,
            role=role,
        )

        try:
            self.db_session.add(user)
            self.db_session.commit()
            return user
        except IntegrityError:
            self.db_session.rollback()
            return None
        except Exception:
            self.db_session.rollback()
            raise

    def get_user_by_email(self, email: str) -> User | None:
        # Use text() for raw SQL as fallback, or ensure proper session configuration
        from sqlalchemy import text
        result = self.db_session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.fetchone()
        if row:
            # Map row to User object
            return User(
                user_id=row[0],
                name=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                profile_image=row[5] if len(row) > 5 else None,
                department=row[6] if len(row) > 6 else None,
                created_at=row[7] if len(row) > 7 else None,
            )
        return None

    def get_user_by_name(self, name: str) -> User | None:
        from sqlalchemy import text
        result = self.db_session.execute(
            text("SELECT * FROM users WHERE name = :name"),
            {"name": name}
        )
        row = result.fetchone()
        if row:
            return User(
                user_id=row[0],
                name=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                profile_image=row[5] if len(row) > 5 else None,
                department=row[6] if len(row) > 6 else None,
                created_at=row[7] if len(row) > 7 else None,
            )
        return None

    def get_user_by_id(self, user_id: int) -> User | None:
        from sqlalchemy import text
        result = self.db_session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.fetchone()
        if row:
            return User(
                user_id=row[0],
                name=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                profile_image=row[5] if len(row) > 5 else None,
                department=row[6] if len(row) > 6 else None,
                created_at=row[7] if len(row) > 7 else None,
            )
        return None

    def verify_user_credentials(
        self,
        identifier: str,
        plaintext_password: str,
    ) -> User | None:
        identifier_normalized = identifier.strip().lower()

        user = self.get_user_by_email(identifier_normalized)
        if not user:
            user = self.get_user_by_name(identifier.strip())
        if not user:
            return None

        if self.check_password_hash(user.password_hash, plaintext_password):
            return user

        return None


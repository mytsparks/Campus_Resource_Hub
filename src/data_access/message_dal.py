from __future__ import annotations

from typing import List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import Message, User


class MessageDAL:
    """Encapsulates all database interactions for the Message model."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_message(
        self,
        sender_id: int,
        receiver_id: int,
        content: str,
        thread_id: int | None = None,
    ) -> Message:
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            thread_id=thread_id,
        )

        self.db_session.add(message)
        self.db_session.commit()
        return message

    def get_thread_messages(self, thread_id: int) -> List[Message]:
        result = self.db_session.execute(
            text("SELECT * FROM messages WHERE thread_id = :thread_id ORDER BY timestamp ASC"),
            {"thread_id": thread_id}
        )
        messages = []
        for row in result:
            messages.append(Message(
                message_id=row[0],
                thread_id=row[1],
                sender_id=row[2],
                receiver_id=row[3],
                content=row[4],
                timestamp=row[5],
            ))
        return messages

    def get_user_conversations(self, user_id: int) -> List[dict]:
        """Get all conversation threads for a user."""
        result = self.db_session.execute(
            text("""
                SELECT DISTINCT thread_id, 
                       CASE WHEN sender_id = :user_id THEN receiver_id ELSE sender_id END as other_user_id,
                       MAX(timestamp) as last_message_time
                FROM messages
                WHERE sender_id = :user_id OR receiver_id = :user_id
                GROUP BY thread_id, other_user_id
                ORDER BY last_message_time DESC
            """),
            {"user_id": user_id}
        )
        return [dict(row._mapping) for row in result]


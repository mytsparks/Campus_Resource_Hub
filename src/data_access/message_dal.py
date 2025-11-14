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
        """Get all conversation threads for a user with other user's name."""
        result = self.db_session.execute(
            text("""
                SELECT DISTINCT 
                    m.thread_id, 
                    CASE WHEN m.sender_id = :user_id THEN m.receiver_id ELSE m.sender_id END as other_user_id,
                    MAX(m.timestamp) as last_message_time,
                    u.name as other_user_name
                FROM messages m
                LEFT JOIN users u ON (CASE WHEN m.sender_id = :user_id THEN m.receiver_id ELSE m.sender_id END = u.user_id)
                WHERE m.sender_id = :user_id OR m.receiver_id = :user_id
                GROUP BY m.thread_id, other_user_id, u.name
                ORDER BY last_message_time DESC
            """),
            {"user_id": user_id}
        )
        return [dict(row._mapping) for row in result]
    
    def find_or_create_thread(self, user1_id: int, user2_id: int) -> int:
        """Find existing thread between two users or create a new one."""
        # First, try to find an existing thread
        result = self.db_session.execute(
            text("""
                SELECT DISTINCT thread_id
                FROM messages
                WHERE (sender_id = :user1_id AND receiver_id = :user2_id)
                   OR (sender_id = :user2_id AND receiver_id = :user1_id)
                LIMIT 1
            """),
            {"user1_id": user1_id, "user2_id": user2_id}
        )
        row = result.fetchone()
        if row and row[0]:
            return row[0]
        
        # No existing thread, create a new one by generating a unique thread_id
        # Use max thread_id + 1, or use a combination of user IDs
        max_thread_result = self.db_session.execute(
            text("SELECT COALESCE(MAX(thread_id), 0) FROM messages")
        )
        max_thread = max_thread_result.scalar() or 0
        new_thread_id = max_thread + 1
        return new_thread_id


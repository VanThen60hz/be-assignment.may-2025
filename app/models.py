# SQLAlchemy or Tortoise models

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sent_messages = relationship("Message", back_populates="sender")
    received_messages = relationship(
        "MessageRecipient", back_populates="recipient")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String, nullable=True)
    content = Column(Text)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sender = relationship("User", back_populates="sent_messages")
    recipients = relationship("MessageRecipient", back_populates="message")


class MessageRecipient(Base):
    __tablename__ = "message_recipients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="recipients")
    recipient = relationship("User", back_populates="received_messages")

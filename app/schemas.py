# Pydantic models

from pydantic import BaseModel, EmailStr, UUID4, ConfigDict
from typing import Optional, List
from datetime import datetime

# User schemas


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID4
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Message schemas


class MessageBase(BaseModel):
    subject: Optional[str] = None
    content: str


class MessageCreate(MessageBase):
    recipient_ids: List[UUID4]
    sender_id: UUID4


class Message(MessageBase):
    id: UUID4
    sender_id: UUID4
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

# Message with recipients


class MessageWithRecipients(Message):
    recipients: List[User]
    model_config = ConfigDict(from_attributes=True)

# Message recipient schemas


class MessageRecipientBase(BaseModel):
    message_id: UUID4
    recipient_id: UUID4
    read: bool = False
    read_at: Optional[datetime] = None


class MessageRecipient(MessageRecipientBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)

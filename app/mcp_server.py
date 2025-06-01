# MCP server integration
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any
import uuid
from . import models, schemas
from .db import get_db
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("messaging")

# Create FastAPI app for MCP
app = FastAPI(title="Messaging System MCP Server")

# Pydantic models


class UserCreate(BaseModel):
    email: str
    name: str


class MessageCreate(BaseModel):
    sender_id: str
    recipient_ids: List[str]
    subject: str
    content: str


class MessageRead(BaseModel):
    message_id: str
    user_id: str

# MCP Tools


@mcp.tool()
async def create_user(email: str, name: str) -> dict:
    """Create a new user in the messaging system"""
    db = next(get_db())
    try:
        db_user = models.User(email=email, name=name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"id": str(db_user.id), "email": db_user.email, "name": db_user.name}
    except IntegrityError:
        db.rollback()
        existing_user = db.query(models.User).filter(
            models.User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with email {email} already exists"
            )
        raise HTTPException(status_code=400, detail="Failed to create user")


@mcp.tool()
async def send_message(sender_id: str, recipient_ids: List[str], content: str, subject: str = "") -> dict:
    """Send a message to one or more recipients"""
    db = next(get_db())
    try:
        db_message = models.Message(
            sender_id=uuid.UUID(sender_id),
            subject=subject,
            content=content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        for recipient_id in recipient_ids:
            recipient = models.MessageRecipient(
                message_id=db_message.id,
                recipient_id=uuid.UUID(recipient_id)
            )
            db.add(recipient)

        db.commit()
        return {"message_id": str(db_message.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@mcp.tool()
async def get_messages(user_id: str) -> List[dict]:
    """Get all messages for a user"""
    db = next(get_db())
    messages = (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(models.MessageRecipient.recipient_id == uuid.UUID(user_id))
        .all()
    )
    return [
        {
            "id": str(msg.id),
            "subject": msg.subject,
            "content": msg.content,
            "sender_id": str(msg.sender_id),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]


@mcp.tool()
async def mark_message_read(message_id: str, user_id: str) -> dict:
    """Mark a message as read"""
    db = next(get_db())
    recipient = (
        db.query(models.MessageRecipient)
        .filter(
            models.MessageRecipient.message_id == uuid.UUID(message_id),
            models.MessageRecipient.recipient_id == uuid.UUID(user_id)
        )
        .first()
    )
    if not recipient:
        raise HTTPException(
            status_code=404, detail="Message recipient not found")

    recipient.read = True
    recipient.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "success"}


@mcp.tool()
async def get_unread_messages(user_id: str) -> List[dict]:
    """Get all unread messages for a user"""
    db = next(get_db())
    messages = (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(
            models.MessageRecipient.recipient_id == uuid.UUID(user_id),
            models.MessageRecipient.read == False
        )
        .all()
    )
    return [
        {
            "id": str(msg.id),
            "subject": msg.subject,
            "content": msg.content,
            "sender_id": str(msg.sender_id),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]


@mcp.tool()
async def get_sent_messages(user_id: str) -> List[dict]:
    """Get all messages sent by a user"""
    db = next(get_db())
    messages = (
        db.query(models.Message)
        .filter(models.Message.sender_id == uuid.UUID(user_id))
        .all()
    )
    return [
        {
            "id": str(msg.id),
            "subject": msg.subject,
            "content": msg.content,
            "sender_id": str(msg.sender_id),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]


@mcp.tool()
async def get_inbox_messages(user_id: str) -> List[dict]:
    """Get all messages received by a user"""
    db = next(get_db())
    messages = (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(models.MessageRecipient.recipient_id == uuid.UUID(user_id))
        .all()
    )
    return [
        {
            "id": str(msg.id),
            "subject": msg.subject,
            "content": msg.content,
            "sender_id": str(msg.sender_id),
            "timestamp": msg.timestamp.isoformat()
        }
        for msg in messages
    ]

# Mount MCP server to FastAPI app
app.mount("/", mcp)

if __name__ == "__main__":
    # Initialize and run the server with stdio transport
    mcp.run(transport='stdio')

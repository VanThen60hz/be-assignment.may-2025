# Optional MCP server logic

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import uuid
from . import models, schemas
from .db import get_db
from sqlalchemy.orm import Session

app = FastAPI(title="Messaging System MCP Server")


def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@app.post("/mcp/create_user")
async def create_user(email: str, name: str, db: Session = next(get_db_session())):
    """Create a new user"""
    user = models.User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": str(user.id), "email": user.email, "name": user.name}


@app.post("/mcp/send_message")
async def send_message(
    sender_id: str,
    recipient_ids: List[str],
    subject: str,
    content: str,
    db: Session = next(get_db_session())
):
    """Send a message to multiple recipients"""
    try:
        message = models.Message(
            sender_id=uuid.UUID(sender_id),
            subject=subject,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        for recipient_id in recipient_ids:
            recipient = models.MessageRecipient(
                message_id=message.id,
                recipient_id=uuid.UUID(recipient_id)
            )
            db.add(recipient)

        db.commit()
        return {"message_id": str(message.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mcp/get_messages/{user_id}")
async def get_messages(user_id: str, db: Session = next(get_db_session())):
    """Get all messages for a user"""
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

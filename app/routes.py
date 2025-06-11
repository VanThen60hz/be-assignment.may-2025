# FastAPI routes

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone
import uuid

from . import models, schemas
from .db import get_db

router = APIRouter()

# User routes


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        email=user.email,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Message routes


@router.post("/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # Create message
    db_message = models.Message(
        subject=message.subject,
        content=message.content,
        sender_id=message.sender_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Create message recipients
    for recipient_id in message.recipient_ids:
        recipient = models.MessageRecipient(
            message_id=db_message.id,
            recipient_id=recipient_id
        )
        db.add(recipient)

    db.commit()
    return db_message


@router.get("/messages/sent/{user_id}", response_model=List[schemas.Message])
def get_sent_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(models.Message).filter(models.Message.sender_id == user_id).all()


@router.get("/messages/inbox/{user_id}", response_model=List[schemas.Message])
def get_inbox_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(models.MessageRecipient.recipient_id == user_id)
        .all()
    )


@router.get("/messages/unread/{user_id}", response_model=List[schemas.Message])
def get_unread_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return (
        db.query(models.Message)
        .join(models.MessageRecipient)
        .filter(
            models.MessageRecipient.recipient_id == user_id,
            models.MessageRecipient.read == False
        )
        .all()
    )


@router.get("/messages/{message_id}", response_model=schemas.Message)
def get_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    message = (
        db.query(models.Message)
        .filter(models.Message.id == message_id)
        .first()
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.post("/messages/{message_id}/read/{user_id}")
def mark_message_as_read(message_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    recipient = (
        db.query(models.MessageRecipient)
        .filter(
            models.MessageRecipient.message_id == message_id,
            models.MessageRecipient.recipient_id == user_id
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

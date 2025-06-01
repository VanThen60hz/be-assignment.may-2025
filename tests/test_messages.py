# Test message-related functionality

from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_send_message():
    # Create sender
    sender_response = client.post(
        "/api/v1/users/",
        json={"email": "sender@example.com", "name": "Sender"}
    )
    sender_id = sender_response.json()["id"]

    # Create recipient
    recipient_response = client.post(
        "/api/v1/users/",
        json={"email": "recipient@example.com", "name": "Recipient"}
    )
    recipient_id = recipient_response.json()["id"]

    # Send message
    response = client.post(
        "/api/v1/messages/",
        json={
            "subject": "Test Subject",
            "content": "Test Content",
            "sender_id": sender_id,
            "recipient_ids": [recipient_id]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["sender_id"] == sender_id


def test_get_inbox():
    # Create sender and recipient
    sender_response = client.post(
        "/api/v1/users/",
        json={"email": "sender2@example.com", "name": "Sender 2"}
    )
    sender_id = sender_response.json()["id"]

    recipient_response = client.post(
        "/api/v1/users/",
        json={"email": "recipient2@example.com", "name": "Recipient 2"}
    )
    recipient_id = recipient_response.json()["id"]

    # Send message
    client.post(
        "/api/v1/messages/",
        json={
            "subject": "Inbox Test",
            "content": "Inbox Content",
            "sender_id": sender_id,
            "recipient_ids": [recipient_id]
        }
    )

    # Get inbox
    response = client.get(f"/api/v1/messages/inbox/{recipient_id}")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) > 0
    assert any(m["subject"] == "Inbox Test" for m in messages)


def test_mark_as_read():
    # Create sender and recipient
    sender_response = client.post(
        "/api/v1/users/",
        json={"email": "sender3@example.com", "name": "Sender 3"}
    )
    sender_id = sender_response.json()["id"]

    recipient_response = client.post(
        "/api/v1/users/",
        json={"email": "recipient3@example.com", "name": "Recipient 3"}
    )
    recipient_id = recipient_response.json()["id"]

    # Send message
    message_response = client.post(
        "/api/v1/messages/",
        json={
            "subject": "Read Test",
            "content": "Read Content",
            "sender_id": sender_id,
            "recipient_ids": [recipient_id]
        }
    )
    message_id = message_response.json()["id"]

    # Mark as read
    response = client.post(
        f"/api/v1/messages/{message_id}/read/{recipient_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Check unread messages
    unread_response = client.get(f"/api/v1/messages/unread/{recipient_id}")
    assert unread_response.status_code == 200
    unread_messages = unread_response.json()
    assert not any(m["id"] == message_id for m in unread_messages)

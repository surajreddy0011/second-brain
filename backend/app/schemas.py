"""
schemas.py — defines the shape of data going IN and OUT of our API.

Important distinction from models.py:
- models.py = database tables (what's stored)
- schemas.py = API contracts (what's sent/received over HTTP)

Why separate? Our User table has `hashed_password` — we NEVER want that
in an API response. Pydantic schemas let us control exactly what's
exposed, independent of what's in the database.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional


class UserCreate(BaseModel):
    """What the client sends us on signup."""
    email: EmailStr
    password: str  # plain text here — only for this one request, in transit.
                    # We hash it immediately in the endpoint; it's never stored raw.


class UserOut(BaseModel):
    """What we send back about a user. No password field — impossible to leak it."""
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)  # lets this read directly from a SQLAlchemy model


class Token(BaseModel):
    """What we send back after a successful login."""
    access_token: str
    token_type: str = "bearer"

class NoteCreate(BaseModel):
    """What the client sends us to create a note."""
    title: str
    content: str


class NoteUpdate(BaseModel):
    """Both fields optional — update just the title, just the content, or both."""
    title: Optional[str] = None
    content: Optional[str] = None


class NoteOut(BaseModel):
    """What we send back about a note."""
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
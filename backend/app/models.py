"""
models.py — defines our database tables as Python classes.

Design decisions explained:

1. Users and Notes are a one-to-many relationship: one user has many
   notes. We express that with a foreign key (Note.owner_id points to
   User.id).

2. We store embeddings in their OWN table rather than as a column on
   Note. Why: a single note might get split into multiple "chunks"
   for RAG (long notes need to be broken up so the AI can retrieve
   just the relevant paragraph, not the whole document). So it's really
   a one-to-many: one note -> many embedded chunks.

3. Vector(1536) is the embedding dimension for OpenAI's
   text-embedding-3-small model. This comes from pgvector, a Postgres
   extension that lets the database store and search vectors natively
   (this is what makes "semantic search" possible — finding chunks by
   MEANING, not just keyword match).
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # We NEVER store the raw password. hashed_password holds the output
    # of bcrypt — a one-way hash. Even if the database leaks, the
    # original password can't be recovered from it.
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="notes")
    chunks = relationship("NoteChunk", back_populates="note", cascade="all, delete-orphan")


class NoteChunk(Base):
    """
    A single embedded piece of a note. This is what RAG search actually
    queries against. We'll build the chunking + embedding logic on
    Days 7-8 — for now we just define where it lives.
    """
    __tablename__ = "note_chunks"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # nullable until Day 7-8

    note = relationship("Note", back_populates="chunks")

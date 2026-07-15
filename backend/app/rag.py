"""
rag.py — the actual AI logic: chunking text, generating embeddings,
and asking the chat model to answer using retrieved context.
"""

import os
from datetime import date
from typing import List

from openai import OpenAI
from sqlalchemy.orm import Session

from . import models

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def index_note(note: models.Note, db: Session) -> None:
    db.query(models.NoteChunk).filter(models.NoteChunk.note_id == note.id).delete()
    for chunk in chunk_text(note.content):
        embedding = get_embedding(chunk)
        db.add(models.NoteChunk(note_id=note.id, chunk_text=chunk, embedding=embedding))
    db.commit()


def retrieve_relevant_chunks(question: str, user_id: int, db: Session, top_k: int = 5):
    question_embedding = get_embedding(question)
    return (
        db.query(models.NoteChunk)
        .join(models.Note)
        .filter(models.Note.owner_id == user_id)
        .order_by(models.NoteChunk.embedding.cosine_distance(question_embedding))
        .limit(top_k)
        .all()
    )


def generate_answer(question: str, context: str, history: list) -> str:
    """
    Asks the chat model to answer using retrieved note chunks as context
    AND recent conversation history — the history is what lets follow-up
    questions like "what date" resolve to whatever was being discussed,
    instead of being treated as a brand-new, context-free question.
    """
    today_str = date.today().strftime("%B %d, %Y")
    system_prompt = (
        f"Today's date is {today_str}. You are a helpful assistant that answers "
        "questions using ONLY the provided notes as context. If the answer isn't "
        "contained in the notes, say so honestly instead of guessing. Use the "
        "conversation history to understand follow-up questions, but still "
        "ground every factual answer in the notes provided. Each note below is "
        "labeled with the date it was written — when a note uses a relative "
        "date like 'tomorrow' or 'next week', calculate the actual date based "
        "on THAT note's written date, not today's date, unless the question "
        "explicitly asks about 'today' or 'now'."
    )
    """
    Asks the chat model to answer using retrieved note chunks as context
    AND recent conversation history — the history is what lets follow-up
    questions like "what date" resolve to whatever was being discussed,
    instead of being treated as a brand-new, context-free question.
    """
    system_prompt = (
        "You are a helpful assistant that answers questions using ONLY "
        "the provided notes as context. If the answer isn't contained in "
        "the notes, say so honestly instead of guessing. Use the "
        "conversation history to understand follow-up questions, but "
        "still ground every factual answer in the notes provided."
    )

    messages = [{"role": "system", "content": system_prompt}]
    # Only the last 6 turns (3 exchanges) — enough for context, not so
    # much it balloons cost or confuses the model with old topics.
    for turn in history[-6:]:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": f"Notes:\n{context}\n\nQuestion: {question}"})

    response = client.chat.completions.create(model=CHAT_MODEL, messages=messages)
    return response.choices[0].message.content


def answer_question(question: str, user_id: int, db: Session, history: list = None) -> dict:
    """The full ask pipeline: retrieve relevant chunks, then generate an answer from them."""
    history = history or []
    chunks = retrieve_relevant_chunks(question, user_id, db)

    if not chunks:
        return {
            "answer": "You don't have any notes yet — add some first so I have something to search.",
            "sources": [],
        }

    
    context = "\n\n---\n\n".join(
        f"[Note '{c.note.title}', written on {c.note.created_at.strftime('%B %d, %Y')}]\n{c.chunk_text}"
        for c in chunks
    )
    answer = generate_answer(question, context, history)
    sources = sorted({c.note.title for c in chunks})

    return {"answer": answer, "sources": sources}
    chunks = retrieve_relevant_chunks(question, user_id, db)
    if not chunks:
        return {
            "answer": "You don't have any notes yet — add some first so I have something to search.",
            "sources": [],
        }
    context = "\n\n---\n\n".join(c.chunk_text for c in chunks)
    answer = generate_answer(question, context)
    sources = sorted({c.note.title for c in chunks})
    return {"answer": answer, "sources": sources}
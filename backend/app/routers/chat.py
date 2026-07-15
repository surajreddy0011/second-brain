"""
routers/chat.py — the endpoint that ties RAG together for the user.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, auth, rag, models
from ..database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatResponse)
def chat(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return rag.answer_question(request.question, current_user.id, db)
"""
routers/notes.py — create, read, update, delete notes.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from .. import models, schemas, auth, rag

router = APIRouter(prefix="/notes", tags=["notes"])


def get_owned_note(note_id: int, db: Session, current_user: models.User) -> models.Note:
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note or note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    note = models.Note(title=note_in.title, content=note_in.content, owner_id=current_user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    rag.index_note(note, db)  # chunk + embed immediately so it's searchable right away
    return note


@router.get("", response_model=List[schemas.NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Note)
        .filter(models.Note.owner_id == current_user.id)
        .order_by(models.Note.created_at.desc())
        .all()
    )


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return get_owned_note(note_id, db, current_user)


@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    note_in: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    note = get_owned_note(note_id, db, current_user)
    if note_in.title is not None:
        note.title = note_in.title
    if note_in.content is not None:
        note.content = note_in.content
    db.commit()
    db.refresh(note)
    if note_in.content is not None:
        rag.index_note(note, db)  # content changed — re-embed so search stays accurate
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    note = get_owned_note(note_id, db, current_user)
    db.delete(note)
    db.commit()
    return None
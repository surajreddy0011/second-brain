"""
main.py — the entrypoint. This is what you run to start the server.

Today (Day 1) this file does two things:
1. Creates the database tables from our models, if they don't exist yet.
2. Exposes one "health check" endpoint so we can confirm the server
   and database are both alive before building anything more complex.

Auth endpoints (Day 3-4) and notes CRUD endpoints (Day 5-6) will get
added as separate "routers" that we include here — that's the standard
FastAPI pattern for keeping a growing app organized instead of dumping
everything into one file.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import engine, Base, get_db
from . import models  # noqa: F401 — importing registers the models with Base
from .routers import auth as auth_router
from .routers import notes as notes_router
from .routers import chat as chat_router

app = FastAPI(title="Second Brain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The pgvector extension has to be turned on per-database — it's installed
# on the Postgres server, but not active in "second_brain" until we say so.
# Doing it here means it happens automatically every time the app starts,
# so nobody ever has to run this by hand.
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# On startup, create any tables that don't exist yet. In a real production
# app you'd use a migration tool (Alembic) instead of this, so you can
# version-control schema changes — we'll add that once the schema stabilizes.
Base.metadata.create_all(bind=engine)
app.include_router(auth_router.router)
app.include_router(notes_router.router)
app.include_router(chat_router.router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Hits the database with a trivial query (SELECT 1) to prove the
    whole chain works: server is running -> database connection is
    live -> query executes. This is the first thing to check whenever
    something breaks later.
    """
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}

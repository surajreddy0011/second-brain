"""
database.py — sets up the connection to PostgreSQL.

This file has exactly one job: create a way for the rest of the app
to talk to the database, without every file needing to know connection
details (host, password, etc).

Key concept: SQLAlchemy is an ORM (Object-Relational Mapper). It lets us
write Python classes (see models.py) instead of raw SQL strings, and it
translates our Python code into SQL under the hood.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()   # reads backend/.env and loads it into the environment

# The connection string format is:
# postgresql://<user>:<password>@<host>:<port>/<database_name>
# We read it from an environment variable so we NEVER hardcode secrets
# in code that might end up on GitHub.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5544/second_brain",
)

# The "engine" manages the actual connection pool to Postgres.
engine = create_engine(DATABASE_URL)

# A "session" is a single conversation with the database — think of it
# as a workspace where you stage changes (add a note, update a note)
# before committing them, similar to git add + git commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class every database model (table) will inherit from.
# SQLAlchemy uses this to know which Python classes map to which tables.
Base = declarative_base()


def get_db():
    """
    This is a FastAPI "dependency". Every endpoint that needs database
    access will call this function to get a session, and FastAPI
    guarantees the session is closed afterward — even if the request
    fails. This pattern prevents connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Second Brain — Day 1: Setup + Data Model

## What exists so far
- `backend/app/database.py` — connects to Postgres via SQLAlchemy
- `backend/app/models.py` — three tables: `users`, `notes`, `note_chunks`
- `backend/app/main.py` — FastAPI app with a `/health` endpoint
- `docker-compose.yml` — runs Postgres (with pgvector) locally in a container

## Run it yourself

You'll need: Python 3.11+, Docker Desktop installed and running.

```bash
# 1. Start the database
docker compose up -d

# 2. Set up the backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up your environment file
cp .env.example .env
# (defaults work as-is for local dev, no editing needed yet)

# 4. Run the server
uvicorn app.main:app --reload
```

Now open **http://localhost:8000/health** in your browser.
You should see: `{"status":"ok","database":"connected"}`

If you see that, your entire chain works: FastAPI server → SQLAlchemy →
Postgres → pgvector extension, all talking to each other correctly.

Also check **http://localhost:8000/docs** — FastAPI auto-generates
interactive API documentation from your code. This becomes very useful
once we add real endpoints on Day 5-6.

## Troubleshooting
- `connection refused` on `/health` → is `docker compose up -d` still running? Check with `docker ps`.
- `password authentication failed` → delete the Docker volume and restart: `docker compose down -v && docker compose up -d`
- `ModuleNotFoundError` → did you activate the venv before `pip install`?

## Why these 3 tables and not fewer?
- `users` / `notes`: standard one-to-many — one user owns many notes.
- `note_chunks`: separated from `notes` on purpose. A long note gets
  split into smaller chunks later (Day 7-8) so the RAG chatbot can
  retrieve just the relevant paragraph instead of dumping your entire
  note history into every AI prompt (which would be slow and expensive).

## Next: Day 3-4 — Authentication
We'll add password hashing, JWT token issuing, and login/signup
endpoints — and importantly, *why* each piece exists, not just the code
to make it work.

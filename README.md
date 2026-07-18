# Second Brain

A full-stack, AI-powered personal knowledge base. Write notes, then ask questions about them in natural language — the app retrieves relevant notes by *meaning* (not keyword matching) and generates grounded answers using retrieval-augmented generation (RAG).

Built end-to-end to develop hands-on depth in backend architecture, authentication, applied AI, and cloud deployment — every feature was built, debugged, and deployed personally rather than scaffolded from a template.

## What it does

- Create, edit, and delete notes through a clean web UI
- Ask questions about your notes in a chat interface
- Answers are grounded only in your own notes (with source attribution), and the assistant says when it doesn't know instead of guessing
- Follow-up questions work naturally — the chat retains conversation context
- Notes with relative dates ("renew by tomorrow") are reasoned about relative to when the note was written, not when the question is asked

## Architecture

```
Browser
  │
  ├──►  React (TypeScript) frontend  ──  hosted on AWS S3
  │
  └──►  FastAPI backend  ──  deployed on AWS Elastic Beanstalk (EC2)
              │
              └──►  PostgreSQL + pgvector  ──  AWS RDS
              │
              └──►  OpenAI API  (embeddings + chat completions)
```

**Write path:** a note is saved → split into overlapping chunks → each chunk embedded (`text-embedding-3-small`) → stored as a vector in Postgres via `pgvector`.

**Ask path:** the question is embedded the same way → Postgres finds the closest chunks by cosine similarity, scoped to the logged-in user → the top matches plus recent chat history are sent to `gpt-4o-mini` to generate a grounded answer.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | FastAPI (Python), SQLAlchemy |
| Database | PostgreSQL + pgvector extension |
| Auth | JWT (python-jose), bcrypt password hashing |
| AI | OpenAI embeddings + chat completions (RAG) |
| Cloud | AWS Elastic Beanstalk (EC2), RDS, S3 |
| Local dev | Docker (Postgres + pgvector) |

## Key implementation details

- **Real authentication** — passwords are bcrypt-hashed, never stored or logged in plaintext; JWTs are verified on every protected request via a FastAPI dependency.
- **Ownership-scoped access control** — every notes/chat query is filtered by the authenticated user's ID at the database level. Requesting another user's note by ID returns 404, not their data.
- **RAG grounding** — the system prompt constrains the model to answer only from retrieved notes and to admit when information is absent, rather than hallucinating a plausible answer.
- **Conversation-aware retrieval** — recent chat history is passed to the model so follow-ups ("what date?") resolve correctly instead of being treated as isolated queries.
- **Deployed to AWS** — backend on Elastic Beanstalk, managed Postgres on RDS with pgvector enabled, static frontend on S3, with security groups locking database access to the application tier.

## Running it locally

Requires Docker, Python 3.9+, and Node 18+.

```bash
# 1. Start Postgres (with pgvector)
docker compose up -d

# 2. Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in OPENAI_API_KEY and JWT_SECRET_KEY
uvicorn app.main:app --reload

# 3. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Backend runs at `localhost:8000` (interactive API docs at `/docs`), frontend at `localhost:5173`.

## API overview

| Endpoint | Description |
|---|---|
| `POST /auth/signup` | Create an account |
| `POST /auth/login` | Log in, receive a JWT |
| `GET /auth/me` | Get the current authenticated user |
| `GET /notes` / `POST /notes` | List / create notes |
| `GET /notes/{id}` / `PUT /notes/{id}` / `DELETE /notes/{id}` | Manage a single note |
| `POST /chat` | Ask a question, get a RAG-grounded answer with sources |

## Deployment notes

The backend is packaged for Elastic Beanstalk (`Procfile` + `.ebextensions`), configured to run under uvicorn. Secrets (database URL, OpenAI key, JWT secret) are injected as environment variables rather than committed to source. The RDS instance runs single-AZ on a burstable instance class to stay within a small budget; the pgvector extension is enabled on first boot.

> Live AWS resources for this project are spun down between demos to control cost. The full stack redeploys from this repo via the Elastic Beanstalk CLI plus an RDS instance.

## Roadmap

- [ ] HTTPS + CDN via CloudFront
- [ ] CI/CD via GitHub Actions
- [ ] Similarity-threshold filtering on retrieval (currently always returns top-k)
- [ ] Persist chat history server-side (currently per-session)
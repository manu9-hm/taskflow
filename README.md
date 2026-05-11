# TaskFlow

> Smart task management with AI-powered semantic search, built with FastAPI + React + pgvector.

![CI](https://github.com/YOUR_USERNAME/taskflow/actions/workflows/ci.yml/badge.svg)

## Features

- **JWT Authentication** — secure register / login flow
- **Full CRUD** — create, update, delete tasks with priority, status, tags, due dates
- **Semantic Search** — natural-language search powered by `sentence-transformers` + pgvector cosine similarity
- **Production-ready** — Dockerized, CI/CD via GitHub Actions, parameterized SQL queries, env-based secrets

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL + pgvector extension |
| AI Search | sentence-transformers (`all-MiniLM-L6-v2`) |
| Auth | JWT (python-jose), bcrypt |
| Frontend | React 18, Vite, TailwindCSS |
| DevOps | Docker, GitHub Actions |

## Project Structure

```
taskflow/
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings from env vars (pydantic-settings)
│   │   ├── database.py        # Async SQLAlchemy engine
│   │   ├── main.py            # FastAPI app + lifespan
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── routers/           # auth + tasks endpoints
│   │   └── utils/             # JWT utils, embedding generator
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios instance with interceptors
│   │   ├── context/           # AuthContext (JWT management)
│   │   ├── pages/             # Login, Register, Dashboard
│   │   └── components/        # Navbar, TaskCard, TaskModal
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
└── .env.example
```

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/taskflow.git
cd taskflow

# 2. Set up environment
cp .env.example .env
# Edit .env — fill in DB_PASSWORD and SECRET_KEY

# 3. Start everything
docker compose up --build

# App is now at http://localhost
# API docs at http://localhost:8000/api/docs
```

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create a .env in the backend/ folder (copy from root .env.example)
# Make sure PostgreSQL + pgvector is running locally

uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # Starts at http://localhost:5173
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/tasks/` | List tasks (filter by status/priority) |
| POST | `/api/tasks/` | Create task |
| PATCH | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| POST | `/api/tasks/search` | **Semantic search** |

Interactive docs: `http://localhost:8000/api/docs`

## Security Highlights

- Secrets loaded from environment variables (never hardcoded)
- Passwords hashed with bcrypt
- Parameterized SQL queries via SQLAlchemy ORM (no SQL injection)
- JWT expiry + ownership checks on every task operation
- CORS restricted to configured origins

## Deployment (Render)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com) pointing to `backend/`
3. Add environment variables from `.env.example`
4. Create a **PostgreSQL** database on Render, enable the `pgvector` extension
5. Create a **Static Site** for the frontend, set build command `npm run build`, publish dir `dist`

## Resume Bullet Points

**SWE Resume:**
> Built and deployed a full-stack task manager with JWT auth, async REST APIs (FastAPI), PostgreSQL, CI/CD via GitHub Actions, and Docker

**AI Resume:**
> Implemented natural-language semantic search using sentence-transformers + pgvector, with background embedding indexing and cosine similarity ranking

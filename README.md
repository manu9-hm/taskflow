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

## Architecture & flow diagrams

High-level views of how the repo fits together: runtime topology, code layout, request paths, and automation. GitHub renders these Mermaid diagrams in the README.

### 1. Runtime topology (Docker Compose — production-style)

```mermaid
flowchart TB
  subgraph Client["Client"]
    U[User / Browser]
  end

  subgraph Host["Docker host"]
    subgraph FE["frontend container — nginx:alpine"]
      NG[nginx :80]
      SPA[Static React build]
      NG --> SPA
      NG -->|"/api/*" proxy| FA
    end

    subgraph API["backend container — uvicorn :8000"]
      FA[FastAPI app.main]
      FA --> R_AUTH[routers/auth]
      FA --> R_TASK[routers/tasks]
      R_AUTH --> ORM[(SQLAlchemy async)]
      R_TASK --> ORM
      R_TASK --> EMB[utils/embeddings\nsentence-transformers]
      EMB --> VOL[(Volume embedding_models\n/models cache)]
    end

    subgraph DB["db container — pgvector/pgvector:pg16"]
      PG[(PostgreSQL + vector ext)]
    end

    ORM --> PG
  end

  U -->|HTTP :80| NG
  U -.->|optional direct API| FA
```

### 2. Local development vs Docker (two ways to run)

```mermaid
flowchart LR
  subgraph Dev["Local dev"]
    V[Vite :5173\nfrontend]
    UV[uvicorn :8000\nbackend]
    V -->|proxy /api| UV
    PGD[(Postgres + pgvector\nlocalhost)]
    UV --> PGD
  end

  subgraph DC["docker-compose.yml"]
    FED[nginx + SPA]
    BED[FastAPI]
    DBD[(pgvector image)]
    FED --> BED
    BED --> DBD
  end

  subgraph GHCR["docker-compose.ghcr.yml"]
    FEG[image ghcr.io/.../taskflow-frontend]
    BEG[image ghcr.io/.../taskflow-backend]
    DBG[(pgvector image)]
    FEG --> BEG
    BEG --> DBG
  end
```

### 3. Repository layout (how folders connect)

```mermaid
flowchart TB
  subgraph Root["Repository root"]
    ENV[".env.example\nCR_OWNER, DB_PASSWORD, SECRET_KEY, ..."]
    DC1["docker-compose.yml\nbuild from source"]
    DC2["docker-compose.ghcr.yml\npull from GHCR"]
    GH[".github/workflows/\nci.yml · deploy.yml"]
  end

  subgraph BE["backend/"]
    DF1[Dockerfile]
    REQ[requirements.txt]
    subgraph APP["app/"]
      CFG[config.py]
      DB[database.py]
      MAIN[main.py]
      MOD[models/\nUser, Task + Vector]
      SCH[schemas/\nPydantic DTOs]
      RT[routers/\nauth, tasks]
      UT[utils/\nauth JWT, embeddings]
    end
  end

  subgraph FE2["frontend/"]
    DF2[Dockerfile + nginx.conf]
    PKG[package.json + lockfile]
    subgraph SRC["src/"]
      API2[api/axios.js]
      CTX[context/AuthContext.jsx]
      PG2[pages/\nLogin, Register, Dashboard]
      CMP[components/\nNavbar, TaskCard, TaskModal]
    end
  end

  Root --> BE
  Root --> FE2
  MAIN --> RT
  RT --> MOD
  RT --> SCH
  RT --> UT
  PG2 --> CTX
  PG2 --> API2
  CMP --> PG2
```

### 4. Frontend SPA routing and data flow

```mermaid
flowchart TB
  M[main.jsx\nBrowserRouter + AuthProvider]
  A[App.jsx]
  M --> A

  A -->|"/login"| L[Login.jsx]
  A -->|"/register"| R[Register.jsx]
  A -->|"/" protected| D[Dashboard.jsx]

  L & R --> CTX[AuthContext\nlogin / register / token]
  D --> NAV[Navbar]
  D --> CARDS[TaskCard list]
  D --> MODAL[TaskModal create/edit]
  CTX --> AX[api/axios.js\nBearer JWT + /api proxy]

  AX -->|OAuth2 form| AUTH_EP["POST /api/auth/login"]
  AX -->|JSON| TASK_EP["/api/tasks/*"]
```

### 5. Backend request path (layers)

```mermaid
flowchart LR
  REQ[HTTP request] --> MW[CORS + FastAPI]
  MW --> R{Router}

  R -->|/api/auth/*| RA[auth.py]
  R -->|/api/tasks/*| RT[task.py]

  RA --> SA[schemas/user.py]
  RT --> ST[schemas/task.py]

  RA --> UA[utils/auth.py\nJWT, bcrypt]
  RT --> UA
  RT --> UE[utils/embeddings.py]

  RA --> MU[(models/user)]
  RT --> MT[(models/task)]

  MU & MT --> DBL[database.py\nAsyncSession]
  DBL --> PG[(PostgreSQL\npgvector column)]
  UE --> STF[sentence-transformers\noptional /models cache]
```

### 6. Authentication sequence (register / login / me)

```mermaid
sequenceDiagram
  participant B as Browser
  participant F as FastAPI
  participant DB as PostgreSQL

  Note over B,DB: Register
  B->>F: POST /api/auth/register JSON
  F->>F: hash password bcrypt
  F->>DB: INSERT user ORM
  DB-->>F: user row
  F-->>B: 201 UserOut

  Note over B,DB: Login
  B->>F: POST /api/auth/login form username=email
  F->>DB: SELECT user by email
  DB-->>F: user + hash
  F->>F: verify password
  F-->>B: access_token JWT

  Note over B,DB: Me
  B->>F: GET /api/auth/me Authorization Bearer
  F->>F: decode JWT get_current_user
  F->>DB: load user by id
  F-->>B: UserOut
```

### 7. Task lifecycle, embeddings, and semantic search

```mermaid
sequenceDiagram
  participant B as Browser
  participant F as FastAPI tasks router
  participant DB as PostgreSQL
  participant BG as Background task
  participant ST as sentence-transformers

  Note over B,ST: Create / update task
  B->>F: POST or PATCH /api/tasks
  F->>DB: persist Task row embedding null
  F-->>B: TaskOut
  F->>BG: schedule _index_embedding
  BG->>ST: encode title+description+tags
  ST-->>BG: vector 384-dim
  BG->>DB: UPDATE task.embedding

  Note over B,ST: Semantic search
  B->>F: POST /api/tasks/search query
  F->>ST: encode query
  ST-->>F: query vector
  F->>DB: ORDER BY embedding cosine distance
  DB-->>F: ranked tasks
  F-->>B: list TaskOut

  Note over B,ST: Fallback if model unavailable
  F->>DB: ILIKE title description
  DB-->>F: rows
```

### 8. CI and optional CD (GitHub Actions)

```mermaid
flowchart TB
  PUSH[Push or PR to GitHub]

  PUSH --> CI[Workflow CI]

  subgraph CI["ci.yml"]
    C1[Backend job\nPostgres service + pip + ruff + pytest]
    C2[Frontend job\nNode + npm install + lint + build]
    C3[Docker job on main only\nbuild backend + frontend images no push]
  end

  CI -->|success on main| CD{deploy.yml\noptional}

  subgraph CD["deploy.yml when present"]
    D1[Checkout same SHA as CI run]
    D2[docker buildx push]
    D3[ghcr.io/OWNER/taskflow-backend:latest]
    D4[ghcr.io/OWNER/taskflow-frontend:latest]
    D1 --> D2 --> D3
    D2 --> D4
  end

  D3 & D4 -.->|docker compose pull| VPS[VPS or registry consumer]
```

---

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
├── docker-compose.ghcr.yml   # run pre-built images from GHCR (after Deploy workflow)
├── .github/workflows/ci.yml
├── .github/workflows/deploy.yml
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

The backend image installs PyTorch + `sentence-transformers` at **build** time; model weights download on **first** semantic-search request and are cached in the `embedding_models` volume (`EMBEDDING_CACHE_DIR=/models`). That keeps CI Docker builds within GitHub runner disk limits.

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

## Continuous deployment (CD)

This repo includes **continuous deployment** in two layers:

### 1. Publish containers (GitHub Actions → GHCR)

Workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) runs when:

- **`CI` succeeds on `main`** (via `workflow_run`), or  
- You trigger **Deploy** manually under **Actions → Deploy → Run workflow**.

It builds and pushes:

- `ghcr.io/<your-github-user>/taskflow-backend:latest` (+ SHA tag)
- `ghcr.io/<your-github-user>/taskflow-frontend:latest` (+ SHA tag)

**Make packages readable:** In GitHub → **Packages** → each package → **Package settings** → **Change visibility** (public for a portfolio, or private + `read:packages` PAT on the server).

**First-time setup:** Pushing workflow files needs a PAT with the **`workflow`** scope (or edit/commit the YAML on github.com).

### 2. Run what you published (VPS)

On any Linux host with Docker:

```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME -p YOUR_PAT_WITH_read:packages

cd taskflow
cp .env.example .env
# Set DB_PASSWORD, SECRET_KEY, ALLOWED_ORIGINS, CR_OWNER=<same username, lowercase>

docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d
```

### 3. Managed platforms (alternative)

| Platform | Idea |
|----------|------|
| **Railway / Render / Fly** | Connect the GitHub repo; enable **auto-deploy on push to `main`** (platform builds from `backend/` + `frontend/` Dockerfiles). |
| **GHCR** | Point the service at the images from step 1 instead of rebuilding (fewer surprises vs huge ML deps on small builders). |

Render-style split (Postgres + API + static frontend) still works; ensure Postgres has the **`vector`** extension for semantic search.

## Deployment (Render — manual outline)

1. Push to GitHub  
2. Create a **Web Service** on [render.com](https://render.com) pointing to `backend/`  
3. Add environment variables from `.env.example`  
4. Create **PostgreSQL** with **`pgvector`** enabled  
5. **Static Site** for the frontend: build `npm run build`, publish `dist` (or deploy the frontend Docker image / GHCR image if you prefer one hostname + nginx proxy)

## Resume Bullet Points

**SWE Resume:**
> Built and deployed a full-stack task manager with JWT auth, async REST APIs (FastAPI), PostgreSQL, CI/CD via GitHub Actions, and Docker

**AI Resume:**
> Implemented natural-language semantic search using sentence-transformers + pgvector, with background embedding indexing and cosine similarity ranking

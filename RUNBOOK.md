# Runbook

## Purpose

This runbook documents how to set up, run, and troubleshoot the Geopolitical Intelligence Platform.

## Recommended Architecture

- Backend: `backend/` FastAPI application
- Frontend: `frontend/` React + Vite application
- Database: PostgreSQL (configured via Docker Compose)
- AI/Media Engines: local or cloud AI providers configured through env vars

## Prerequisites

- Python 3.11+
- Node 18+
- Docker & Docker Compose
- Git
- Optional: local GPU support for `sdnext`, `ollama`, and `sadtalker`

## Setup

### 1. Clone repository

```powershell
cd d:\Downloads\geopolitical-intelligence
git clone <repo-url> .
```

### 2. Copy environment files

```powershell
cp .env.example .env
cp backend/.env.example backend/.env
```

Update `.env` and `backend/.env` with your values.

### 3. Start with Docker Compose

```powershell
docker compose up -d --build
```

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost`
- API docs: `http://localhost/api/docs`

### 4. Manual backend setup (optional)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 5. Manual frontend setup (optional)

```powershell
cd frontend
npm install
npm run dev
```

## Environment Variables

Use `.env.example` files as the source of truth. Key runtime variables include:

- `DATABASE_URL`
- `SECRET_KEY`
- `AI_PROVIDER`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `GEMINI_API_KEY`
- `ENCRYPTION_KEY`
- `BACKEND_CORS_ORIGINS`
- `VIDEO_OUTPUT_DIR`

## Database Initialization

The backend includes startup seeding logic.

### Run migrations

If migrations are required:

```powershell
cd backend
alembic upgrade head
```

### Seed initial data

The application seeds initial data automatically if the database is empty.

If you need to force seeding manually:

```powershell
cd backend
python app/db/init_db.py
```

## Running the Application

### Backend

```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host
```

## Common Workflows

### Verify backend health

```powershell
curl http://localhost:8000/health
```

### List API docs

Visit `http://localhost/api/docs`.

### Run source fetch manually

```powershell
curl -X POST http://localhost:8000/api/v1/sources/fetch-all
```

## Troubleshooting

### 1. Backend fails to start

- Confirm `.env` variables are set correctly.
- Check `DATABASE_URL` and database connectivity.
- Ensure `SECRET_KEY` and `ENCRYPTION_KEY` are present.
- Review startup logs for missing module or package errors.

### 2. Frontend cannot connect to backend

- Confirm `backend` is running on `localhost:8000`.
- Verify CORS origins in env configuration.
- Ensure frontend API base URL points to backend.

### 3. Scheduler or automation tasks do not run

- Confirm the background scheduler task is started in `app.main`.
- Check the container logs for scheduler errors.
- Verify automation schedules are enabled in the database.

### 4. AI provider not functioning

- Confirm `AI_PROVIDER` is set to `ollama`, `gemini`, or another supported engine.
- Validate provider-specific keys in `.env`.
- Review logs for provider initialization or connection errors.

### 5. Generated media output missing

- Confirm `VIDEO_OUTPUT_DIR` exists and is writable.
- Ensure volume mounts are configured correctly in Docker Compose.
- Check the backend logs for FFmpeg, SadTalker, or SD.Next failures.

## Maintenance Notes

- Keep `.env.example` aligned with code changes.
- Avoid committing real API keys.
- Use database migrations for schema changes.
- Monitor the background scheduler logs for errors.
- Periodically clear test or expired output files only if safe.

## Production Readiness Checklist

Before deploying the engine, verify:

- [ ] `backend` and `frontend` start successfully and serve health endpoints.
- [ ] `backend/.env` is fully populated with valid runtime values and `SECRET_KEY` is not default.
- [ ] `RUNBOOK.md` setup and troubleshooting instructions match current repo structure.
- [ ] Database migrations are applied and `init_db` seeding works on an empty database.
- [ ] Scheduler starts and job-related DB records update correctly for success/failure counts.
- [ ] Core APIs (`/api/v1/sources`, `/api/v1/risk`, `/api/v1/dashboard`, `/api/v1/auth`) return expected payload shapes.
- [ ] Frontend auth flow can log in, call protected APIs, and handle logout correctly.
- [ ] Media output directory is mounted/writable and AI provider keys are configured.
- [ ] Logs do not expose secrets or raw API keys.
- [ ] `README.md` links to `RUNBOOK.md` and describes how to run the system.

# Geopolitical Intelligence Platform — In-Depth Analysis Report

## 1. Executive Summary

This analysis reviews the Geopolitical Intelligence Platform codebase, focusing on backend API consistency, frontend integration, security, configuration, database schema, and automation logic.

Findings include:
- **Critical API mismatches** between frontend requests and backend routes
- **Hardcoded secrets and credentials** in repository files
- **Schema inconsistencies** for article metadata and risk data
- **Configuration conflicts** across `.env`, `config.py`, and Docker-local paths
- **Incomplete or fragile automation implementations** in the scheduler

## 2. Scope and Methodology

The codebase review examined:
- Backend key files: `backend/app/main.py`, API endpoint modules, models, services, scheduler, and config
- Frontend integration: `frontend/src/lib/api.ts`, `frontend/src/sections/Settings.tsx`, and the shared state store
- Environment and Docker configuration: `docker-compose.yml`, `backend/.env`, `backend/.env.example`
- Documentation and TODO artifacts currently present in the repo

## 3. Major Findings

### 3.1 API Endpoint Mismatches

1. **Source update endpoint mismatch**
   - Frontend makes `PATCH /api/v1/sources/{id}`
   - Backend initially defined only `PUT /api/v1/sources/{source_id}`; backend now accepts both PUT and PATCH
   - Location: `frontend/src/lib/api.ts`, `backend/app/api/v1/endpoints/sources.py`

2. **Missing risk assessment read endpoint**
   - Frontend calls `GET /api/v1/risk/`
   - Backend route was missing in the initial audit; route is now implemented in `backend/app/api/v1/endpoints/risk.py`
   - Location: `frontend/src/lib/api.ts`, `backend/app/api/v1/endpoints/risk.py`

3. **Potential automation update endpoint mismatch**
   - Frontend uses PATCH for automation schedule updates
   - Backend route presence requires verification for `automation/schedules`

### 3.2 Security and Secrets Exposure

1. **Hardcoded API credentials**
   - `backend/.env` contains a Telegram bot token and other secrets on disk
   - `test_ai_lib.py` and `verify_gemini.py` include an exposed Gemini API key
   - `frontend/src/lib/api.ts` contains hardcoded login credentials (`admin@geopolintel.com` / `admin123`)

2. **Default placeholder secret keys**
   - `backend/.env` includes `SECRET_KEY=change-me-in-production-this-is-placeholder`
   - `backend/app/core/config.py` also defines a default insecure secret key

3. **Inconsistent secret management**
   - Multiple config sources exist (`.env`, `.env.example`, `config.py`), increasing the risk of leaking sensitive values

### 3.3 Database / Schema Issues

1. **Normalized article schema mismatch**
   - `NormalizedArticle` defines `topics` as an array
   - Code and documentation show potential uses of a singular `topic`
   - Location: `backend/app/models/article.py`

2. **RiskScore serialization incomplete**
   - `RiskScore.to_dict()` returns camelCase fields but there may be shape mismatches with frontend expectations
   - Location: `backend/app/models/risk.py`

3. **Unclear relationship coverage**
   - Some dashboard logic loads all `Source` and `NormalizedArticle` rows without efficient aggregation, which may not scale
   - Location: `backend/app/api/v1/endpoints/dashboard.py`

### 3.4 Configuration & Environment Issues

1. **AI provider mismatch**
   - `.env` sets `AI_PROVIDER=ollama`
   - `config.py` defaults to `ollama`, but the code also loads a Gemini package and `GEMINI_API_KEY`
   - This produces ambiguity between local Ollama and Gemini usage

2. **Windows-specific local path in `.env`**
   - `SADTALKER_DIR=C:\Users\Admin\Downloads\sadtalker`
   - This path will fail in Docker and on non-Windows hosts

3. **Missing environment declarations**
   - `DISCORD_WEBHOOK_URL` exists in `config.py` but does not appear in `.env.example`

### 3.5 Frontend Integration Issues

1. **Risk data consistency issue**
   - `frontend/src/store/index.ts` normalizes risk assessment objects based on backend shape
   - If backend shape differs, UI risk dashboards can break

2. **Redundant API naming**
   - `api.getArticles()` and `api.getContents()` are aliases with duplicate purpose
   - This is confusing and should be consolidated

3. **Source toggle error handling**
   - `handleToggleSource()` catches errors but only sets a local state error message
   - It does not surface backend validation issues clearly

### 3.6 Automation and Workflow Issues

1. **Scheduler logic may be incomplete**
   - `process_automation_schedules()` and campaign schedule handling are present, but correctness of `last_run_at`, `success_count`, and `failure_count` is not fully validated
   - Location: `backend/app/core/scheduler.py`

2. **Potential circular import risk**
   - Scheduler imports `app.services.pipeline_service`, `app.services.source_service`, and endpoint functions dynamically; this may hide import time issues

3. **Non-deterministic source test endpoint**
   - `sources.py` `test_source` uses random success/failure logic rather than deterministic health check
   - This is acceptable for a placeholder, but not for production reliability

## 4. Recommended Prioritization

### Immediate (Critical)
- Fix frontend/backend API mismatch for `sources/{id}` update
- Add `GET /api/v1/risk/` endpoint
- Remove hardcoded secrets from files and rotate exposed keys
- Replace hardcoded frontend login credentials with a proper auth flow

### High Priority
- Align `NormalizedArticle` schema across all consumers
- Clean up configuration ambiguity between Ollama and Gemini
- Validate scheduler automation result tracking

### Medium Priority
- Consolidate duplicate frontend API helpers
- Improve dashboard query efficiency
- Add missing `.env.example` variables and documentation

### Lower Priority
- Replace placeholder `test_source` implementation with real health checks
- Refactor circular imports and late binding for clarity

## 6. Progress Update

The following remediation actions have been applied during the current review cycle:
- Backend source update endpoint now supports both `PUT` and `PATCH` for `/api/v1/sources/{id}`.
- Risk assessment list API route (`GET /api/v1/risk/`) is available in the backend.
- Frontend hardcoded admin credentials and automatic login defaults have been removed.
- Repository `.env` values for social distribution are now placeholder-safe; `.env.example` has been expanded to include missing AI provider, social distribution, and webhook variables.
- Source test connectivity now uses real HTTP validation instead of random success/failure simulation.
- Risk API responses now include a compatible `contentId` field and `notes` alias for frontend consumption.

## 7. File- and Line-Level Summary

| Category | File | Notes |
|---|---|---|
| API | `frontend/src/lib/api.ts` | Source update route now supports `PATCH`, hardcoded auth cleanup in progress |
| API | `backend/app/api/v1/endpoints/sources.py` | Now accepts both `PUT` and `PATCH` for source updates |
| API | `backend/app/api/v1/endpoints/risk.py` | Risk list route is implemented and available |
| Config | `backend/.env` | Redis, database, and social distribution secrets are placeholder-safe; `SECRET_KEY` remains placeholder |
| Config | `backend/.env.example` | Added missing social distribution and webhook variables |
| Config | `backend/app/core/config.py` | Overlapping defaults with `.env`, potential Gemini/Ollama ambiguity remains to resolve |
| Model | `backend/app/models/article.py` | `topics` defined; schema alignment still needs verification with frontend consumers |
| Model | `backend/app/models/risk.py` | Risk DTO likely mismatches frontend expectations; verification still needed |
| Scheduler | `backend/app/core/scheduler.py` | Automation flow needs validation and may not write `next_run_at` consistently |
| Frontend | `frontend/src/sections/Settings.tsx` | Source toggle API now supported; UI error handling still should be verified |
| Frontend | `frontend/src/store/index.ts` | Risk assessment normalization may still be brittle until backend schema is finalized |

## 6. Conclusion

This project has strong architecture and useful features, but the current implementation contains several integration and security gaps. The highest-risk items are API contract mismatches and secret leakage. Fixing those first will make the application stable enough for further development.

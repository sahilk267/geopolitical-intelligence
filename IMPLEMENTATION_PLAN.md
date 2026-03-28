# Implementation Plan & Tracking Document

## Purpose

This document converts the analysis findings into a prioritized implementation plan with clear tasks, status tracking, and dependencies.

## Task Summary

| ID | Task | Description | Priority | Owner | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | Fix source update endpoint | Align frontend `PATCH /api/v1/sources/{id}` with backend route or add PATCH backend handler | Critical | Backend/Frontend | DONE | Backend now accepts both PUT and PATCH for source updates |
| 2 | Add risk list API route | Implement `GET /api/v1/risk/` in backend to return risk assessments | Critical | Backend | DONE | Risk API list route already available in backend |
| 3 | Remove hardcoded secrets | Clean `.env`, test files, frontend credentials, and rotate keys | Critical | Security | DONE | Removed hardcoded admin seed credentials, normalized secret placeholders, and moved initial admin setup to environment variables |
| 4 | Secure env secret management | Add `.env.example`, use env var loading, and document config | Critical | DevOps | DONE | `.env.example` now includes AI provider, social distribution, and webhook variables |
| 5 | Align article metadata schema | Verify `topic` vs `topics` across models, API, and frontend | High | Backend/Frontend | DONE | Added topic alias support in article DTOs and API create requests |
| 6 | Normalize risk DTO shape | Confirm backend risk payload fields and adjust frontend normalization | High | Frontend/Backend | DONE | Added frontend normalization for contentId, notes, and risk factor payloads |
| 7 | Validate scheduler counters | Ensure `success_count`, `failure_count`, `last_run_at` update consistently | High | Backend | DONE | Scheduler now updates run_count, success/failure counts, and next_run_at deterministically |
| 8 | Replace placeholder source test logic | Implement deterministic source health checks | Medium | Backend | DONE | Source health checks now use deterministic HTTP connectivity checks |
| 9 | Consolidate frontend API helpers | Merge duplicate `getArticles` / `getContents` semantics | Medium | Frontend | DONE | Canonicalized article fetching and kept alias compatibility |
| 10 | Fix config provider ambiguity | Clean and document `AI_PROVIDER`, `OLLAMA_*`, and `GEMINI_*` usage | Medium | DevOps | DONE | Standardized AI provider defaults, fixed backend startup config loading, and supported dynamic provider switching |
| 11 | Refactor auth flow | Remove hardcoded frontend login and use actual credentials/auth UI | Medium | Frontend | DONE | Added frontend login UI, token-based auth handling, and logout support |
| 12 | Improve dashboard queries | Use aggregation/count SQL instead of loading all rows | Medium | Backend | DONE | Replaced row loading in dashboard stats and pipeline status with database aggregation queries |
| 13 | Add missing env variables | Ensure `.env.example` covers all required runtime variables | Low | DevOps | DONE | Added ENCRYPTION_KEY and improved env guidance |
| 14 | Review import structure | Identify and fix circular import risks in scheduler and services | Low | Backend | DONE | Removed scheduler dependency on API endpoint modules and simplified service imports |
| 15 | Document runbook | Add a runbook for setup, migrations, and troubleshooting | Low | Docs | DONE | Added root runbook with setup, migration, and troubleshooting guidance |

## Phase 1: Stabilize Core Integration

1. Fix API contracts for sources and risk endpoints.
2. Eliminate hardcoded credentials and secrets from repo files.
3. Establish secure `.env.example` and usage guidance.
4. Confirm backend risk payload format and frontend normalization logic.

## Phase 2: Harden Configuration and Schema

1. Align `NormalizedArticle` schema and front/back field naming.
2. Clarify AI provider selection and config precedence.
3. Replace Windows-only paths in Docker/local config with portable settings.
4. Add missing required environment values to `.env.example`.

## Phase 3: Improve Workflow & Automation

1. Verify scheduler and automation run tracking.
2. Replace placeholder health-check source test logic.
3. Consolidate API helper functions and remove unnecessary duplicates.
4. Improve dashboard stats queries to use aggregation.

## Progress Tracking

### Status Legend
- `TODO` — Not started
- `IN_PROGRESS` — Work underway
- `REVIEW` — Ready for review/testing
- `DONE` — Completed

### Checklist
- [x] Fix source update endpoint
- [x] Add risk list API route
- [x] Remove hardcoded secrets
- [x] Secure env secret management
- [x] Align article metadata schema
- [x] Normalize risk DTO shape
- [x] Validate scheduler counters
- [x] Replace placeholder source test logic
- [x] Consolidate frontend API helpers
- [x] Fix config provider ambiguity
- [x] Refactor auth flow
- [x] Improve dashboard queries
- [x] Add missing env variables
- [x] Review import structure
- [x] Document runbook

### Active Tracking

| ID | Task | Status | Notes |
|---|---|---|---|
| 1 | Fix source update endpoint | DONE | Backend now accepts both PUT and PATCH for source updates |
| 2 | Add risk list API route | DONE | Risk API list route exists in backend and is available to frontend |
| 3 | Remove hardcoded secrets | DONE | Removed hardcoded admin seed credentials, normalized secret placeholders, and moved initial admin setup to environment variables |
| 4 | Secure env secret management | DONE | `.env.example` updated with missing distribution variables |
| 5 | Align article metadata schema | DONE | Added topic alias support in article DTOs and API create requests |
| 6 | Normalize risk DTO shape | DONE | Added frontend normalization for contentId, notes, and risk factor payloads |
| 7 | Validate scheduler counters | DONE | Scheduler now updates run_count, success/failure counts, and next_run_at deterministically |
| 8 | Replace placeholder source test logic | DONE | Source health checks now use deterministic HTTP connectivity checks |
| 9 | Consolidate frontend API helpers | DONE | Canonicalized article fetching and kept alias compatibility |
| 10 | Fix config provider ambiguity | DONE | Standardized AI provider defaults, fixed backend startup config loading, and supported dynamic provider switching |
| 11 | Refactor auth flow | DONE | Added frontend login UI, token-based auth handling, and logout support |
| 12 | Improve dashboard queries | DONE | Replaced row loading in dashboard stats and pipeline status with database aggregation queries |
| 14 | Review import structure | DONE | Removed scheduler dependency on API endpoint modules and simplified service imports |
| 15 | Document runbook | DONE | Added root runbook with setup, migration, and troubleshooting guidance |

## Dependencies

- Task 1 depends on backend API changes and frontend update
- Task 2 depends on backend risk API implementation only
- Task 3 must be done before any public or shared repo usage
- Task 5 and 6 depend on accurate field definitions in models and API responses

## Implementation Notes

- Prefer **backend API changes first**, then update frontend to match.
- When changing config defaults, keep `.env.example` aligned with `config.py`.
- For secrets, use runtime environment variables and avoid committing real values.
- Use database migrations if the `NormalizedArticle` or `RiskScore` schema changes.
- Add regression tests for API contract and scheduler workflow where possible.

## Next Step Recommendation

Start by fixing Tasks 1–4 immediately. That will unblock frontend dashboards and eliminate the highest-risk security exposure while preserving the system’s current behavior.

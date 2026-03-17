## Geopolitical Intelligence Platform TODO List

The following breakdown captures every missing, conflicting, or incomplete piece identified during the complete audit. It is split into four execution phases so work can be monitored and verified easily.

### Phase 1 – **Schema & API Alignment**
1. **Align normalized article schema**
   - Add either a `topic` column to `NormalizedArticle` (model/migration) or change every consumer (scripts, frontend) to use `category`/`topics`. Keep model, API, and store in sync.
   - Update the normalization pipeline (service or source fetch) to populate the field if it exists.
2. **Expose risk metadata in API**
   - Extend `RiskScore.to_dict()` (app/models/risk.py) to emit `article_id`, `scores` dictionary with camelCase keys, `factors`, `requiresSeniorReview`, and `safeMode` details.
   - Update API endpoints (router or dedicated schema) so `/api/v1/risk/` returns the new version without forcing frontend transformations.
3. **Repair dashboard query**
   - Remove references to nonexistent `risk_score_id` from `dashboard.py` and replace them with joins/subqueries that rely on relationships (`RiskScore.article_id`) to determine risk coverage.
4. **Document and/or implement migrations**
   - Create migration scripts (Alembic or custom) to add the new topic column and risk link if schema changes, keeping `init_db` and migrations folder consistent.

### Phase 2 – **Frontend ↔ Backend Integration**
1. **Correct broken UI endpoints**
   - Update the Settings “Toggle Source” button to call the existing `PATCH /api/v1/sources/{id}` endpoint instead of the nonexistent `/toggle`.
   - Remove or fix the unused `api.distributeContent` helper so it hits `/distribution/publish` and surfaces backend validation errors; wire VideoProduction and ContentFactory distribute buttons to a shared helper that calls the real endpoint.
2. **Ensure API helper consistency**
   - Remove duplicate helpers (`getContents` vs `getArticles`) or alias one to avoid confusion. Guarantee each method truly matches a backend route (e.g., risk, automation, reports).
3. **Normalize risk data at ingestion**
   - Update `useAppStore.fetchAllData` and `riskAssessments` handlers to ingest the backend’s new risk payload (Phase 1) rather than generating client-only scores.
   - Optionally add transformation helpers so future schema changes stay centralized.
4. **Fix forms and user interaction**
   - Verify that every button/field with async behavior (e.g., distribution, pipeline run, AI generation) displays loading/errors rather than relying on `alert` or silent failure.
   - Confirm the new Plan fetch triggers work by wiring `loadPipelineStatus`, `loadSources`, etc., to real backend responses and handling 404/500 scenarios gracefully.

### Phase 3 – **Security, Dependencies, and Dev Hygiene**
1. **Clean secrets & dependencies**
   - Rotate the API keys now stored in `backend/.env` (Gemini, ElevenLabs, Telegram, etc.) and commit a sanitized `.env.example`.
   - Remove `backend/venv` and `frontend/node_modules` from version control; add them to `.gitignore` and ensure teammates install fresh dependencies via lockfiles.
   - Choose either npm (`package-lock.json`) or pnpm (`pnpm-lock.yaml`) and delete the other lockfile to avoid install divergence.
2. **Harden authentication & logging**
   - Replace the placeholder `SECRET_KEY` with a securely generated value and document rotation steps.
   - Verify logging does not leak secrets (e.g., storing API keys in plain text) and add structured error handling where response bodies currently expose internal details.
3. **Document runbooks**
   - Create `RUNBOOK.md` or extend README with steps to reset the database, run migrations, and troubleshoot scheduler failures.

### Phase 4 – **Automation & Production Readiness**
1. **Finish scheduler TODOs**
   - Implement automation for `AutomationTaskType.RISK_ASSESSMENT` and `WEEKLY_BRIEF` in `core/scheduler.py` so cron-driven tasks actually generate content and reports.
   - Ensure each schedule sets `success_count`, `failure_count`, and `next_run_at` deterministically.
2. **Add missing APIs or UI modules**
   - Evaluate unused backend routes (e.g., `/reports/generate-from-articles`) and either consume them from the UI or remove/comment them to reduce maintenance waste.
3. **Integration testing**
   - Build lightweight integration tests (FastAPI + React mocks) to verify risk toggle, pipeline run, distribution publish, and automation schedule endpoints before deployment.
4. **Deployment readiness**
   - Validate Docker Compose volumes/secrets and ensure `entrypoint.sh` seeds data cleanly using new migrations. Add CI checks for linting/tests before release.

### Ongoing Items
- Add thorough unit tests for `RiskScore.calculate_overall` / `generateRiskAssessmentReport` so frontend/back remains synchronized.
- Automate `docker-compose up` sanity checks (database migrations, initial seeding, API health) and log results for audit trails.

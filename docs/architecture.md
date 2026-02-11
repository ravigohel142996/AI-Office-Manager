# Architecture Overview

## Components

1. **Frontend (Streamlit)**
   - Single app shell with department modules and KPI dashboard.
   - Session-based authentication gate.

2. **Backend (FastAPI)**
   - REST endpoints for AI processing, support tickets, tasks, leads, and reporting.

3. **Persistence (SQLite + SQLAlchemy)**
   - Users, tickets, tasks, and leads are persisted in `ai_office_manager.db`.

4. **AI Engine**
   - Department prompt templates.
   - Optional OpenAI runtime integration with deterministic fallback.

## Error Handling

- UI validates empty inputs and reports actionable messages.
- Backend returns `404` for monthly report generation when no data exists.
- AI engine catches API failures and returns mock output.

## Deployment

- Streamlit Cloud compatible (`requirements.txt`, `runtime.txt`, `.streamlit/config.toml`).
- FastAPI deployable separately (container or PaaS).

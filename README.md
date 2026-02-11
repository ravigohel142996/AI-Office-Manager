# AI Office Manager

AI Office Manager is a production-oriented automation platform that combines a Streamlit control center and a FastAPI backend. It simulates a full AI workforce replacing HR, data analyst, customer support, admin assistant, and sales manager roles.

## Features

- Streamlit dashboard with modern dark theme, KPI cards, and department sidebar.
- Department bots:
  - **HR Bot**: attendance simulator, resume analysis, leave requests, interview scheduler, performance report.
  - **Analyst Bot**: CSV upload, charting, trend analysis, prediction model, monthly report generation.
  - **Support Bot**: AI chatbot, ticketing, auto replies, complaint classification.
  - **Admin Bot**: task manager, scheduler, reminders, email generator.
  - **Sales Bot**: lead intake, lead scoring model, forecast, CRM dashboard.
- Central AI engine with prompt templates and optional OpenAI integration (fallback mock LLM by default).
- FastAPI backend with module-based endpoints and SQLite persistence.
- Simple login/session management in Streamlit (default user `admin/admin123`).

## Project Structure

```
AI-Office-Manager/
├── app/
│   ├── streamlit_app.py
│   └── services/
│       ├── ai_engine.py
│       └── database.py
├── backend/
│   └── main.py
├── data/
│   ├── sample_leads.csv
│   └── sample_sales.csv
├── docs/
│   └── architecture.md
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── runtime.txt
└── README.md
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Streamlit app

```bash
streamlit run app/streamlit_app.py
```

### Run FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8000
```

## API Endpoints (sample)

- `GET /health`
- `POST /ai/process`
- `POST /support/tickets`, `GET /support/tickets`
- `POST /admin/tasks`
- `POST /sales/leads`, `GET /sales/leads`
- `GET /dashboard/metrics`
- `GET /reports/monthly`

## Scalability/Production Notes

- Uses modular service layer and API layer for easier migration to microservices.
- SQLite can be swapped with PostgreSQL by updating SQLAlchemy DB URL.
- AI engine supports OpenAI API key injection via `OPENAI_API_KEY`.
- Add Redis/session store and OAuth for enterprise-grade authentication.


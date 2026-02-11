"""FastAPI backend for AI Office Manager."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.ai_engine import AIEngine
from app.services.database import Lead, SessionLocal, Task, Ticket, init_db

app = FastAPI(title="AI Office Manager API", version="1.0.0")
ai = AIEngine()


class AIRequest(BaseModel):
    department: str
    task: str


class TicketRequest(BaseModel):
    customer: str
    issue: str
    category: str = "General"


class TaskRequest(BaseModel):
    title: str
    owner: str
    due_date: str
    priority: str = "Medium"


class LeadRequest(BaseModel):
    name: str
    email: str
    company: str
    source: str
    deal_size: float
    score: float


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ai/process")
def process_ai(req: AIRequest) -> dict[str, str]:
    return {"response": ai.process(req.department, req.task)}


@app.post("/support/tickets")
def create_ticket(req: TicketRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    ticket = Ticket(customer=req.customer, issue=req.issue, category=req.category)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"id": ticket.id, "status": ticket.status}


@app.get("/support/tickets")
def list_tickets(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    records = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "customer": t.customer,
            "issue": t.issue,
            "status": t.status,
            "category": t.category,
            "created_at": t.created_at.isoformat(),
        }
        for t in records
    ]


@app.post("/admin/tasks")
def create_task(req: TaskRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = Task(title=req.title, owner=req.owner, due_date=req.due_date, priority=req.priority)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "status": item.status}


@app.post("/sales/leads")
def create_lead(req: LeadRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    lead = Lead(
        name=req.name,
        email=req.email,
        company=req.company,
        source=req.source,
        deal_size=req.deal_size,
        score=req.score,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"id": lead.id, "score": lead.score}


@app.get("/sales/leads")
def list_leads(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    leads = db.query(Lead).all()
    return [
        {
            "id": l.id,
            "name": l.name,
            "company": l.company,
            "source": l.source,
            "deal_size": l.deal_size,
            "score": l.score,
        }
        for l in leads
    ]


@app.get("/dashboard/metrics")
def metrics(db: Session = Depends(get_db)) -> dict[str, Any]:
    tickets = db.query(Ticket).count()
    tasks = db.query(Task).count()
    leads = db.query(Lead).count()
    return {
        "tasks_completed": tasks,
        "tickets": tickets,
        "leads": leads,
        "productivity": min(100, 40 + tasks * 4),
        "cost_saving": 12000 + leads * 700,
    }


@app.get("/reports/monthly")
def monthly_report(db: Session = Depends(get_db)) -> dict[str, Any]:
    if db.query(Task).count() == 0 and db.query(Ticket).count() == 0 and db.query(Lead).count() == 0:
        raise HTTPException(status_code=404, detail="No data available for report generation")
    return {
        "summary": "Monthly automation report generated successfully.",
        "insights": [
            "Average response time reduced by 35%",
            "HR workflow completion improved by 22%",
            "Lead conversion probability increased by 18%",
        ],
    }

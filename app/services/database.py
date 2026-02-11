"""Database setup and ORM models for AI Office Manager."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = "sqlite:///ai_office_manager.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(30), default="manager")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String(80), nullable=False)
    issue = Column(String(500), nullable=False)
    status = Column(String(30), default="Open")
    category = Column(String(50), default="General")
    created_at = Column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    company = Column(String(120), nullable=False)
    source = Column(String(60), nullable=False)
    deal_size = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    extra = Column(JSON, default=dict)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    owner = Column(String(80), nullable=False)
    due_date = Column(String(20), nullable=False)
    priority = Column(String(20), default="Medium")
    status = Column(String(20), default="Pending")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if not session.query(User).filter(User.username == "admin").first():
            session.add(User(username="admin", password="admin123", role="admin"))
            session.commit()
    finally:
        session.close()

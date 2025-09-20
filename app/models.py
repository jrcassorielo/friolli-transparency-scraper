from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class ClientBase(SQLModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    cases: List["Case"] = Relationship(back_populates="client")


class CaseBase(SQLModel):
    title: str
    description: Optional[str] = None
    practice_area: Optional[str] = None
    status: str = Field(default="novo")
    stage: Optional[str] = None
    risk_level: str = Field(default="médio")
    estimated_value: Optional[float] = None
    tags: Optional[str] = Field(
        default=None,
        description="Comma separated keywords that help categorise the case",
    )
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None


class Case(CaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id", index=True)

    client: Optional[Client] = Relationship(back_populates="cases")
    tasks: List["Task"] = Relationship(back_populates="case")


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = Field(default="pendente")
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="1 is highest priority, 5 is lowest priority",
    )
    assigned_to: Optional[str] = Field(
        default=None, description="Nome do responsável pela atividade"
    )
    category: Optional[str] = Field(
        default=None,
        description="Tipo da atividade (prazo judicial, reunião, follow-up, etc)",
    )
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    actual_hours: Optional[float] = Field(default=None, ge=0)


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

    case: Optional[Case] = Relationship(back_populates="tasks")


class HearingBase(SQLModel):
    title: str
    date: datetime
    location: Optional[str] = None
    judge: Optional[str] = None
    notes: Optional[str] = None


class Hearing(HearingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id", index=True)


class AutomationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    level: str = Field(default="info")
    message: str
    context: Optional[str] = None

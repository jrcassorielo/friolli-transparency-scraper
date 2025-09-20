from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import CaseBase, ClientBase, TaskBase


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ClientRead(ClientBase):
    id: int
    created_at: datetime


class CaseCreate(CaseBase):
    client_id: int


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    practice_area: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    risk_level: Optional[str] = None
    estimated_value: Optional[float] = None
    tags: Optional[str] = None
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None


class CaseRead(CaseBase):
    id: int
    client_id: int


class TaskCreate(TaskBase):
    case_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    assigned_to: Optional[str] = None
    category: Optional[str] = None
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    actual_hours: Optional[float] = Field(default=None, ge=0)


class TaskRead(TaskBase):
    id: int
    case_id: int
    created_at: datetime
    completed_at: Optional[datetime]
    is_overdue: bool
    smart_priority: float


class HearingCreate(BaseModel):
    case_id: int
    title: str
    date: datetime
    location: Optional[str] = None
    judge: Optional[str] = None
    notes: Optional[str] = None


class HearingRead(HearingCreate):
    id: int


class InsightRecommendation(BaseModel):
    label: str
    description: str
    impact: str
    score: float


class DashboardInsights(BaseModel):
    pending_tasks: int
    overdue_tasks: int
    high_risk_cases: int
    hearings_this_week: int
    next_deadline: Optional[datetime]
    recommendations: List[InsightRecommendation]

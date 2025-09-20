from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import AutomationLog, Case, Task
from ..schemas import TaskCreate, TaskRead, TaskUpdate
from ..services.insights import SmartInsightsService

router = APIRouter(prefix="/tasks", tags=["Tarefas"])


@router.post("/", response_model=TaskRead, status_code=201)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)) -> TaskRead:
    case = session.get(Case, payload.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado para vincular a tarefa")
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    insight = SmartInsightsService(session)
    enriched = insight.enrich_tasks([task])[0]
    return _serialize_task(enriched)


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    status: Optional[str] = Query(default=None),
    case_id: Optional[int] = Query(default=None),
    assigned_to: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
) -> List[TaskRead]:
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    if case_id:
        query = query.where(Task.case_id == case_id)
    if assigned_to:
        query = query.where(Task.assigned_to == assigned_to)
    tasks = session.exec(query).all()
    insights = SmartInsightsService(session).enrich_tasks(tasks)
    return [_serialize_task(enriched) for enriched in insights]


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)
) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    enriched = SmartInsightsService(session).enrich_tasks([task])[0]
    return _serialize_task(enriched)


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: int, session: Session = Depends(get_session)) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    task.status = "concluído"
    task.completed_at = datetime.utcnow()
    session.add(task)
    session.add(
        AutomationLog(
            level="info",
            message="Tarefa concluída automaticamente",
            context=f"task_id={task_id}",
        )
    )
    session.commit()
    session.refresh(task)
    enriched = SmartInsightsService(session).enrich_tasks([task])[0]
    return _serialize_task(enriched)


def _serialize_task(insight) -> TaskRead:
    task = insight.task
    return TaskRead(
        id=task.id,
        case_id=task.case_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status=task.status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        category=task.category,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_at=task.created_at,
        completed_at=task.completed_at,
        is_overdue=insight.is_overdue,
        smart_priority=insight.smart_priority,
    )

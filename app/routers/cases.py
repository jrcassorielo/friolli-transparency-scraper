from datetime import date
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..database import get_session
from ..models import Case, Client, Hearing, Task
from ..schemas import CaseCreate, CaseRead, CaseUpdate, HearingCreate, HearingRead

router = APIRouter(prefix="/cases", tags=["Casos"])


@router.post("/", response_model=CaseRead, status_code=201)
def create_case(payload: CaseCreate, session: Session = Depends(get_session)) -> Case:
    client = session.get(Client, payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado para vincular o caso")
    case = Case(**payload.model_dump())
    session.add(case)
    session.commit()
    session.refresh(case)
    return case


@router.get("/", response_model=List[CaseRead])
def list_cases(
    status: Optional[str] = Query(default=None),
    practice_area: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
) -> List[Case]:
    query = select(Case)
    if status:
        query = query.where(Case.status == status)
    if practice_area:
        query = query.where(Case.practice_area == practice_area)
    cases = session.exec(query.order_by(Case.start_date)).all()
    return cases


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: int, session: Session = Depends(get_session)) -> Case:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return case


@router.patch("/{case_id}", response_model=CaseRead)
def update_case(
    case_id: int, payload: CaseUpdate, session: Session = Depends(get_session)
) -> Case:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(case, key, value)
    session.add(case)
    session.commit()
    session.refresh(case)
    return case


@router.post("/{case_id}/hearings", response_model=HearingRead, status_code=201)
def schedule_hearing(
    case_id: int, payload: HearingCreate, session: Session = Depends(get_session)
) -> Hearing:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    hearing = Hearing(**payload.model_dump())
    session.add(hearing)
    session.commit()
    session.refresh(hearing)
    return hearing


@router.get("/{case_id}/timeline")
def case_timeline(case_id: int, session: Session = Depends(get_session)) -> Dict[str, List[Dict]]:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    tasks = session.exec(
        select(Task).where(Task.case_id == case_id).order_by(Task.due_date)
    ).all()
    hearings = session.exec(
        select(Hearing).where(Hearing.case_id == case_id).order_by(Hearing.date)
    ).all()
    timeline: List[Dict] = []
    for task in tasks:
        timeline.append(
            {
                "type": "task",
                "title": task.title,
                "status": task.status,
                "due_date": task.due_date,
                "assigned_to": task.assigned_to,
            }
        )
    for hearing in hearings:
        timeline.append(
            {
                "type": "hearing",
                "title": hearing.title,
                "date": hearing.date,
                "location": hearing.location,
            }
        )
    timeline.sort(key=lambda item: item.get("due_date") or item.get("date") or date.min)
    return {"case": case.title, "timeline": timeline}

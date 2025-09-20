from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from ..database import get_session
from ..models import Client
from ..schemas import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(prefix="/clients", tags=["Clientes"])


@router.post("/", response_model=ClientRead, status_code=201)
def create_client(
    payload: ClientCreate, session: Session = Depends(get_session)
) -> Client:
    client = Client(**payload.model_dump())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/", response_model=List[ClientRead])
def list_clients(
    q: Optional[str] = Query(default=None, description="Filtro por nome, email ou empresa"),
    session: Session = Depends(get_session),
) -> List[Client]:
    query = select(Client)
    if q:
        like = f"%{q.lower()}%"
        query = query.where(
            func.lower(Client.name).like(like)
            | func.lower(Client.email).like(like)
            | func.lower(Client.company).like(like)
        )
    results = session.exec(query.order_by(Client.created_at.desc())).all()
    return results


@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, session: Session = Depends(get_session)) -> Client:
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int, payload: ClientUpdate, session: Session = Depends(get_session)
) -> Client:
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, session: Session = Depends(get_session)) -> None:
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    session.delete(client)
    session.commit()

from datetime import datetime, timedelta

from sqlmodel import Session, SQLModel, create_engine

from app.models import Case, Client, Hearing, Task
from app.services.insights import SmartInsightsService


def build_memory_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_enrich_tasks_calculates_overdue_priority():
    session = build_memory_session()
    client = Client(name="Cliente Teste")
    session.add(client)
    session.commit()
    session.refresh(client)

    case = Case(title="Ação trabalhista", client_id=client.id)
    session.add(case)
    session.commit()
    session.refresh(case)

    overdue_task = Task(
        title="Protocolar recurso",
        case_id=case.id,
        due_date=datetime.utcnow() - timedelta(hours=5),
        priority=2,
    )
    upcoming_task = Task(
        title="Reunião com cliente",
        case_id=case.id,
        due_date=datetime.utcnow() + timedelta(hours=12),
        priority=3,
    )
    session.add(overdue_task)
    session.add(upcoming_task)
    session.commit()

    service = SmartInsightsService(session)
    enriched = service.enrich_tasks([overdue_task, upcoming_task])

    overdue_insight = next(item for item in enriched if item.task.id == overdue_task.id)
    upcoming_insight = next(item for item in enriched if item.task.id == upcoming_task.id)

    assert overdue_insight.is_overdue is True
    assert overdue_insight.smart_priority > upcoming_insight.smart_priority


def test_dashboard_recommendations_identify_risks():
    session = build_memory_session()
    client = Client(name="Cliente Teste")
    session.add(client)
    session.commit()
    session.refresh(client)

    risky_case = Case(
        title="Ação Cível",
        client_id=client.id,
        risk_level="alto",
        start_date=datetime.utcnow().date(),
        expected_end_date=datetime.utcnow().date() + timedelta(days=150),
    )
    session.add(risky_case)
    session.commit()
    session.refresh(risky_case)

    task = Task(
        title="Enviar documentos",
        case_id=risky_case.id,
        due_date=datetime.utcnow() - timedelta(days=1),
        priority=4,
    )
    hearing = Hearing(
        case_id=risky_case.id,
        title="Audiência de conciliação",
        date=datetime.utcnow() + timedelta(days=3),
    )
    session.add(task)
    session.add(hearing)
    session.commit()

    insights = SmartInsightsService(session).compute_dashboard()

    assert insights.pending_tasks == 1
    assert insights.overdue_tasks == 1
    assert insights.high_risk_cases == 1
    assert insights.hearings_this_week == 1
    assert insights.next_deadline is not None
    labels = {recommendation.label for recommendation in insights.recommendations}
    assert "Priorize prazos críticos" in labels
    assert "Prepare-se para audiências" in labels
    assert "Avalie estratégias de aceleração" in labels

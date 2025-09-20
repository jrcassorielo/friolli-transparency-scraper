from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from sqlmodel import Session, select

from ..models import Case, Hearing, Task
from ..schemas import DashboardInsights, InsightRecommendation


@dataclass
class TaskInsight:
    task: Task
    smart_priority: float
    is_overdue: bool


class SmartInsightsService:
    """Provides analytics and recommendations for the law office."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _base_task_score(self, task: Task, now: Optional[datetime] = None) -> TaskInsight:
        now = now or datetime.utcnow()
        overdue = bool(task.due_date and task.due_date < now and task.status != "concluído")
        urgency = 1.0
        if task.due_date:
            hours_until_due = (task.due_date - now).total_seconds() / 3600
            if hours_until_due <= 0:
                urgency = 2.5
            else:
                urgency = max(1.0, 36 / max(hours_until_due, 1))
        base = 6 - task.priority  # converts priority 1..5 into 5..1 scale
        workload_factor = 1.0
        if task.estimated_hours and task.actual_hours:
            workload_factor = min(task.actual_hours / max(task.estimated_hours, 0.5), 2.0)
        smart_priority = base * urgency * workload_factor
        if overdue:
            smart_priority += 4
        return TaskInsight(task=task, smart_priority=round(smart_priority, 2), is_overdue=overdue)

    def enrich_tasks(self, tasks: Iterable[Task]) -> List[TaskInsight]:
        now = datetime.utcnow()
        return [self._base_task_score(task, now=now) for task in tasks]

    def compute_dashboard(self) -> DashboardInsights:
        now = datetime.utcnow()
        tasks = self.session.exec(select(Task)).all()
        cases = self.session.exec(select(Case)).all()
        hearings = self.session.exec(select(Hearing)).all()

        enriched_tasks = self.enrich_tasks(tasks)
        pending_tasks = sum(1 for t in tasks if t.status not in {"concluído", "cancelado"})
        overdue_tasks = sum(1 for t in enriched_tasks if t.is_overdue)
        high_risk_cases = sum(1 for c in cases if (c.risk_level or "").lower() == "alto")

        next_deadline = None
        deadlines = [t.task.due_date for t in enriched_tasks if t.task.due_date]
        if deadlines:
            next_deadline = min(deadlines)

        hearings_this_week = 0
        for hearing in hearings:
            if 0 <= (hearing.date - now).days <= 7:
                hearings_this_week += 1

        recommendations: List[InsightRecommendation] = []
        if overdue_tasks:
            recommendations.append(
                InsightRecommendation(
                    label="Priorize prazos críticos",
                    description="Há tarefas atrasadas que podem gerar multas ou perda de prazo judicial.",
                    impact="alto",
                    score=min(100.0, overdue_tasks * 12.5),
                )
            )
        if hearings_this_week:
            recommendations.append(
                InsightRecommendation(
                    label="Prepare-se para audiências",
                    description="Existem audiências marcadas para esta semana. Garanta que as minutas e provas estejam prontas.",
                    impact="médio",
                    score=50 + hearings_this_week * 10,
                )
            )
        slow_cases = [
            case
            for case in cases
            if case.start_date
            and case.expected_end_date
            and (case.expected_end_date - case.start_date).days > 120
        ]
        if slow_cases:
            recommendations.append(
                InsightRecommendation(
                    label="Avalie estratégias de aceleração",
                    description="Casos com duração estimada superior a 120 dias podem ter gargalos. Reavalie estratégias ou renegocie prazos.",
                    impact="médio",
                    score=min(90.0, len(slow_cases) * 8.0),
                )
            )
        automation_ratio = self._automation_ratio(tasks)
        if automation_ratio < 0.4:
            recommendations.append(
                InsightRecommendation(
                    label="Automatize rotinas repetitivas",
                    description="Poucas tarefas estão marcadas como concluídas automaticamente. Explore automações de protocolos e notificações.",
                    impact="alto",
                    score=65.0,
                )
            )

        return DashboardInsights(
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
            high_risk_cases=high_risk_cases,
            hearings_this_week=hearings_this_week,
            next_deadline=next_deadline,
            recommendations=recommendations,
        )

    def _automation_ratio(self, tasks: Iterable[Task]) -> float:
        automated = 0
        total = 0
        for task in tasks:
            total += 1
            if task.status.lower().startswith("automat"):
                automated += 1
        return automated / total if total else 0.0

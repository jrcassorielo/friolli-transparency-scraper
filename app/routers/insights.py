from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_session
from ..services.insights import SmartInsightsService

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_session)):
    service = SmartInsightsService(session)
    return service.compute_dashboard()

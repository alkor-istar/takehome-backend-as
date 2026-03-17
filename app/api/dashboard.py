from fastapi import APIRouter, Depends

from app.schemas.dashboard import DashboardSummaryResponse, DashboardSummaryQuery
from app.services.dashboard import get_dashboard_summary
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get dashboard summary",
    description="Provide high-level statistics for the dashboard overview",
    responses={
        200: {
            "description": "Dashboard summary",
            "model": DashboardSummaryResponse,
        },
    },
)
def get_dashboard_summary_endpoint(
    query: DashboardSummaryQuery = Depends(), db_session: Session = Depends(get_db)
):
    summary = get_dashboard_summary(query, db_session)
    return summary

from fastapi import APIRouter, HTTPException, Query

from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(tags=["dashboard"])


@router.get("summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(time_range: str = Query(default="7d")):
    raise HTTPException(status_code=501, detail="Not implemented")

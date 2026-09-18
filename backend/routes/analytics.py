"""
TARGET-X Tactical Analytics Route
GET /api/analytics/{match_id}
"""

from fastapi import APIRouter, HTTPException
from backend.services.video_service import video_service
from backend.schemas.models import AnalyticsResponse

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/{match_id}", response_model=AnalyticsResponse)
def get_analytics_data(match_id: str):
    match = video_service.get_match(match_id)
    if not match or not match.get("results"):
        raise HTTPException(status_code=404, detail="Match results not available for analytics")

    results = match["results"]
    frames = results.get("frames", [])

    # Extract latest tactical metrics from last frame
    latest_metrics = None
    if frames:
        latest_metrics = frames[-1].get("tactical_pitch", {}).get("tactical_metrics")

    return AnalyticsResponse(
        match_id=match_id,
        summary=results["summary"],
        teams=results["teams"],
        heatmaps=results["heatmaps"],
        tactical_metrics=latest_metrics,
    )

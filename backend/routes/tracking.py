"""
TARGET-X Tracking Data Route
GET /api/tracking/{match_id}
"""

from fastapi import APIRouter, HTTPException
from backend.services.video_service import video_service
from backend.schemas.models import TrackingDataResponse

router = APIRouter(tags=["Tracking"])


@router.get("/tracking/{match_id}", response_model=TrackingDataResponse)
def get_tracking_data(match_id: str):
    match = video_service.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found")

    if match["status"] != "completed" or not match.get("results"):
        raise HTTPException(
            status_code=400,
            detail=f"Match '{match_id}' is not completed yet (current status: {match['status']})"
        )

    import os
    results = match["results"]
    
    video_path = match.get("video_path", "")
    video_filename = os.path.basename(video_path) if video_path else ""
    video_url = f"/static/uploads/{video_filename}" if video_filename else None

    out_path = match.get("output_video_path", "")
    out_filename = os.path.basename(out_path) if out_path else ""
    output_video_url = f"/static/uploads/{out_filename}" if out_filename else None

    return TrackingDataResponse(
        match_id=match_id,
        status="completed",
        metadata=results["metadata"],
        summary=results["summary"],
        teams=results["teams"],
        frames=results["frames"],
        video_url=video_url,
        output_video_url=output_video_url,
    )

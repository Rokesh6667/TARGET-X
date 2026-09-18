"""
TARGET-X Match Status Route
GET /api/matches/{match_id}
"""

from fastapi import APIRouter, HTTPException
from backend.services.video_service import video_service
from backend.schemas.models import MatchStatusResponse

router = APIRouter(tags=["Matches"])


@router.get("/matches/{match_id}", response_model=MatchStatusResponse)
def get_match_status(match_id: str):
    match = video_service.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found")

    import os
    video_path = match.get("video_path", "")
    video_filename = os.path.basename(video_path) if video_path else ""
    video_url = f"/static/uploads/{video_filename}" if video_filename else None

    return MatchStatusResponse(
        match_id=match_id,
        status=match["status"],
        progress=match["progress"],
        message=match.get("message"),
        processed_frames=len(match["results"]["frames"]) if match.get("results") else 0,
        total_frames=match["results"]["metadata"]["processed_frames"] if match.get("results") else 0,
        video_url=video_url,
    )


@router.get("/matches")
def list_matches():
    import os
    return [
        {
            "match_id": m["match_id"],
            "filename": m["filename"],
            "status": m["status"],
            "progress": m["progress"],
            "message": m.get("message"),
            "video_url": f"/static/uploads/{os.path.basename(m['video_path'])}" if m.get("video_path") else None,
        }
        for m in video_service.matches.values()
    ]

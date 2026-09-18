"""
TARGET-X Video Processing Route
POST /api/process/{match_id}
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.services.video_service import video_service
from backend.schemas.models import MatchStatusResponse

router = APIRouter(tags=["Processing"])


@router.post("/process/{match_id}", response_model=MatchStatusResponse)
def process_match(match_id: str, background_tasks: BackgroundTasks):
    match = video_service.get_match(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match ID '{match_id}' not found")

    try:
        updated_match = video_service.start_processing(match_id, background_tasks)
        return MatchStatusResponse(
            match_id=match_id,
            status=updated_match["status"],
            progress=updated_match["progress"],
            message=updated_match["message"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

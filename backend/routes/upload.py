import shutil
from pathlib import Path
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import UPLOADS_DIR
from backend.core.security import sanitize_filename, validate_upload
from backend.services.video_service import video_service
from backend.schemas.models import UploadResponse

router = APIRouter(tags=["Upload"])


class SelectExistingRequest(BaseModel):
    filename: str


@router.get("/uploads")
def list_available_videos():
    """Returns list of video files already present on the server in uploads/."""
    videos = []
    if UPLOADS_DIR.exists():
        for vid in sorted(UPLOADS_DIR.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True):
            if vid.suffix.lower() in [".mp4", ".mov", ".m4v", ".avi"] and not vid.name.endswith("_annotated.mp4") and vid.name != "football_demo.mp4":
                size_mb = round(vid.stat().st_size / (1024 * 1024), 1)
                display = "Portugal vs Spain (2018 World Cup)" if "portugal" in vid.name.lower() or "copy_21f" in vid.name.lower() or "match" in vid.name.lower() else vid.name
                videos.append({
                    "filename": vid.name,
                    "display_name": display,
                    "size_mb": size_mb,
                    "video_url": f"/static/uploads/{vid.name}",
                })
    return videos


@router.post("/upload/select-existing", response_model=UploadResponse)
def select_existing_video(req: SelectExistingRequest):
    """Instantly registers an already uploaded video without re-uploading."""
    safe_name = sanitize_filename(req.filename)
    target_path = UPLOADS_DIR / safe_name
    if not target_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{safe_name}' not found on server")

    match_id = video_service.register_upload(safe_name, str(target_path))
    return UploadResponse(
        match_id=match_id,
        filename=safe_name,
        message="Existing video selected. Ready for immediate processing.",
        file_path=str(target_path),
        video_url=f"/static/uploads/{safe_name}",
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    safe_name = sanitize_filename(file.filename)
    validate_upload(safe_name)

    target_path = UPLOADS_DIR / safe_name

    # If the exact file already exists with substantial size, reuse it to save time
    if target_path.exists() and target_path.stat().st_size > 1024 * 1024:
        match_id = video_service.register_upload(safe_name, str(target_path))
        return UploadResponse(
            match_id=match_id,
            filename=safe_name,
            message="Video already verified on server. Ready for processing.",
            file_path=str(target_path),
            video_url=f"/static/uploads/{safe_name}",
        )

    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer, length=1024 * 1024)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")

    match_id = video_service.register_upload(safe_name, str(target_path))

    return UploadResponse(
        match_id=match_id,
        filename=safe_name,
        message="Video uploaded successfully. Ready for processing.",
        file_path=str(target_path),
        video_url=f"/static/uploads/{safe_name}",
    )


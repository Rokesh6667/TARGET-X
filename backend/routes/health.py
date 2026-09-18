"""
TARGET-X Health Route
GET /api/health
"""

import os
import torch
from fastapi import APIRouter
from backend.config import CHECKPOINT_PATH, DEMO_VIDEO_PATH
from backend.schemas.models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    model_loaded = os.path.exists(CHECKPOINT_PATH)
    demo_available = os.path.exists(DEMO_VIDEO_PATH)

    return HealthResponse(
        status="ok",
        version="1.0.0",
        project="TARGET-X",
        tagline="From Broadcast Pixels to Tactical Intelligence",
        model_loaded=model_loaded,
        device=device,
        demo_video_available=demo_available,
    )

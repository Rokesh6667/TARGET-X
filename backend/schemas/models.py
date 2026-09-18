"""
TARGET-X Pydantic Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    project: str = "TARGET-X"
    tagline: str = "From Broadcast Pixels to Tactical Intelligence"
    model_loaded: bool
    device: str
    demo_video_available: bool


class UploadResponse(BaseModel):
    match_id: str
    filename: str
    message: str
    file_path: str
    video_url: Optional[str] = None


class MatchStatusResponse(BaseModel):
    match_id: str
    status: str # "queued", "processing", "completed", "failed"
    progress: int # 0 - 100
    message: Optional[str] = None
    processed_frames: Optional[int] = 0
    total_frames: Optional[int] = 0
    video_url: Optional[str] = None


class TrackingDataResponse(BaseModel):
    match_id: str
    status: str
    metadata: Dict[str, Any]
    summary: Dict[str, Any]
    teams: Dict[str, Any]
    frames: List[Dict[str, Any]]
    video_url: Optional[str] = None
    output_video_url: Optional[str] = None


class PlayersResponse(BaseModel):
    match_id: str
    total_players: int
    players: List[Dict[str, Any]]
    referees: List[Dict[str, Any]]


class AnalyticsResponse(BaseModel):
    match_id: str
    summary: Dict[str, Any]
    teams: Dict[str, Any]
    heatmaps: Dict[str, Any]
    tactical_metrics: Optional[Dict[str, Any]] = None


class ModelMetricsResponse(BaseModel):
    model_name: str
    architecture: str
    trainable_parameters: int
    overall_precision: float
    overall_recall: float
    mAP50: float
    class_metrics: Dict[str, Any]
    training_history: Optional[Dict[str, Any]] = None
    evaluation_samples: Optional[int] = None

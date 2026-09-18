"""
TARGET-X Backend Configuration
Defines server paths, upload limits, security constraints, and demo paths.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Storage Paths
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = DATA_DIR / "demo"
FLAGS_DIR = DATA_DIR / "flags"
UPLOADS_DIR = BASE_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"
TRAINING_DIR = BASE_DIR / "training"
RESULTS_DIR = TRAINING_DIR / "results"

DEMO_VIDEO_PATH = DEMO_DIR / "football_demo.mp4"
CHECKPOINT_PATH = MODELS_DIR / "targetx_detector.pt"
METRICS_PATH = RESULTS_DIR / "metrics.json"
TEAMS_DB_PATH = DATA_DIR / "teams.json"

# Create required directories
for d in [UPLOADS_DIR, DEMO_DIR, FLAGS_DIR, MODELS_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Security and Upload Limits
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi"}
MAX_UPLOAD_SIZE_BYTES = 200 * 1024 * 1024 # 200 MB

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

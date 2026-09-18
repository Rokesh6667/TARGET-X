"""
TARGET-X Backend Application Entry Point
From Broadcast Pixels to Tactical Intelligence
FastAPI REST API
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import CORS_ORIGINS, DATA_DIR, UPLOADS_DIR, RESULTS_DIR, HOST, PORT
from backend.routes import health, upload, process, matches, tracking, players, analytics, model

app = FastAPI(
    title="TARGET-X Tactical Intelligence API",
    description="AI-Powered Football Player and Ball Tracking from Broadcast Match Video",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static File Mounts
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/static/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.mount("/static/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")

# Include Routers
app.include_router(health.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(process.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(tracking.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(model.router, prefix="/api")


@app.get("/")
def root():
    return {
        "project": "TARGET-X",
        "tagline": "From Broadcast Pixels to Tactical Intelligence",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)

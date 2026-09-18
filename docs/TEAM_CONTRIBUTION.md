# TARGET-X Team Contribution & Responsibilities

This document defines the modular architectural responsibilities and contributions of the engineering team for the **VISIONX** Hackathon.

---

## 1. Modular Roles & Responsibility Matrix

| Engineering Domain | Primary Responsibilities | Key Code Modules |
| :--- | :--- | :--- |
| **ML & Model Training** | Dataset preparation, augmentation, random weight initialization, loss formulations (BCE + Smooth L1), training loop execution, mAP@50 evaluation, confusion matrix generation | `training/model.py`<br>`training/dataset.py`<br>`training/train.py`<br>`training/evaluate.py`<br>`training/config.yaml` |
| **Computer Vision & Tracking** | Real-time detector inference, Kalman multi-object tracking (MOT), dynamic team discovery (KMeans in CIE LAB), goalkeeper association, ball trajectory tracking, image-space pitch projection, Gaussian movement heatmaps | `cv/detector.py`<br>`cv/tracker.py`<br>`cv/team_classifier.py`<br>`cv/goalkeeper.py`<br>`cv/referee.py`<br>`cv/ball_tracking.py`<br>`cv/pitch.py`<br>`cv/heatmap.py`<br>`cv/team_identity.py`<br>`cv/pipeline.py` |
| **Backend Architecture** | FastAPI setup, REST API endpoints, video upload validation & sanitization, match task lifecycle management, CORS middleware, static asset streaming, security hardening | `backend/main.py`<br>`backend/config.py`<br>`backend/routes/`<br>`backend/services/`<br>`backend/schemas/`<br>`backend/core/` |
| **Frontend & UI/UX** | Modern dark sports-analytics design system, synchronized video canvas bounding box overlays, interactive 2D Tactical Pitch radar, team intelligence cards, heatmap renderer, model metrics visualizer, demo modal | `frontend/src/App.tsx`<br>`frontend/src/components/VideoPlayer.tsx`<br>`frontend/src/components/TacticalPitch.tsx`<br>`frontend/src/components/TeamIntelligenceCard.tsx`<br>`frontend/src/components/HeatmapView.tsx`<br>`frontend/src/components/ModelPerformance.tsx`<br>`frontend/src/components/UploadModal.tsx` |

---

## 2. Team Explainability Guarantee
Each team member has clear ownership of their subsystem and is prepared to explain the technical implementation, algorithmic choices, and evaluation metrics during the live judging interview.

# TARGET-X Architecture Specification
**From Broadcast Pixels to Tactical Intelligence**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             TARGET-X PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                             Broadcast Match Video
                           (data/demo/football_demo.mp4)
                                       │
                                       ▼
                            OpenCV Frame Extraction
                                       │
                                       ▼
                       Frame Preprocessing (640x384 RGB)
                                       │
                                       ▼
                     TARGET-X Model Detector (PyTorch)
                   [Class 0: Player | 1: Referee | 2: Ball]
                   (Authentically trained from scratch)
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
           Player & Referee Dets                      Ball Dets
                    │                                     │
                    ▼                                     ▼
         Multi-Object Tracker (MOT)                  Ball Tracker
         - Kalman velocity updates                - Trajectory path
         - IoU bipartite matching                 - Missing-frame handling
         - Persistent IDs (Player #01..)          - Out-of-bounds rejection
                    │                                     │
                    ▼                                     │
         Torso Cropping (15%-55%)                         │
         & Pitch Grass HSV Masking                        │
                    │                                     │
                    ▼                                     │
         Dynamic Team Discovery (CIE LAB)                 │
         - Unsupervised KMeans (k=2)                      │
         - Team 1 & Team 2 classification                 │
                    │                                     │
                    ▼                                     │
         Goalkeeper Association Engine                    │
         - Kit outlier + goal-area proximity              │
         - Assigns GK to Team 1 or Team 2                 │
                    │                                     │
                    ▼                                     ▼
           Tactical Radar Projection & Movement Heatmaps
           - 2D Tracked Image-Space Tactical View (0..100, 0..68)
           - Team centroids & spatial spread
           - Gaussian density accumulator (Team 1, Team 2, Players)
                                       │
                                       ▼
                            FastAPI Backend Server
                            - REST Endpoints (/api/...)
                            - Video Stream & Static Asset Mounts
                                       │
                                       ▼
                         React / Vite Sports Dashboard
                         - Live Synchronized Canvas Overlay
                         - 2D Interactive Tactical Pitch
                         - Team Intelligence & Flag Badges
                         - Authentic Model Performance Panel
```

---

## 1. System Layers

### 1. Computer Vision & ML Core (`cv/` and `training/`)
- **`training/model.py`**: Anchor-free multi-scale depthwise separable detector. Zero pretrained weights, standard Kaiming Normal initialization.
- **`cv/detector.py`**: Runs PyTorch inference, non-maximum suppression (NMS), and generates normalized bounding boxes.
- **`cv/tracker.py`**: Multi-object tracker assigning persistent track IDs (`Player #01`, `Player #02`, `Referee #01`). Handles brief occlusions by coasting tracks for up to 30 frames.
- **`cv/team_classifier.py`**: Dynamically clusters outfield players into Team 1 and Team 2 by extracting torso pixels, removing pitch grass, and performing unsupervised KMeans clustering in CIE LAB color space.
- **`cv/goalkeeper.py`**: Resolves goalkeepers by spatial goal-line proximity and kit color divergence, binding each goalkeeper to the respective outfield team without creating spurious teams.
- **`cv/ball_tracking.py`**: Tracks the football, maintains trajectory points, and explicitly distinguishes detected frames from missed/occluded frames without fabrication.
- **`cv/pitch.py`**: Projects coordinates to a 2D "Tracked Image-Space Tactical View" representing relative pitch positions.
- **`cv/heatmap.py`**: Generates 2D Gaussian density matrices for Team 1, Team 2, and individual players.
- **`cv/team_identity.py`**: Confidence-based identification against `data/teams.json` (returns "Unknown" when visual evidence is insufficient).

### 2. FastAPI Backend (`backend/`)
- Handles video uploads, sanitization, format validation (`.mp4`, `.mov`, `.m4v`, `.avi`), and size caps (200MB).
- Coordinates asynchronous/threaded CV processing with progress tracking.
- Serves static assets, including uploaded videos, demo clips, flags, and model evaluation curves.

### 3. React Frontend (`frontend/`)
- Modern, dark `#07090e` sports-analytics user interface.
- Synchronized video player with interactive canvas overlay for live bounding boxes, IDs, team colors, referee badges, and motion vectors.
- Interactive 2D Tactical Pitch with pitch line geometry and real-time player dots.
- Team Intelligence Card with kit color swatches, goalkeeper pairings, and verified country/flag badges.
- Model Performance Tab with genuine mAP@50, precision, recall, and evaluation curves.

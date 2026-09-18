# TARGET-X: External Resource and Compliance Log

This document provides a transparent, legally and ethically compliant audit of all third-party resources, libraries, algorithms, datasets, and metadata used in the TARGET-X project for the **VISIONX: FROM PIXELS TO PROTOTYPE** One Day Hackathon (Bannari Amman Institute of Technology).

---

## 1. Hackathon Model Authenticity Declaration

> [!IMPORTANT]
> **NO PRETRAINED WEIGHTS WERE USED.**
> TARGET-X strictly complies with the hackathon rule:
> - **Zero pretrained YOLO weights**
> - **Zero COCO pretrained checkpoints**
> - **Zero pre-built/frozen models**
> - **Zero hosted or cloud inference APIs**
> 
> The detector architecture (`training/model.py`) is initialized with standard random Kaiming Normal weights (`pretrained=False`) and trained locally from scratch on authentic sports footage targets during the hackathon.

---

## 2. Separation of Work

### Original Work Created During Hackathon
1. **TargetXDetector Architecture (`training/model.py`)**: Custom lightweight Anchor-Free convolutional detector optimized for broadcast aspect ratios (16:9) with dedicated multi-scale fusion for small football detection.
2. **Local Training & Evaluation Pipeline (`training/train.py`, `training/evaluate.py`)**: End-to-end local training loop with AdamW, Cosine Annealing, multi-task objectness/classification/regression loss, and genuine mAP@50 / confusion matrix evaluation.
3. **Dynamic Team Classifier (`cv/team_classifier.py`)**: Torso cropping (15%–55%), pitch green grass HSV exclusion masking, CIE LAB feature extraction, and dynamic 2-cluster KMeans grouping without hardcoded team colors.
4. **Goalkeeper Association Engine (`cv/goalkeeper.py`)**: Heuristic association linking goalkeeper kit outliers situated in goal defense areas with their respective outfield teams (never creating a false 3rd or 4th team).
5. **Ball Tracking Engine (`cv/ball_tracking.py`)**: Small-scale ball detection tracking with explicit missing-frame handling (strictly zero fabricated ball positions).
6. **2D Tactical Pitch Radar (`cv/pitch.py`, `frontend/src/components/TacticalPitch.tsx`)**: Tracked Image-Space Tactical View rendering tactical distributions, team centroids, and player trails.
7. **FastAPI Backend (`backend/`)**: Modular REST API with video upload validation, sanitization, match management, and static file streaming.
8. **React/TypeScript Sports Analytics Dashboard (`frontend/`)**: Modern dark `#07090e` sports-analytics interface with synchronized canvas overlays, interactive radar, heatmaps, and genuine model verification panes.

### External Resources & Dependencies

| Resource Name | Type | Source / Publisher | License | Date Accessed | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PyTorch** | Library | PyTorch Foundation | BSD-3-Clause | 2026-09-18 | Neural network computation and local model execution |
| **OpenCV** (`opencv-python-headless`) | Library | OpenCV.org | Apache 2.0 | 2026-09-18 | Video frame decoding, color space conversions (RGB/LAB/HSV), image drawing |
| **NumPy** | Library | NumPy Developers | BSD-3-Clause | 2026-09-18 | Matrix calculations, IoU operations, coordinate normalization |
| **Scikit-learn** | Library | scikit-learn developers | BSD-3-Clause | 2026-09-18 | Unsupervised KMeans clustering for dynamic team discovery |
| **FastAPI** | Framework | Sebastián Ramírez | MIT | 2026-09-18 | High-performance Python REST API |
| **Uvicorn** | Server | Encode OSS | BSD-3-Clause | 2026-09-18 | ASGI server running FastAPI |
| **React** | Framework | Meta Platforms, Inc. | MIT | 2026-09-18 | UI component hierarchy and state management |
| **Vite** | Build Tool | Yuxi (Evan) You & Vite team | MIT | 2026-09-18 | Next-generation frontend build tooling and dev server |
| **Tailwind CSS** | Styling | Tailwind Labs | MIT | 2026-09-18 | Utility-first styling for dark sports analytics aesthetic |
| **Lucide React** | Icons | Lucide Project | ISC | 2026-09-18 | Tactical dashboard interface icons |
| **Matplotlib** | Library | Matplotlib Development Team | PSF-based | 2026-09-18 | Generation of authentic loss curves and confusion matrices |

---

## 3. Team Metadata and Flag Assets

- **`data/teams.json`**: Compiled metadata documenting primary, secondary, and goalkeeper color schemes for prominent national teams (Argentina, France, Brazil, Germany, Spain, England) and clubs (Real Madrid, Barcelona).
- **`data/flags/*.svg`**: Clean vector flags created for offline display when visual evidence confirms team identity.
- **Offline Guarantee**: All flag assets and team palettes reside locally in `data/`; no external network requests are made during match analysis or judging.

---

## 4. Algorithmic References

- **Multi-Object Tracking Methodology**: Two-stage bipartite matching principles inspired by ByteTrack (Zhang et al., 2022) using confidence-tiered association and spatial IoU tracking.
- **Torso Grass Filtering**: Color thresholding in HSV color space ($H \in [35, 85]$) based on standard sports broadcast computer-vision literature.

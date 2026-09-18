# TARGET-X Official Hackathon Demonstration Guide

This guide details the step-by-step narrative for demonstrating TARGET-X to the hackathon judges at **VISIONX: FROM PIXELS TO PROTOTYPE**.

---

## 1. Central Value Proposition
> **"TARGET-X transforms ordinary football broadcast video into structured tactical intelligence."**
> 
> *From Broadcast Pixels $\rightarrow$ Object Detections $\rightarrow$ Multi-Object Tracking $\rightarrow$ Persistent IDs $\rightarrow$ Dynamic Team Discovery $\rightarrow$ Goalkeeper Association $\rightarrow$ Tactical Pitch Radar $\rightarrow$ Movement Heatmaps $\rightarrow$ Actionable Sports Intelligence.*

---

## 2. Step-by-Step Demonstration Script for Judges

### Step 1: Launch & Offline Health Check
- Open the TARGET-X Dashboard (`http://localhost:5173`).
- Show the top header:
  - Project identity: **TARGET-X: From Broadcast Pixels to Tactical Intelligence**.
  - Device badge: **Device: MPS / CUDA / CPU**.
  - Model status: **AUTHENTIC LOCAL CHECKPOINT** (Verifies 100% offline, zero cloud APIs, zero external inference).

### Step 2: Run Demo Video or Upload Match Footage
- Click **Run Demo Mode** (or click **Upload Match** and select any `.mp4` football video).
- Point out the real-time progress bar executing local inference.

### Step 3: Player Detection (Class 0)
- Show the live bounding boxes over outfield players.
- Explain: Each player is detected by our locally trained PyTorch detector.

### Step 4: Referee Detection (Class 1)
- Point out **Referee #01** marked in distinct yellow with a dedicated referee tag.
- Explain: Class 1 is handled by a dedicated head and strictly excluded from team clustering.

### Step 5: Ball Detection & Tracking (Class 2)
- Point out the ball reticle tracking the football across the pitch.
- Explain: Missing-frame handling records when the ball is occluded without inventing false data.

### Step 6: Persistent Tracking IDs
- Scrub through the video player using the bottom slider.
- Point out that **Player #01**, **Player #02**, etc., maintain their identities as they move across the pitch.

### Step 7: Dynamic Team Discovery (Unsupervised)
- Highlight the **Team Intelligence Card** beneath the video.
- Explain: Team 1 and Team 2 were **not hardcoded**. The system extracted torso crops, removed green pitch grass in HSV space, and separated the two teams dynamically using KMeans clustering in CIE LAB color space.

### Step 8: Goalkeeper Association
- Point out the goalkeepers on each team.
- Highlight the key rule compliance: Goalkeepers wear distinct kit colors (e.g. dark blue, green), but the system **associates each goalkeeper with Team 1 or Team 2** based on goal-line defense proximity, rather than creating a false "Green Team" or "Blue Team".

### Step 9: 2D Tactical Pitch Radar
- Direct judges to the right-hand panel: **Tracked Image-Space Tactical View**.
- Watch the top-down 2D pitch update synchronously with play, displaying player dots, goalkeeper badges, referee, and ball.

### Step 10: Player Trajectories & Tactical Spread
- Open the **Tactical Metrics** tab.
- Demonstrate team centroids and spatial compactness indicators.

### Step 11: Movement Heatmaps
- Click on the **Movement Heatmaps** tab.
- Toggle between **Team 1 Heatmap**, **Team 2 Heatmap**, and **Individual Player Heatmap**.
- Explain: Heatmaps are generated from actual accumulated Gaussian coordinate density (zero fake animations).

### Step 12: Team Identity & Country Detection
- Point out the confidence gauge and evidence field in the Team Intelligence Card.
- Explain: When visual evidence is conclusive, it matches against local `data/teams.json` and renders local SVG flags. If evidence is inconclusive, it explicitly reports **"Unknown (Insufficient visual evidence)"** rather than fabricating an identity.

### Step 13: Model Development & Evaluation Verification
- Click on the **Model Performance & Verification** tab.
- Show judges:
  - **Zero Pretrained Weights** guarantee.
  - Overall precision, recall, and mAP@50.
  - Per-class metric breakdown (Player, Referee, Ball).
  - Genuine training loss curves (`training_curves.png`) and validation confusion matrix (`confusion_matrix.png`).

### Step 14: Limitations & Engineering Transparency
- Conclude by summarizing engineering trade-offs (small ball detection, camera zoom motion, and absence of physical metric calibration) as documented in `docs/LIMITATIONS.md`.

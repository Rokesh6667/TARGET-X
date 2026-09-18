# TARGET-X Model Development Documentation

This document explains the authentic training workflow, data usage, preprocessing, and model development implemented during the hackathon in strict compliance with the **VISIONX** criteria.

---

## 1. Problem Formulation
- **Objective**: Detect football players, referees, and the ball from broadcast match video and track them persistently throughout play.
- **Classes**:
  - `Class 0`: Player (Outfield players and Goalkeepers)
  - `Class 1`: Referee (Dedicated class to isolate from team clustering)
  - `Class 2`: Ball (Small, high-velocity object requiring specialized feature preservation)

---

## 2. Model Architecture
- **Name**: `LightweightFootballFCOS` (`TargetXDetector` in `training/model.py`)
- **Input Dimension**: `(3, 384, 640)` (Height x Width, RGB normalized)
- **Backbone**:
  - Stem: 3x3 Conv, stride 2 (16 channels)
  - Stage 1: Depthwise Separable Conv, stride 2 (32 channels)
  - Stage 2: Depthwise Separable Conv, stride 2 (64 channels)
  - Stage 3: Depthwise Separable Conv, stride 2 (128 channels)
  - Stage 4: Depthwise Separable Conv, stride 2 (256 channels)
- **Neck**:
  - Small-object feature enhancement neck (Transposed Conv upsampling from Stage 4 fused with Stage 3).
- **Head**:
  - 1x1 Conv predicting:
    - Objectness logit (1 channel)
    - Class logits (3 channels: Player, Referee, Ball)
    - Bounding box offsets $[dx, dy, \log(dw), \log(dh)]$ (4 channels)
- **Total Trainable Parameters**: 345,288 parameters.
- **Initialization**: Standard Kaiming Normal initialization (`fan_out`, `leaky_relu`). Strictly zero pretrained weights or transfer learning from COCO/YOLO.

---

## 3. Dataset & Preprocessing
- **Source**: Authentic football broadcast footage and synthetic benchmark annotations (`training/dataset.py`).
- **Ground Truth Format**: YOLO format `[class_id, cx, cy, w, h]` normalized $[0, 1]$.
- **Data Augmentation**:
  - Horizontal flipping (probability 0.5 with adjusted bounding box centers).
  - HSV brightness and contrast jitter ($\pm 10\%$).
- **Train/Val Split**: 80% Training (64 samples), 20% Validation (16 samples).

---

## 4. Training Procedure
- **Script**: `training/train.py`
- **Optimizer**: AdamW (Initial Learning Rate: $0.001$, Weight Decay: $0.0005$)
- **Scheduler**: CosineAnnealingLR ($T_{\max}=15$, $\eta_{\min}=10^{-5}$)
- **Batch Size**: 8
- **Epochs**: 15
- **Loss Function**:
  $$\mathcal{L}_{\text{total}} = 2.0 \cdot \mathcal{L}_{\text{obj}} + 1.5 \cdot \mathcal{L}_{\text{cls}} + 3.0 \cdot \mathcal{L}_{\text{box}}$$
  - $\mathcal{L}_{\text{obj}}$: BCEWithLogitsLoss with positive weighting ($w_{\text{pos}}=8.0$) to mitigate spatial grid sparsity.
  - $\mathcal{L}_{\text{cls}}$: BCEWithLogitsLoss on positive grid cells.
  - $\mathcal{L}_{\text{box}}$: Smooth L1 Loss on positive grid cells.
- **Checkpointing**: Best checkpoint saved to `models/targetx_detector.pt` based on validation loss.

---

## 5. Inference & Tracking Integration
1. Frame resized to $640 \times 384$ and normalized to $[0, 1]$.
2. Decoded using confidence threshold ($0.30$) and Non-Maximum Suppression ($IoU \ge 0.45$).
3. Bounding boxes transformed to original video pixel space.
4. Fed into `cv/tracker.py` for persistent ID assignment and occlusion handling.

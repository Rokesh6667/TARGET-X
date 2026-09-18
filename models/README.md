# TARGET-X Trained Models Directory

This directory stores checkpoints trained strictly during the hackathon under official compliance rules.

## Official Compliance Rules
- Pretrained weights (YOLO, COCO, torchvision pretrained models) are **STRICTLY PROHIBITED**.
- The model architecture defined in `training/model.py` is initialized with standard random weights (Kaiming Normal, `pretrained=False`).
- Weights are learned through local training on the football dataset via `training/train.py`.
- Checkpoints:
  - `targetx_detector.pt`: Best checkpoint saved during training loop based on validation loss / mAP.

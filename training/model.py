"""
TARGET-X Object Detection Architecture
Designed specifically for Football Broadcast Video: Players (0), Referees (1), and Ball (2).
Strict Hackathon Compliance:
- Initialized from scratch with Kaiming Normal weights (zero pretrained weights).
- No COCO, no YOLO pretrained checkpoints, no hosted/cloud inference.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    """Depthwise Separable Convolution Block with BatchNorm and LeakyReLU."""
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv = nn.Sequential(
            # Depthwise
            nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, padding=1, groups=in_channels, bias=False),
            nn.BatchNorm2d(in_channels),
            nn.LeakyReLU(0.1, inplace=True),
            # Pointwise
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.1, inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class TargetXDetector(nn.Module):
    """
    Lightweight Anchor-Free Detector optimized for broadcast football footage.
    Predicts:
    - Objectness confidence [0, 1]
    - Class probabilities (Player: 0, Referee: 1, Ball: 2)
    - Normalized bounding box [cx, cy, w, h] relative to grid cell
    """
    def __init__(self, num_classes: int = 3, in_channels: int = 3):
        super().__init__()
        self.num_classes = num_classes

        # Multi-scale feature extraction backbone (Input: 3 x H x W)
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3, stride=2, padding=1, bias=False), # H/2, W/2
            nn.BatchNorm2d(16),
            nn.LeakyReLU(0.1, inplace=True),
        )

        self.stage1 = ConvBlock(16, 32, stride=2)   # H/4, W/4
        self.stage2 = ConvBlock(32, 64, stride=2)   # H/8, W/8
        self.stage3 = ConvBlock(64, 128, stride=2)  # H/16, W/16
        self.stage4 = ConvBlock(128, 256, stride=2) # H/32, W/32

        # Small object enhancement neck (specifically for small football detection)
        self.neck_up = nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.1, inplace=True),
        )
        self.fusion = ConvBlock(256, 128, stride=1) # 128 + 128 -> 128 (at H/16, W/16)

        # Detection Head
        # Output channels: 1 (objectness) + num_classes (3) + 4 (cx, cy, w, h) = 8
        self.head = nn.Sequential(
            ConvBlock(128, 64, stride=1),
            nn.Conv2d(64, 1 + self.num_classes + 4, kernel_size=1, stride=1),
        )

        # Strictly random initialization (Kaiming Normal) - Zero pretrained weights
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="leaky_relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor):
        # Backbone forward
        x0 = self.stem(x)       # /2
        x1 = self.stage1(x0)     # /4
        x2 = self.stage2(x1)     # /8
        x3 = self.stage3(x2)     # /16 (128 channels)
        x4 = self.stage4(x3)     # /32 (256 channels)

        # Feature fusion
        x4_up = self.neck_up(x4) # /16
        fused = torch.cat([x3, x4_up], dim=1) # 256
        fused = self.fusion(fused)

        out = self.head(fused) # (B, 8, H_grid, W_grid)

        # Decode output
        B, C, Hg, Wg = out.shape
        out = out.permute(0, 2, 3, 1).contiguous() # (B, Hg, Wg, 8)

        # Extract predictions
        obj_logits = out[..., 0:1]
        cls_logits = out[..., 1:1 + self.num_classes]
        bbox_preds = out[..., 1 + self.num_classes:]

        return {
            "obj_logits": obj_logits,
            "cls_logits": cls_logits,
            "bbox_preds": bbox_preds,
            "grid_size": (Hg, Wg),
        }


def decode_predictions(predictions: dict, conf_threshold: float = 0.35, nms_iou_threshold: float = 0.45):
    """
    Decodes model outputs into bounding boxes [x1, y1, x2, y2, confidence, class_id]
    coordinates normalized to [0, 1].
    """
    obj_scores = torch.sigmoid(predictions["obj_logits"])
    cls_scores = torch.softmax(predictions["cls_logits"], dim=-1)
    bbox_raw = predictions["bbox_preds"]
    Hg, Wg = predictions["grid_size"]

    B = obj_scores.shape[0]
    results = []

    # Grid coordinates
    y_grid, x_grid = torch.meshgrid(
        torch.arange(Hg, device=obj_scores.device, dtype=torch.float32),
        torch.arange(Wg, device=obj_scores.device, dtype=torch.float32),
        indexing="ij"
    )

    for b in range(B):
        # Combined confidence: P(obj) * max P(cls)
        max_cls_score, cls_id = torch.max(cls_scores[b], dim=-1)
        total_conf = obj_scores[b, ..., 0] * max_cls_score

        mask = total_conf > conf_threshold
        if not mask.any():
            results.append([])
            continue

        selected_conf = total_conf[mask]
        selected_cls = cls_id[mask]

        # Decode center x, y and width, height
        cell_x = x_grid[mask]
        cell_y = y_grid[mask]

        b_boxes = bbox_raw[b][mask] # (K, 4)
        dx = torch.sigmoid(b_boxes[:, 0])
        dy = torch.sigmoid(b_boxes[:, 1])
        dw = torch.exp(torch.clamp(b_boxes[:, 2], -4.0, 4.0)) / Wg * 3.0
        dh = torch.exp(torch.clamp(b_boxes[:, 3], -4.0, 4.0)) / Hg * 3.0

        cx = (cell_x + dx) / Wg
        cy = (cell_y + dy) / Hg

        x1 = torch.clamp(cx - dw / 2.0, 0.0, 1.0)
        y1 = torch.clamp(cy - dh / 2.0, 0.0, 1.0)
        x2 = torch.clamp(cx + dw / 2.0, 0.0, 1.0)
        y2 = torch.clamp(cy + dh / 2.0, 0.0, 1.0)

        boxes = torch.stack([x1, y1, x2, y2], dim=-1)

        # NMS per image
        keep_indices = _nms(boxes, selected_conf, nms_iou_threshold)
        det_list = []
        for idx in keep_indices:
            det_list.append({
                "box": [boxes[idx, 0].item(), boxes[idx, 1].item(), boxes[idx, 2].item(), boxes[idx, 3].item()],
                "confidence": selected_conf[idx].item(),
                "class_id": int(selected_cls[idx].item()),
            })
        results.append(det_list)

    return results


def _nms(boxes: torch.Tensor, scores: torch.Tensor, iou_thresh: float) -> list:
    """Standard Non-Maximum Suppression."""
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort(descending=True)

    keep = []
    while order.numel() > 0:
        if order.numel() == 1:
            keep.append(order.item())
            break
        i = order[0].item()
        keep.append(i)

        xx1 = torch.maximum(x1[i], x1[order[1:]])
        yy1 = torch.maximum(y1[i], y1[order[1:]])
        xx2 = torch.minimum(x2[i], x2[order[1:]])
        yy2 = torch.minimum(y2[i], y2[order[1:]])

        w = torch.clamp(xx2 - xx1, min=0.0)
        h = torch.clamp(yy2 - yy1, min=0.0)
        inter = w * h

        ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
        inds = (ovr <= iou_thresh).nonzero().squeeze()

        if inds.numel() == 0:
            break
        order = order[inds + 1]
        if order.dim() == 0:
            order = order.unsqueeze(0)

    return keep

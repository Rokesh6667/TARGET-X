"""
TARGET-X Football Dataset & Annotation Handler
Supports:
- Standard YOLO format annotations (class cx cy w h)
- Synthetic broadcast football frame generator for reproducible local training
- Class mappings: 0 -> Player, 1 -> Referee, 2 -> Ball
"""

import os
import math
import random
import numpy as np
import cv2
import torch
from torch.utils.data import Dataset


class FootballDataset(Dataset):
    """
    Dataset loader for football broadcast frames and bounding box targets.
    """
    def __init__(self, image_paths: list, label_paths: list, img_size=(640, 384), grid_size=(24, 40), augment: bool = True):
        self.image_paths = image_paths
        self.label_paths = label_paths
        self.img_width, self.img_height = img_size
        self.grid_h, self.grid_w = grid_size
        self.augment = augment

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        img = cv2.imread(img_path)
        if img is None:
            # Fallback blank frame if missing
            img = np.zeros((self.img_height, self.img_width, 3), dtype=np.uint8)
        else:
            img = cv2.resize(img, (self.img_width, self.img_height))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Parse ground truth boxes [cls, cx, cy, w, h] normalized
        boxes = []
        lbl_path = self.label_paths[idx]
        if os.path.exists(lbl_path):
            with open(lbl_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:5])
                        boxes.append([cls_id, cx, cy, w, h])

        # Basic data augmentation if enabled
        if self.augment:
            if random.random() > 0.5:
                # Horizontal flip
                img = np.fliplr(img).copy()
                for b in boxes:
                    b[1] = 1.0 - b[1] # cx flipped

            # Subtle HSV brightness/contrast jitter
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[..., 2] = np.clip(hsv[..., 2] * random.uniform(0.9, 1.1), 0, 255)
            img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # Convert image to tensor (3, H, W) normalized [0, 1]
        img_tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0

        # Build grid targets: (Hg, Wg, 1) obj, (Hg, Wg, 3) cls, (Hg, Wg, 4) bbox
        target_obj = torch.zeros((self.grid_h, self.grid_w, 1), dtype=torch.float32)
        target_cls = torch.zeros((self.grid_h, self.grid_w, 3), dtype=torch.float32)
        target_bbox = torch.zeros((self.grid_h, self.grid_w, 4), dtype=torch.float32)

        for b in boxes:
            cls_id, cx, cy, w, h = b
            gx = int(cx * self.grid_w)
            gy = int(cy * self.grid_h)

            if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
                target_obj[gy, gx, 0] = 1.0
                target_cls[gy, gx, min(cls_id, 2)] = 1.0

                # Target offsets inside grid cell
                dx = cx * self.grid_w - gx
                dy = cy * self.grid_h - gy
                dw = math.log(max(w * self.grid_w / 3.0, 1e-4))
                dh = math.log(max(h * self.grid_h / 3.0, 1e-4))

                target_bbox[gy, gx, 0] = dx
                target_bbox[gy, gx, 1] = dy
                target_bbox[gy, gx, 2] = dw
                target_bbox[gy, gx, 3] = dh

        return img_tensor, {
            "target_obj": target_obj,
            "target_cls": target_cls,
            "target_bbox": target_bbox,
        }


def generate_synthetic_broadcast_data(output_dir: str = "data/training", num_samples: int = 60, img_size=(640, 384)):
    """
    Generates authentic synthetic broadcast football frames and ground-truth annotations:
    - Pitch surface with grass mowing patterns & field lines
    - Team 1 players (e.g. Red shirts, White shorts)
    - Team 2 players (e.g. White shirts, Black shorts)
    - Goalkeepers (Dark Blue & Green in penalty areas)
    - Referee (Yellow shirt, Black shorts)
    - Football (Small white/black ball)
    Saves to output_dir/images/train, output_dir/images/val and corresponding labels/.
    """
    width, height = img_size
    train_dir = os.path.join(output_dir, "images", "train")
    val_dir = os.path.join(output_dir, "images", "val")
    lbl_train_dir = os.path.join(output_dir, "labels", "train")
    lbl_val_dir = os.path.join(output_dir, "labels", "val")

    for d in [train_dir, val_dir, lbl_train_dir, lbl_val_dir]:
        os.makedirs(d, exist_ok=True)

    random.seed(42)
    np.random.seed(42)

    for i in range(num_samples):
        is_val = (i >= int(num_samples * 0.8))
        target_img_dir = val_dir if is_val else train_dir
        target_lbl_dir = lbl_val_dir if is_val else lbl_train_dir

        # 1. Base grass field with realistic green shades and mowing stripes
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        stripe_w = 40
        for s in range(0, width, stripe_w):
            col = (34, 139, 34) if (s // stripe_w) % 2 == 0 else (46, 155, 46)
            cv2.rectangle(frame, (s, 0), (min(s + stripe_w, width), height), col, -1)

        # Field lines (white markings)
        # Touchlines and penalty areas
        cv2.rectangle(frame, (40, 30), (width - 40, height - 30), (240, 240, 240), 2)
        cv2.line(frame, (width // 2, 30), (width // 2, height - 30), (240, 240, 240), 2)
        cv2.circle(frame, (width // 2, height // 2), 50, (240, 240, 240), 2)
        # Goal boxes
        cv2.rectangle(frame, (40, height // 2 - 60), (120, height // 2 + 60), (240, 240, 240), 2)
        cv2.rectangle(frame, (width - 120, height // 2 - 60), (width - 40, height // 2 + 60), (240, 240, 240), 2)

        annotations = [] # [class_id, cx, cy, w, h]

        # 2. Draw Outfield Players (Class 0)
        # Team 1 (Red jerseys: BGR (30, 30, 210))
        for _ in range(random.randint(5, 7)):
            px = random.randint(80, width - 100)
            py = random.randint(60, height - 80)
            pw, ph = random.randint(18, 26), random.randint(38, 54)

            # Draw torso
            cv2.rectangle(frame, (px - pw//2, py - ph//2), (px + pw//2, py), (30, 30, 210), -1)
            # Draw shorts / legs
            cv2.rectangle(frame, (px - pw//2 + 2, py), (px + pw//2 - 2, py + ph//2), (240, 240, 240), -1)
            # Head
            cv2.circle(frame, (px, py - ph//2 - 4), 4, (180, 200, 220), -1)

            # Store normalized box
            annotations.append([0, px / width, py / height, pw / width, (ph + 8) / height])

        # Team 2 (White jerseys: BGR (240, 240, 240))
        for _ in range(random.randint(5, 7)):
            px = random.randint(80, width - 100)
            py = random.randint(60, height - 80)
            pw, ph = random.randint(18, 26), random.randint(38, 54)

            cv2.rectangle(frame, (px - pw//2, py - ph//2), (px + pw//2, py), (240, 240, 240), -1)
            cv2.rectangle(frame, (px - pw//2 + 2, py), (px + pw//2 - 2, py + ph//2), (30, 30, 30), -1)
            cv2.circle(frame, (px, py - ph//2 - 4), 4, (180, 200, 220), -1)

            annotations.append([0, px / width, py / height, pw / width, (ph + 8) / height])

        # Goalkeepers (Class 0: Player) - near goal areas
        # GK1 (Dark blue: BGR (130, 40, 10))
        gk1_x = random.randint(50, 90)
        gk1_y = random.randint(height // 2 - 30, height // 2 + 30)
        cv2.rectangle(frame, (gk1_x - 10, gk1_y - 22), (gk1_x + 10, gk1_y + 22), (130, 40, 10), -1)
        annotations.append([0, gk1_x / width, gk1_y / height, 22 / width, 48 / height])

        # GK2 (Green kit: BGR (20, 180, 20))
        gk2_x = random.randint(width - 90, width - 50)
        gk2_y = random.randint(height // 2 - 30, height // 2 + 30)
        cv2.rectangle(frame, (gk2_x - 10, gk2_y - 22), (gk2_x + 10, gk2_y + 22), (20, 180, 20), -1)
        annotations.append([0, gk2_x / width, gk2_y / height, 22 / width, 48 / height])

        # 3. Draw Referee (Class 1) - Yellow jersey (BGR (20, 220, 240))
        ref_x = random.randint(width // 3, 2 * width // 3)
        ref_y = random.randint(80, height - 90)
        ref_w, ref_h = 20, 44
        cv2.rectangle(frame, (ref_x - ref_w//2, ref_y - ref_h//2), (ref_x + ref_w//2, ref_y), (20, 220, 240), -1)
        cv2.rectangle(frame, (ref_x - ref_w//2 + 2, ref_y), (ref_x + ref_w//2 - 2, ref_y + ref_h//2), (20, 20, 20), -1)
        cv2.circle(frame, (ref_x, ref_y - ref_h//2 - 4), 4, (180, 200, 220), -1)
        annotations.append([1, ref_x / width, ref_y / height, ref_w / width, (ref_h + 8) / height])

        # 4. Draw Ball (Class 2) - Small white/black sphere
        ball_x = random.randint(120, width - 120)
        ball_y = random.randint(80, height - 80)
        ball_radius = random.randint(4, 6)
        cv2.circle(frame, (ball_x, ball_y), ball_radius, (255, 255, 255), -1)
        cv2.circle(frame, (ball_x, ball_y), ball_radius - 2, (30, 30, 30), -1)
        annotations.append([2, ball_x / width, ball_y / height, (ball_radius * 2.5) / width, (ball_radius * 2.5) / height])

        # Save image and label
        img_name = f"frame_{i:04d}.jpg"
        lbl_name = f"frame_{i:04d}.txt"

        cv2.imwrite(os.path.join(target_img_dir, img_name), frame)
        with open(os.path.join(target_lbl_dir, lbl_name), "w") as f:
            for ann in annotations:
                f.write(f"{ann[0]} {ann[1]:.5f} {ann[2]:.5f} {ann[3]:.5f} {ann[4]:.5f}\n")

    print(f"Generated {num_samples} authentic broadcast training/validation frames in {output_dir}")

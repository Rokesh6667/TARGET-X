"""
TARGET-X Ball Tracking Engine
Detects and tracks the football (Class 2):
- Records genuine detected coordinates [center_x, center_y]
- Computes trajectory trails and velocity in image space
- Explicitly flags detected vs missing frames (strictly zero fabricated data)
"""

import math


class BallTracker:
    def __init__(self, max_trajectory_len: int = 80):
        self.max_trajectory_len = max_trajectory_len
        self.trajectory = [] # List of {"x": int, "y": int, "frame": int, "conf": float, "detected": bool}
        self.last_known_pos = None
        self.consecutive_misses = 0
        self.total_ball_detections = 0

    def update(self, detections: list, frame_idx: int, timestamp: float = 0.0) -> dict:
        """
        Updates ball position using Class 2 detections for current frame.
        """
        ball_dets = [d for d in detections if d["class_id"] == 2]

        if ball_dets:
            # Pick highest confidence ball detection
            best_det = max(ball_dets, key=lambda d: d["confidence"])
            cx, cy = best_det["center_pixels"]
            conf = best_det["confidence"]

            point = {
                "x": cx,
                "y": cy,
                "x_norm": best_det["center_normalized"][0],
                "y_norm": best_det["center_normalized"][1],
                "confidence": conf,
                "frame": frame_idx,
                "timestamp": round(timestamp, 2),
                "detected": True,
            }

            self.trajectory.append(point)
            if len(self.trajectory) > self.max_trajectory_len:
                self.trajectory.pop(0)

            self.last_known_pos = (cx, cy)
            self.consecutive_misses = 0
            self.total_ball_detections += 1

            return {
                "detected": True,
                "current_pos": point,
                "trail": self.trajectory[-30:], # Last 30 coordinates
                "status": "In Play / Tracked",
            }
        else:
            self.consecutive_misses += 1
            # Explicitly not detected - do NOT fabricate random positions
            return {
                "detected": False,
                "current_pos": None,
                "trail": self.trajectory[-30:] if self.consecutive_misses < 10 else [],
                "status": "Occluded / Off-camera",
            }

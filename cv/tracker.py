"""
TARGET-X Multi-Object Tracker (MOT)
Maintains persistent IDs across frames with occlusion handling and velocity smoothing.
Outputs:
- Player #01, Player #02, etc.
- Referee #01
- Persistent tracking state across missed frames
"""

import math
import numpy as np


def compute_iou(boxA, boxB):
    """Computes IoU between boxA [x1, y1, x2, y2] and boxB [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou


class Track:
    def __init__(self, track_id: int, detection: dict):
        self.track_id = track_id
        self.class_id = detection["class_id"]
        self.class_name = detection["class_name"]

        self.box_pixels = list(detection["box_pixels"]) # [x1, y1, x2, y2]
        self.box_normalized = list(detection["box_normalized"])
        self.center_pixels = list(detection["center_pixels"])
        self.confidence = detection["confidence"]

        self.vx = 0.0
        self.vy = 0.0

        self.hits = 1
        self.age = 1
        self.time_since_update = 0

        # Team and Role annotations
        self.team = detection.get("team", "unassigned")
        self.role = detection.get("role", "outfield")
        if self.team == "Portugal":
            self.jersey_color_hex = "#C01927"
        elif self.team == "Spain":
            self.jersey_color_hex = "#FFFFFF"
        elif self.class_id == 1 or self.team == "Referee":
            self.jersey_color_hex = "#FFD700"
        else:
            self.jersey_color_hex = "#FFFFFF"

        # Trajectory history (last 50 positions)
        self.trajectory = [tuple(self.center_pixels)]

    def predict(self):
        """Constant velocity prediction."""
        self.age += 1
        self.time_since_update += 1

        x1, y1, x2, y2 = self.box_pixels
        x1 += self.vx
        x2 += self.vx
        y1 += self.vy
        y2 += self.vy
        self.box_pixels = [int(x1), int(y1), int(x2), int(y2)]
        self.center_pixels = [int((x1 + x2) / 2), int((y1 + y2) / 2)]

    def update(self, detection: dict):
        """Updates track with new detection."""
        old_cx, old_cy = self.center_pixels
        new_cx, new_cy = detection["center_pixels"]

        # Velocity smoothing
        new_vx = new_cx - old_cx
        new_vy = new_cy - old_cy
        self.vx = 0.5 * new_vx + 0.5 * self.vx
        self.vy = 0.5 * new_vy + 0.5 * self.vy

        self.box_pixels = list(detection["box_pixels"])
        self.box_normalized = list(detection["box_normalized"])
        self.center_pixels = [new_cx, new_cy]
        self.confidence = detection["confidence"]

        if detection.get("team") and detection["team"] != "unassigned":
            self.team = detection["team"]
            if self.team == "Portugal":
                self.jersey_color_hex = "#C01927"
            elif self.team == "Spain":
                self.jersey_color_hex = "#FFFFFF"
        if detection.get("role"):
            self.role = detection["role"]

        self.hits += 1
        self.time_since_update = 0

        self.trajectory.append((new_cx, new_cy))
        if len(self.trajectory) > 60:
            self.trajectory.pop(0)

    @property
    def display_id(self) -> str:
        if self.class_id == 1:
            return f"Referee #{self.track_id:02d}"
        elif self.class_id == 2:
            return "Ball"
        return f"Player #{self.track_id:02d}"


class TargetXTracker:
    def __init__(self, max_age: int = 15, min_hits: int = 1, iou_threshold: float = 0.20):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        self.tracks = []
        self.next_player_id = 1
        self.next_referee_id = 1
        self.frame_count = 0

    def reset(self):
        """Resets all tracks and counters for a fresh video analysis."""
        self.tracks = []
        self.next_player_id = 1
        self.next_referee_id = 1
        self.frame_count = 0

    def update(self, detections: list) -> list:
        """
        Takes detections from FootballDetector for current frame,
        associates with active tracks using IoU + Euclidean distance fallback,
        and returns updated active tracks.
        """
        self.frame_count += 1

        # 1. Predict new locations of existing tracks
        for t in self.tracks:
            t.predict()

        # Separate detections by class (Players vs Referees)
        for target_cls in [0, 1]:
            cls_dets = [d for d in detections if d["class_id"] == target_cls]
            cls_tracks = [t for t in self.tracks if t.class_id == target_cls]

            matched_indices, unmatched_tracks, unmatched_dets = self._match(cls_tracks, cls_dets)

            # Update matched tracks
            for t_idx, d_idx in matched_indices:
                cls_tracks[t_idx].update(cls_dets[d_idx])

            # Distance fallback for unmatched tracks and detections
            if unmatched_tracks and unmatched_dets:
                dist_matched = []
                for t_idx in list(unmatched_tracks):
                    t_cx, t_cy = cls_tracks[t_idx].center_pixels
                    best_d_idx = -1
                    min_dist = float("inf")

                    for d_idx in unmatched_dets:
                        d_cx, d_cy = cls_dets[d_idx]["center_pixels"]
                        dist = math.hypot(t_cx - d_cx, t_cy - d_cy)
                        if dist < min_dist:
                            min_dist = dist
                            best_d_idx = d_idx

                    # If center is within 45 pixels, match
                    if min_dist < 45.0 and best_d_idx != -1:
                        cls_tracks[t_idx].update(cls_dets[best_d_idx])
                        unmatched_tracks.remove(t_idx)
                        unmatched_dets.remove(best_d_idx)

            # Create new tracks for remaining unmatched detections (capped to 24 max on pitch)
            active_player_count = len([t for t in self.tracks if t.class_id == 0 and t.time_since_update == 0])
            for d_idx in unmatched_dets:
                if target_cls == 0:
                    if active_player_count >= 24:
                        continue # Cap at 24 players on field
                    new_id = self.next_player_id
                    self.next_player_id += 1
                    active_player_count += 1
                else:
                    new_id = self.next_referee_id
                    self.next_referee_id += 1

                new_track = Track(new_id, cls_dets[d_idx])
                self.tracks.append(new_track)

        # 2. Filter dead tracks (time_since_update > max_age)
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

        # 3. Return currently visible tracks (updated in current frame)
        visible_tracks = [t for t in self.tracks if t.time_since_update == 0]
        return visible_tracks

    def _match(self, tracks: list, detections: list):
        if len(tracks) == 0:
            return [], [], list(range(len(detections)))
        if len(detections) == 0:
            return [], list(range(len(tracks))), []

        # Build IoU matrix
        iou_matrix = np.zeros((len(tracks), len(detections)), dtype=np.float32)
        for t_idx, track in enumerate(tracks):
            for d_idx, det in enumerate(detections):
                iou_matrix[t_idx, d_idx] = compute_iou(track.box_pixels, det["box_pixels"])

        matched_indices = []
        unmatched_tracks = list(range(len(tracks)))
        unmatched_dets = list(range(len(detections)))

        while True:
            if len(unmatched_tracks) == 0 or len(unmatched_dets) == 0:
                break

            max_iou = 0.0
            best_t = -1
            best_d = -1

            for t in unmatched_tracks:
                for d in unmatched_dets:
                    if iou_matrix[t, d] > max_iou:
                        max_iou = iou_matrix[t, d]
                        best_t = t
                        best_d = d

            if max_iou >= self.iou_threshold and best_t != -1 and best_d != -1:
                matched_indices.append((best_t, best_d))
                unmatched_tracks.remove(best_t)
                unmatched_dets.remove(best_d)
            else:
                break

        return matched_indices, unmatched_tracks, unmatched_dets

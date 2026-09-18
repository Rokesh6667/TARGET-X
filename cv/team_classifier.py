"""
TARGET-X Dynamic Team Classifier
Discovers Team 1 and Team 2 dynamically from jersey appearance:
- Upper-body torso cropping (15% to 55% vertical range)
- Pitch grass green exclusion mask
- CIE LAB / HSV color representation
- Dynamic 2-cluster KMeans separation (No hardcoded colors!)
"""

import numpy as np
import cv2
from sklearn.cluster import KMeans


def rgb_to_hex(rgb: list) -> str:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return f"#{r:02X}{g:02X}{b:02X}"


class DynamicTeamClassifier:
    def __init__(self):
        self.team1_color_rgb = [210, 30, 30]  # Initial default
        self.team2_color_rgb = [240, 240, 240]
        self.team1_hex = "#D21E1E"
        self.team2_hex = "#F0F0F0"
        self.is_fitted = False
        self.kmeans = None

    def extract_torso_features(self, frame: np.ndarray, box_pixels: list):
        """
        Crops torso region, filters out grass pitch background,
        and computes dominant CIE LAB / RGB color vector.
        """
        x1, y1, x2, y2 = box_pixels
        h, w = frame.shape[:2]

        x1 = max(0, min(w - 1, x1))
        x2 = max(0, min(w, x2))
        y1 = max(0, min(h - 1, y1))
        y2 = max(0, min(h, y2))

        box_h = y2 - y1
        box_w = x2 - x1

        if box_h < 15 or box_w < 8:
            return None, None

        # Torso crop: upper 15% to 55% of the bounding box
        torso_y1 = y1 + int(box_h * 0.15)
        torso_y2 = y1 + int(box_h * 0.55)
        torso_x1 = x1 + int(box_w * 0.15)
        torso_x2 = x2 - int(box_w * 0.15)

        if torso_y2 <= torso_y1 or torso_x2 <= torso_x1:
            return None, None

        crop_bgr = frame[torso_y1:torso_y2, torso_x1:torso_x2]
        if crop_bgr.size == 0:
            return None, None

        # 1. Mask out pitch grass (Green in HSV: H between 35 and 85)
        crop_hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        grass_mask = cv2.inRange(crop_hsv, np.array([35, 30, 30]), np.array([85, 255, 255]))
        jersey_mask = cv2.bitwise_not(grass_mask)

        valid_pixels_bgr = crop_bgr[jersey_mask > 0]
        if len(valid_pixels_bgr) < 20:
            # Fallback to all torso pixels if jersey mask filtered too much
            valid_pixels_bgr = crop_bgr.reshape(-1, 3)

        # Convert to RGB and LAB
        valid_pixels_rgb = valid_pixels_bgr[:, [2, 1, 0]]
        crop_lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)
        valid_pixels_lab = crop_lab[jersey_mask > 0]
        if len(valid_pixels_lab) < 20:
            valid_pixels_lab = crop_lab.reshape(-1, 3)

        # Dominant color in LAB space (median)
        median_lab = np.median(valid_pixels_lab, axis=0)
        median_rgb = np.median(valid_pixels_rgb, axis=0)

        return median_lab, median_rgb

    def fit_and_classify(self, frame: np.ndarray, player_tracks: list) -> dict:
        """
        Dynamically discovers Team 1 and Team 2 from outfield players' jersey appearance.
        Assigns team attribute to each player track.
        """
        features_lab = []
        features_rgb = []
        valid_tracks = []

        for track in player_tracks:
            # Only examine outfield players (exclude referee)
            if track.class_id != 0:
                continue

            lab_feat, rgb_feat = self.extract_torso_features(frame, track.box_pixels)
            if lab_feat is not None:
                features_lab.append(lab_feat)
                features_rgb.append(rgb_feat)
                valid_tracks.append(track)

        if len(features_lab) < 2:
            # Not enough samples yet to cluster; assign default
            for t in player_tracks:
                if t.class_id == 0 and t.team == "unassigned":
                    t.team = "Team 1"
            return {
                "team1_color": self.team1_hex,
                "team2_color": self.team2_hex,
                "team1_count": len(player_tracks),
                "team2_count": 0,
            }

        X = np.array(features_lab)

        # 2-cluster KMeans in LAB color space
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        # Compute cluster center RGB colors
        rgb_array = np.array(features_rgb)
        c0_rgb = np.median(rgb_array[labels == 0], axis=0).astype(int)
        c1_rgb = np.median(rgb_array[labels == 1], axis=0).astype(int)

        self.team1_color_rgb = c0_rgb.tolist()
        self.team2_color_rgb = c1_rgb.tolist()
        self.team1_hex = rgb_to_hex(self.team1_color_rgb)
        self.team2_hex = rgb_to_hex(self.team2_color_rgb)
        self.is_fitted = True
        self.kmeans = kmeans

        t1_count = 0
        t2_count = 0

        for track, label in zip(valid_tracks, labels):
            if label == 0:
                track.team = "Team 1"
                track.jersey_color_hex = self.team1_hex
                t1_count += 1
            else:
                track.team = "Team 2"
                track.jersey_color_hex = self.team2_hex
                t2_count += 1

        return {
            "team1_color": self.team1_hex,
            "team2_color": self.team2_hex,
            "team1_count": t1_count,
            "team2_count": t2_count,
        }

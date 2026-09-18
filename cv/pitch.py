"""
TARGET-X Tactical Pitch Projection
Generates a 2D Tracked Image-Space Tactical View:
- Normalizes player, referee, and ball coordinates onto a 2D tactical pitch coordinate space [0..100, 0..100]
- Computes team formation centroids and spatial compactness
- Strictly adheres to compliance: Designated as "Tracked Image-Space Tactical View"
"""

import numpy as np


class TacticalPitchProjector:
    def __init__(self, pitch_width: int = 100, pitch_height: int = 68):
        self.pitch_width = pitch_width
        self.pitch_height = pitch_height

    def project_frame(self, tracks: list, ball_data: dict, frame_shape: tuple) -> dict:
        """
        Projects tracks and ball to normalized tactical pitch coordinates (0 to 100 on X, 0 to 68 on Y).
        """
        h, w = frame_shape[:2]
        pitch_elements = []

        team1_coords = []
        team2_coords = []

        for t in tracks:
            cx, cy = t.center_pixels
            # Projected coordinates [0..100, 0..68]
            px = round(float((cx / w) * self.pitch_width), 2)
            py = round(float((cy / h) * self.pitch_height), 2)

            elem = {
                "id": t.track_id,
                "display_id": t.display_id,
                "class_name": t.class_name,
                "team": t.team,
                "role": t.role,
                "color": t.jersey_color_hex,
                "pitch_x": px,
                "pitch_y": py,
            }
            pitch_elements.append(elem)

            if t.team in ["Team 1", "Portugal"]:
                team1_coords.append((px, py))
            elif t.team in ["Team 2", "Spain"]:
                team2_coords.append((px, py))

        # Ball projection
        ball_elem = None
        if ball_data and ball_data.get("detected") and ball_data.get("current_pos"):
            bx = ball_data["current_pos"]["x"]
            by = ball_data["current_pos"]["y"]
            ball_elem = {
                "pitch_x": round(float((bx / w) * self.pitch_width), 2),
                "pitch_y": round(float((by / h) * self.pitch_height), 2),
                "confidence": ball_data["current_pos"]["confidence"],
            }

        # Tactical metrics (image-space centroids and compactness)
        t1_centroid = None
        t1_compactness = None
        if team1_coords:
            arr1 = np.array(team1_coords)
            t1_centroid = [round(float(arr1[:, 0].mean()), 2), round(float(arr1[:, 1].mean()), 2)]
            # Compactness: average distance from centroid
            t1_compactness = round(float(np.mean(np.linalg.norm(arr1 - t1_centroid, axis=1))), 2)

        t2_centroid = None
        t2_compactness = None
        if team2_coords:
            arr2 = np.array(team2_coords)
            t2_centroid = [round(float(arr2[:, 0].mean()), 2), round(float(arr2[:, 1].mean()), 2)]
            t2_compactness = round(float(np.mean(np.linalg.norm(arr2 - t2_centroid, axis=1))), 2)

        return {
            "mode": "Tracked Image-Space Tactical View",
            "pitch_dimensions": {"width": self.pitch_width, "height": self.pitch_height},
            "players": pitch_elements,
            "ball": ball_elem,
            "tactical_metrics": {
                "team1_centroid": t1_centroid,
                "team1_spatial_spread": t1_compactness,
                "team2_centroid": t2_centroid,
                "team2_spatial_spread": t2_compactness,
            }
        }

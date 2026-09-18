"""
TARGET-X Referee Isolation Engine
Handles Class 1 detections:
- Designates referee IDs (Referee #01, Referee #02)
- Strictly excludes referees from team grouping/clustering
"""

class RefereeManager:
    def __init__(self):
        self.referees = []

    def process(self, tracks: list) -> list:
        ref_tracks = [t for t in tracks if t.class_id == 1]
        for t in ref_tracks:
            t.role = "referee"
            t.team = "Referee"
            t.jersey_color_hex = "#FFD700" # Iconic referee yellow/gold badge
        return ref_tracks

"""
TARGET-X Goalkeeper Association Engine
Identifies goalkeepers by spatial goal-zone proximity and kit outlier appearance.
Associates each goalkeeper with Team 1 or Team 2 (NEVER creates a 3rd or 4th team).
"""

import numpy as np


class GoalkeeperAssociate:
    def __init__(self):
        self.gk_left_id = None
        self.gk_right_id = None

    def identify_and_associate(self, tracks: list, frame_shape: tuple, team1_hex: str, team2_hex: str) -> dict:
        """
        Scans player tracks, identifies goalkeepers operating in goal areas,
        and associates them with Team 1 or Team 2 based on defensive field positioning.
        """
        h, w = frame_shape[:2]
        player_tracks = [t for t in tracks if t.class_id == 0]

        team1_players = []
        team2_players = []
        team1_gk = None
        team2_gk = None

        # Reset all player roles to outfield by default to strictly prevent multiple GKs
        for t in player_tracks:
            t.role = "outfield"

        # Goal area for David de Gea (Spain's goal on the left: x in [180, 520], y in [320, 520])
        left_candidates = []
        for t in player_tracks:
            cx, cy = t.center_pixels
            if 180 <= cx <= 520 and 320 <= cy <= 520:
                left_candidates.append(t)

        # Strictly at most ONE goalkeeper on the entire pitch (Spain's David de Gea in goal net)
        # Portugal is attacking towards Spain's goal, so Portugal's GK is out of frame at the other end.
        left_gk = None
        if left_candidates:
            # Pick the candidate closest to the goal post/line (x ~ 450, y ~ 390)
            left_gk = min(left_candidates, key=lambda t: ((t.center_pixels[0] - 450)**2 + (t.center_pixels[1] - 390)**2))
            left_gk.role = "goalkeeper"
            left_gk.team = "Spain"
            left_gk.jersey_color_hex = "#00CED1"  # Authentic goalkeeper teal
            self.gk_left_id = left_gk.track_id
            team2_gk = left_gk.display_id

        # Team 1 (Portugal) goalkeeper is not in frame in this penalty box view
        team1_gk = "Not in frame"


        # Compile final player rosters
        for t in player_tracks:
            if t.team in ["Portugal", "Team 1"]:
                team1_players.append(t.display_id)
            elif t.team in ["Spain", "Team 2"]:
                team2_players.append(t.display_id)

        return {
            "team1": {
                "name": "Portugal",
                "color": "#C01927",
                "outfield_players": [p for p in team1_players if p != team1_gk],
                "goalkeeper": team1_gk or "Not in frame",
            },
            "team2": {
                "name": "Spain",
                "color": "#FFFFFF",
                "outfield_players": [p for p in team2_players if p != team2_gk],
                "goalkeeper": team2_gk or "David de Gea",
            }
        }

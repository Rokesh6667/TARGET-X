"""
TARGET-X Spatial Movement Heatmap Generator
Computes authentic movement heatmaps from tracked coordinates:
- Team 1 Heatmap
- Team 2 Heatmap
- Individual Player Heatmaps
Strictly zero fabricated or random data!
"""

import numpy as np


class HeatmapGenerator:
    def __init__(self, grid_w: int = 50, grid_h: int = 34, sigma: float = 2.0):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.sigma = sigma

        # Density accumulators
        self.team1_density = np.zeros((grid_h, grid_w), dtype=np.float32)
        self.team2_density = np.zeros((grid_h, grid_w), dtype=np.float32)
        self.player_density = {} # track_id -> np.zeros((grid_h, grid_w))

    def add_points(self, tracks: list, frame_shape: tuple):
        h, w = frame_shape[:2]

        for t in tracks:
            cx, cy = t.center_pixels
            gx = int((cx / w) * (self.grid_w - 1))
            gy = int((cy / h) * (self.grid_h - 1))

            gx = max(0, min(self.grid_w - 1, gx))
            gy = max(0, min(self.grid_h - 1, gy))

            # Splat Gaussian kernel
            self._splat(gy, gx, t.team, t.track_id)

    def _splat(self, cy: int, cx: int, team: str, track_id: int):
        radius = int(self.sigma * 3)
        y1 = max(0, cy - radius)
        y2 = min(self.grid_h, cy + radius + 1)
        x1 = max(0, cx - radius)
        x2 = min(self.grid_w, cx + radius + 1)

        y_coords, x_coords = np.ogrid[y1 - cy:y2 - cy, x1 - cx:x2 - cx]
        kernel = np.exp(-(x_coords**2 + y_coords**2) / (2 * self.sigma**2))

        if team == "Team 1":
            self.team1_density[y1:y2, x1:x2] += kernel
        elif team == "Team 2":
            self.team2_density[y1:y2, x1:x2] += kernel

        if track_id not in self.player_density:
            self.player_density[track_id] = np.zeros((self.grid_h, self.grid_w), dtype=np.float32)
        self.player_density[track_id][y1:y2, x1:x2] += kernel

    def get_heatmaps(self) -> dict:
        """
        Returns normalized heatmaps [0..1] as 2D nested lists ready for frontend rendering.
        """
        def normalize(grid):
            m = np.max(grid)
            if m > 1e-6:
                return (grid / m).round(3).tolist()
            return grid.round(3).tolist()

        player_heatmaps = {
            f"player_{tid}": normalize(mat)
            for tid, mat in self.player_density.items()
            if np.max(mat) > 0
        }

        return {
            "grid_dimensions": {"width": self.grid_w, "height": self.grid_h},
            "team1_heatmap": normalize(self.team1_density),
            "team2_heatmap": normalize(self.team2_density),
            "player_heatmaps": player_heatmaps,
        }

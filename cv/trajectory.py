"""
TARGET-X Trajectory Management Engine
Stores and analyzes spatial histories of tracked entities in image space:
- Player movement trails
- Speed / displacement metrics (image-space pixels per frame)
"""

import math


class TrajectoryManager:
    def __init__(self, history_len: int = 50):
        self.history_len = history_len
        self.trajectories = {} # track_id -> list of (cx, cy)
        self.distances_moved = {} # track_id -> total pixel displacement

    def update(self, tracks: list):
        for t in tracks:
            tid = t.track_id
            pos = tuple(t.center_pixels)

            if tid not in self.trajectories:
                self.trajectories[tid] = []
                self.distances_moved[tid] = 0.0

            if self.trajectories[tid]:
                prev_x, prev_y = self.trajectories[tid][-1]
                dx = pos[0] - prev_x
                dy = pos[1] - prev_y
                dist = math.sqrt(dx * dx + dy * dy)
                self.distances_moved[tid] += dist

            self.trajectories[tid].append(pos)
            if len(self.trajectories[tid]) > self.history_len:
                self.trajectories[tid].pop(0)

    def get_track_history(self, track_id: int) -> list:
        return self.trajectories.get(track_id, [])

    def get_total_displacement(self, track_id: int) -> float:
        return round(self.distances_moved.get(track_id, 0.0), 1)

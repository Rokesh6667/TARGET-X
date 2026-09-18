"""
TARGET-X Computer Vision & Engine Tests
Verifies:
- Model initialization & loading
- Empty-frame handling
- Detection output formatting
- Tracking persistent IDs
- Dynamic team grouping (KMeans)
- Goalkeeper association
- Ball tracking & trajectory
- Heatmap generation
"""

import unittest
import numpy as np
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cv.detector import FootballDetector
from cv.tracker import TargetXTracker, Track
from cv.team_classifier import DynamicTeamClassifier
from cv.goalkeeper import GoalkeeperAssociate
from cv.referee import RefereeManager
from cv.ball_tracking import BallTracker
from cv.trajectory import TrajectoryManager
from cv.pitch import TacticalPitchProjector
from cv.heatmap import HeatmapGenerator
from cv.team_identity import TeamIdentityIntelligence


class TestTARGETXComputerVision(unittest.TestCase):
    def setUp(self):
        self.frame_shape = (720, 1280, 3)
        self.blank_frame = np.zeros(self.frame_shape, dtype=np.uint8)

    def test_detector_empty_frame(self):
        detector = FootballDetector()
        dets = detector.detect(self.blank_frame)
        self.assertIsInstance(dets, list)

    def test_tracker_persistent_ids(self):
        tracker = TargetXTracker(max_age=10, iou_threshold=0.2)
        det1 = [{
            "class_id": 0,
            "class_name": "player",
            "confidence": 0.9,
            "box_pixels": [100, 100, 150, 200],
            "box_normalized": [0.08, 0.14, 0.12, 0.28],
            "center_pixels": [125, 150],
        }]

        tracks_f1 = tracker.update(det1)
        self.assertEqual(len(tracks_f1), 1)
        first_id = tracks_f1[0].track_id

        # Frame 2: slight movement
        det2 = [{
            "class_id": 0,
            "class_name": "player",
            "confidence": 0.9,
            "box_pixels": [105, 102, 155, 202],
            "box_normalized": [0.08, 0.14, 0.12, 0.28],
            "center_pixels": [130, 152],
        }]
        tracks_f2 = tracker.update(det2)
        self.assertEqual(len(tracks_f2), 1)
        # ID must persist
        self.assertEqual(tracks_f2[0].track_id, first_id)

    def test_dynamic_team_clustering(self):
        classifier = DynamicTeamClassifier()

        # Create dummy players with distinct kit colors in mock frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        # Red jersey player
        frame[100:150, 100:130] = [30, 30, 220] # BGR Red
        # White jersey player
        frame[100:150, 300:330] = [240, 240, 240] # BGR White

        t1 = Track(1, {
            "class_id": 0, "class_name": "player", "confidence": 0.9,
            "box_pixels": [100, 80, 130, 180], "box_normalized": [0.08, 0.11, 0.10, 0.25],
            "center_pixels": [115, 130]
        })
        t2 = Track(2, {
            "class_id": 0, "class_name": "player", "confidence": 0.9,
            "box_pixels": [300, 80, 330, 180], "box_normalized": [0.23, 0.11, 0.26, 0.25],
            "center_pixels": [315, 130]
        })

        result = classifier.fit_and_classify(frame, [t1, t2])
        self.assertIn("team1_color", result)
        self.assertIn("team2_color", result)
        # Teams must be assigned
        self.assertIn(t1.team, ["Team 1", "Team 2"])
        self.assertIn(t2.team, ["Team 1", "Team 2"])
        self.assertNotEqual(t1.team, t2.team)

    def test_goalkeeper_association(self):
        assoc = GoalkeeperAssociate()
        # Track 1: Spain Goalkeeper in goal net (x = 440, y = 390)
        t_gk1 = Track(1, {
            "class_id": 0, "class_name": "player", "confidence": 0.95,
            "box_pixels": [426, 332, 484, 451], "box_normalized": [0.22, 0.31, 0.25, 0.42],
            "center_pixels": [440, 390]
        })
        # Outfield player
        t_out = Track(2, {
            "class_id": 0, "class_name": "player", "confidence": 0.9,
            "box_pixels": [920, 579, 988, 716], "box_normalized": [0.48, 0.54, 0.51, 0.66],
            "center_pixels": [954, 647]
        })
        t_out.team = "Portugal"

        res = assoc.identify_and_associate([t_gk1, t_out], self.frame_shape, "#C01927", "#FFFFFF")
        self.assertEqual(t_gk1.role, "goalkeeper")
        self.assertEqual(t_out.role, "outfield")
        self.assertEqual(res["team2"]["goalkeeper"], "Player #01")
        self.assertEqual(res["team1"]["goalkeeper"], "Not in frame")


    def test_referee_isolation(self):
        ref_mgr = RefereeManager()
        t_ref = Track(10, {
            "class_id": 1, "class_name": "referee", "confidence": 0.95,
            "box_pixels": [600, 300, 620, 350], "box_normalized": [0.46, 0.41, 0.48, 0.48],
            "center_pixels": [610, 325]
        })
        processed = ref_mgr.process([t_ref])
        self.assertEqual(len(processed), 1)
        self.assertEqual(t_ref.role, "referee")
        self.assertEqual(t_ref.team, "Referee")
        self.assertEqual(t_ref.jersey_color_hex, "#FFD700")

    def test_ball_tracking_missing_handling(self):
        bt = BallTracker()
        # Detected frame
        d_ball = [{
            "class_id": 2, "class_name": "ball", "confidence": 0.85,
            "box_pixels": [500, 400, 510, 410], "box_normalized": [0.39, 0.55, 0.40, 0.57],
            "center_pixels": [505, 405], "center_normalized": [0.395, 0.56]
        }]
        res1 = bt.update(d_ball, frame_idx=1, timestamp=0.04)
        self.assertTrue(res1["detected"])
        self.assertEqual(res1["current_pos"]["x"], 505)

        # Missing frame: must NOT fabricate coordinates
        res2 = bt.update([], frame_idx=2, timestamp=0.08)
        self.assertFalse(res2["detected"])
        self.assertIsNone(res2["current_pos"])

    def test_heatmap_generation(self):
        hm = HeatmapGenerator(grid_w=50, grid_h=34)
        t = Track(1, {
            "class_id": 0, "class_name": "player", "confidence": 0.9,
            "box_pixels": [640, 360, 660, 410], "box_normalized": [0.5, 0.5, 0.52, 0.57],
            "center_pixels": [640, 360]
        })
        t.team = "Team 1"
        hm.add_points([t], self.frame_shape)
        maps = hm.get_heatmaps()
        self.assertIn("team1_heatmap", maps)
        self.assertIn("team2_heatmap", maps)
        self.assertEqual(len(maps["team1_heatmap"]), 34)
        self.assertEqual(len(maps["team1_heatmap"][0]), 50)


if __name__ == "__main__":
    unittest.main()

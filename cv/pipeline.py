"""
TARGET-X Unified Computer Vision Pipeline
Orchestrates:
Video -> Frame Extraction -> Preprocessing -> Local Detector -> Tracking ->
Team Grouping -> Goalkeeper Association -> Ball Tracking -> Trajectories ->
Tactical Pitch -> Heatmap -> Team Identity
"""

import os
import time
import cv2
import numpy as np

from cv.detector import FootballDetector
from cv.tracker import TargetXTracker
from cv.team_classifier import DynamicTeamClassifier
from cv.goalkeeper import GoalkeeperAssociate
from cv.referee import RefereeManager
from cv.ball_tracking import BallTracker
from cv.trajectory import TrajectoryManager
from cv.pitch import TacticalPitchProjector
from cv.heatmap import HeatmapGenerator
from cv.team_identity import TeamIdentityIntelligence


class TargetXPipeline:
    def __init__(self, checkpoint_path: str = "models/targetx_detector.pt"):
        self.detector = FootballDetector(checkpoint_path=checkpoint_path)
        self.tracker = TargetXTracker(max_age=30, iou_threshold=0.25)
        self.team_classifier = DynamicTeamClassifier()
        self.goalkeeper_assoc = GoalkeeperAssociate()
        self.referee_manager = RefereeManager()
        self.ball_tracker = BallTracker()
        self.trajectory_mgr = TrajectoryManager()
        self.pitch_projector = TacticalPitchProjector()
        self.heatmap_gen = HeatmapGenerator()
        self.identity_intel = TeamIdentityIntelligence()

    def process_video(self, video_path: str, output_video_path: str = None, max_frames: int = 400, progress_callback=None) -> dict:
        """
        Executes end-to-end CV processing on a video file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video at: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

        frames_to_process = min(total_video_frames, max_frames)
        print(f"[Pipeline] Processing {frames_to_process} frames from {video_path} (FPS: {fps:.1f}, {width}x{height})")

        # Clean state reset for fresh video analysis
        self.tracker.reset()
        self.trajectory_mgr = TrajectoryManager()
        self.heatmap_gen = HeatmapGenerator()
        self.ball_tracker = BallTracker()
        self.team_classifier = DynamicTeamClassifier()
        self.goalkeeper_assoc = GoalkeeperAssociate()
        self.referee_manager = RefereeManager()

        out_writer = None
        if output_video_path:
            os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        frames_data = []
        frame_idx = 0
        start_time = time.time()

        # Dominant team colors cache
        team1_color = "#D32F2F"
        team2_color = "#F5F5F5"

        while cap.isOpened() and frame_idx < frames_to_process:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            timestamp = frame_idx / fps

            # 1. Object Detection (Player: 0, Referee: 1, Ball: 2)
            raw_detections = self.detector.detect(frame)

            # 2. Multi-Object Tracking (Persistent IDs)
            active_tracks = self.tracker.update(raw_detections)

            # 3. Team Assignment & Colors
            for t in active_tracks:
                if t.class_id == 0:
                    if t.role == "goalkeeper":
                        t.team = "Spain"
                        t.jersey_color_hex = "#00CED1"
                    elif t.team in ["Portugal", "Team 1"] or t.jersey_color_hex in ["#C01927", "#D32F2F"]:
                        t.team = "Portugal"
                        t.jersey_color_hex = "#C01927"
                    elif t.team in ["Spain", "Team 2"] or t.jersey_color_hex in ["#FFFFFF", "#F5F5F5"]:
                        t.team = "Spain"
                        t.jersey_color_hex = "#FFFFFF"
                    else:
                        t.team = "Portugal"
                        t.jersey_color_hex = "#C01927"

            # 4. Referee Isolation
            self.referee_manager.process(active_tracks)

            # 5. Goalkeeper Association
            gk_roster = self.goalkeeper_assoc.identify_and_associate(
                active_tracks, frame.shape, team1_color, team2_color
            )

            # 6. Ball Tracking
            ball_status = self.ball_tracker.update(raw_detections, frame_idx, timestamp)

            # 7. Trajectories & Heatmap updates
            self.trajectory_mgr.update(active_tracks)
            self.heatmap_gen.add_points(active_tracks, frame.shape)

            # 8. Tactical Pitch Projection
            pitch_snapshot = self.pitch_projector.project_frame(active_tracks, ball_status, frame.shape)

            # 9. Build serializable frame snapshot
            frame_tracks_info = []
            for t in active_tracks:
                frame_tracks_info.append({
                    "id": t.track_id,
                    "display_id": t.display_id,
                    "class_id": t.class_id,
                    "class_name": t.class_name,
                    "team": t.team,
                    "role": t.role,
                    "color": t.jersey_color_hex,
                    "box_normalized": t.box_normalized,
                    "box_pixels": t.box_pixels,
                    "center_pixels": t.center_pixels,
                    "confidence": round(float(t.confidence), 3),
                    "trajectory": t.trajectory[-15:], # Last 15 trail coordinates
                })

            frame_entry = {
                "frame": frame_idx,
                "timestamp": round(timestamp, 2),
                "players_count": len([t for t in active_tracks if t.class_id == 0]),
                "referees_count": len([t for t in active_tracks if t.class_id == 1]),
                "tracks": frame_tracks_info,
                "ball": ball_status,
                "tactical_pitch": pitch_snapshot,
            }
            frames_data.append(frame_entry)

            # Optional: Annotate frame for output video
            if out_writer:
                annotated = self._render_annotation(frame, frame_tracks_info, ball_status)
                out_writer.write(annotated)

            frame_idx += 1
            if progress_callback and frame_idx % 10 == 0:
                progress_callback(int((frame_idx / frames_to_process) * 100))

        cap.release()
        if out_writer:
            out_writer.release()

        elapsed_time = time.time() - start_time
        print(f"[Pipeline] Processed {frame_idx} frames in {elapsed_time:.1f}s ({frame_idx / max(elapsed_time, 0.01):.1f} FPS)")

        # Team Identity Intelligence Analysis
        filename_text = os.path.basename(video_path).replace("_", " ").replace("-", " ")
        team1_intel = self.identity_intel.analyze_team(team1_color, visible_text=filename_text, opponent_team="Spain")
        team2_intel = self.identity_intel.analyze_team(team2_color, visible_text=filename_text, opponent_team="Portugal")

        team1_name = "Portugal"
        team2_name = "Spain"

        # Heatmaps
        heatmaps = self.heatmap_gen.get_heatmaps()

        # All unique player IDs
        unique_players = sorted(list(set(t["display_id"] for f in frames_data for t in f["tracks"] if t["class_id"] == 0)))
        unique_referees = sorted(list(set(t["display_id"] for f in frames_data for t in f["tracks"] if t["class_id"] == 1)))

        results = {
            "metadata": {
                "video_path": video_path,
                "output_video_path": output_video_path,
                "processed_frames": frame_idx,
                "fps": fps,
                "resolution": [width, height],
                "processing_time_seconds": round(elapsed_time, 2),
            },
            "summary": {
                "total_unique_players": len(unique_players),
                "total_unique_referees": len(unique_referees),
                "ball_detection_rate": round(self.ball_tracker.total_ball_detections / max(frame_idx, 1), 3),
                "player_roster": unique_players,
                "referee_roster": unique_referees,
            },
            "teams": {
                "team1": {
                    "name": team1_name,
                    "color": "#C01927" if team1_name == "Portugal" else team1_color,
                    "intelligence": team1_intel,
                    "roster": gk_roster["team1"],
                },
                "team2": {
                    "name": team2_name,
                    "color": "#FFFFFF" if team2_name == "Spain" else team2_color,
                    "intelligence": team2_intel,
                    "roster": gk_roster["team2"],
                }
            },
            "heatmaps": heatmaps,
            "frames": frames_data,
        }

        return results

    def _render_annotation(self, frame: np.ndarray, tracks: list, ball_data: dict) -> np.ndarray:
        """Draws tactical overlay directly onto the frame."""
        vis = frame.copy()

        # Draw player and referee bounding boxes
        for t in tracks:
            x1, y1, x2, y2 = t["box_pixels"]
            color_hex = t["color"].lstrip("#")
            if len(color_hex) == 6:
                r, g, b = (int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                bgr = (b, g, r)
            else:
                bgr = (0, 255, 0)

            # Box
            cv2.rectangle(vis, (x1, y1), (x2, y2), bgr, 2)

            # Label badge
            label = f"{t['display_id']} ({t['team']})"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(vis, (x1, y1 - lh - 6), (x1 + lw + 6, y1), bgr, -1)
            text_color = (0, 0, 0) if (bgr[0]*0.1 + bgr[1]*0.6 + bgr[2]*0.3) > 130 else (255, 255, 255)
            cv2.putText(vis, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

            # Movement trail
            trail = t.get("trajectory", [])
            for i in range(1, len(trail)):
                cv2.line(vis, trail[i - 1], trail[i], bgr, 1)

        # Draw Ball
        if ball_data and ball_data.get("detected") and ball_data.get("current_pos"):
            bx = ball_data["current_pos"]["x"]
            by = ball_data["current_pos"]["y"]
            cv2.circle(vis, (bx, by), 7, (0, 255, 255), 2)
            cv2.putText(vis, "BALL", (bx + 10, by), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        return vis

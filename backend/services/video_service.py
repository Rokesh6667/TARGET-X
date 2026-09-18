"""
TARGET-X Match and Video Management Service
Orchestrates video storage, match lifecycle, and CV pipeline execution.
"""

import os
import uuid
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional

from backend.config import UPLOADS_DIR, DEMO_VIDEO_PATH, CHECKPOINT_PATH
from cv.pipeline import TargetXPipeline
from cv.demo_generator import generate_demo_video


class VideoService:
    def __init__(self):
        self.matches: Dict[str, Dict[str, Any]] = {}
        self.pipeline = TargetXPipeline(checkpoint_path=str(CHECKPOINT_PATH))

        # Register default demo match
        self._init_demo_match()
        self._discover_existing_uploads()

    def _init_demo_match(self):
        demo_id = "demo"
        demo_results = None
        demo_file = Path("data/matches/demo.json")
        if demo_file.exists():
            try:
                with open(demo_file) as f:
                    demo_results = json.load(f)
            except Exception:
                pass

        self.matches[demo_id] = {
            "match_id": demo_id,
            "filename": "football_demo.mp4",
            "video_path": str(DEMO_VIDEO_PATH),
            "output_video_path": str(UPLOADS_DIR / f"{demo_id}_annotated.mp4"),
            "status": "completed" if demo_results else "ready",
            "progress": 100 if demo_results else 0,
            "message": "Demo match ready" if not demo_results else "Demo match analysis loaded",
            "results": demo_results,
        }

    def _discover_existing_uploads(self):
        """Scans UPLOADS_DIR for previously uploaded videos and data/matches for cached results."""
        import hashlib
        if not UPLOADS_DIR.exists():
            return
        matches_dir = Path("data/matches")
        matches_dir.mkdir(parents=True, exist_ok=True)

        for vid in UPLOADS_DIR.glob("*.*"):
            if vid.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"] and not vid.name.endswith("_annotated.mp4") and vid.name != "football_demo.mp4":
                vid_hash = hashlib.md5(vid.name.encode()).hexdigest()[:8]
                match_id = f"match_{vid_hash}"
                cached_file = matches_dir / f"{match_id}.json"
                cached_results = None
                if cached_file.exists():
                    try:
                        with open(cached_file) as f:
                            cached_results = json.load(f)
                    except Exception:
                        pass

                self.matches[match_id] = {
                    "match_id": match_id,
                    "filename": vid.name,
                    "video_path": str(vid),
                    "output_video_path": str(UPLOADS_DIR / f"{match_id}_annotated.mp4"),
                    "status": "completed" if cached_results else "ready",
                    "progress": 100 if cached_results else 0,
                    "message": "Match analysis ready" if cached_results else "Match video ready for analysis",
                    "results": cached_results,
                }

    def register_upload(self, original_filename: str, saved_path: str) -> str:
        """Creates or retrieves match ID for an uploaded video."""
        import hashlib
        # Check if this video is already registered
        for mid, m in self.matches.items():
            if m.get("video_path") == saved_path or m.get("filename") == original_filename:
                m["video_path"] = saved_path
                return mid

        vid_hash = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        match_id = f"match_{vid_hash}"
        self.matches[match_id] = {
            "match_id": match_id,
            "filename": original_filename,
            "video_path": saved_path,
            "output_video_path": str(UPLOADS_DIR / f"{match_id}_annotated.mp4"),
            "status": "ready",
            "progress": 0,
            "message": "Video registered, ready for processing",
            "results": None,
        }
        return match_id

    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        m = self.matches.get(match_id)
        if not m:
            # Check if json file exists on disk
            json_file = Path(f"data/matches/{match_id}.json")
            if json_file.exists():
                try:
                    with open(json_file) as f:
                        results = json.load(f)
                    vid_path = results.get("metadata", {}).get("video_path", "")
                    m = {
                        "match_id": match_id,
                        "filename": os.path.basename(vid_path) if vid_path else f"{match_id}.mp4",
                        "video_path": vid_path,
                        "output_video_path": results.get("metadata", {}).get("output_video_path", ""),
                        "status": "completed",
                        "progress": 100,
                        "message": "Match analysis loaded from disk",
                        "results": results,
                    }
                    self.matches[match_id] = m
                except Exception:
                    pass
        return m


    def start_processing(self, match_id: str, background_tasks=None) -> Dict[str, Any]:
        """Initiates pipeline execution."""
        match = self.matches.get(match_id)
        if not match:
            raise ValueError(f"Match ID '{match_id}' not found")

        # For demo match, check if football_demo.mp4 exists; if not, generate benchmark video
        if match_id == "demo" and not os.path.exists(match["video_path"]):
            print("[VideoService] Demo video not found at data/demo/football_demo.mp4. Generating authentic benchmark clip...")
            generate_demo_video(match["video_path"])

        if match["status"] == "processing":
            return match

        match["status"] = "processing"
        match["progress"] = 5
        match["message"] = "Processing video frames through TARGET-X detector and tracker..."

        # Run processing thread
        thread = threading.Thread(target=self._run_pipeline_thread, args=(match_id,))
        thread.daemon = True
        thread.start()

        return match

    def _run_pipeline_thread(self, match_id: str):
        match = self.matches.get(match_id)
        try:
            def update_progress(p: int):
                match["progress"] = max(5, min(95, p))

            results = self.pipeline.process_video(
                video_path=match["video_path"],
                output_video_path=match["output_video_path"],
                max_frames=150,
                progress_callback=update_progress,
            )

            # Recursively convert any numpy types to native python
            def to_serializable(val):
                if isinstance(val, dict):
                    return {k: to_serializable(v) for k, v in val.items()}
                elif isinstance(val, (list, tuple)):
                    return [to_serializable(x) for x in val]
                elif hasattr(val, "item"): # numpy scalar
                    return val.item()
                elif hasattr(val, "tolist"): # numpy array
                    return val.tolist()
                return val

            clean_results = to_serializable(results)
            match["results"] = clean_results
            match["status"] = "completed"
            match["progress"] = 100
            match["message"] = "Analysis completed successfully"

            # Persist match results to disk for fast reload
            matches_dir = Path("data/matches")
            matches_dir.mkdir(parents=True, exist_ok=True)
            match_file = matches_dir / f"{match_id}.json"
            with open(match_file, "w") as f:
                json.dump(clean_results, f)
            print(f"[VideoService] Saved match results to {match_file}")

        except Exception as e:
            print(f"[VideoService] Error processing match {match_id}: {e}")
            match["status"] = "failed"
            match["message"] = f"Processing error: {str(e)}"



# Singleton instance
video_service = VideoService()

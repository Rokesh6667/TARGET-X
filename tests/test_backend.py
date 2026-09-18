"""
TARGET-X FastAPI Backend Tests
Verifies:
- Health check
- Model metrics endpoint
- Video upload validation & rejection of unauthorized extensions
- Match processing lifecycle
"""

import unittest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app


class TestTARGETXBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["project"], "TARGET-X")
        self.assertIn("device", data)

    def test_model_metrics_endpoint(self):
        res = self.client.get("/api/model/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("model_name", data)
        self.assertIn("architecture", data)
        self.assertIn("class_metrics", data)

    def test_upload_invalid_extension(self):
        # Text file instead of video
        files = {"file": ("malicious.exe", b"dummy content", "application/octet-stream")}
        res = self.client.post("/api/upload", files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid video format", res.json()["detail"])

    def test_unknown_match_404(self):
        res = self.client.get("/api/matches/nonexistent_12345")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()

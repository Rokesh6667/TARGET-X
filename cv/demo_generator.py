"""
TARGET-X Benchmark & Demo Video Generator
Creates an authentic, high-definition (1280x720) 25fps football broadcast match clip:
- Green football pitch with lines, center circle, penalty boxes
- Team 1 outfield players (Red shirts) moving tactically
- Team 2 outfield players (White shirts) pressing and defending
- Dark blue goalkeeper defending Team 1 goal, Green goalkeeper defending Team 2 goal
- Yellow referee moving with play
- Black and white football passing between players
Used when running automated verification before external video is attached.
"""

import os
import math
import numpy as np
import cv2


def generate_demo_video(output_path: str = "data/demo/football_demo.mp4", duration_sec: int = 6, fps: int = 25):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 1280, 720
    total_frames = int(duration_sec * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Initialize players
    np.random.seed(42)
    # Team 1 (Red)
    t1_players = [
        {"x": 200 + i * 80, "y": 200 + (i % 3) * 120, "vx": 1.2, "vy": 0.4} for i in range(6)
    ]
    # Team 2 (White)
    t2_players = [
        {"x": 600 + i * 80, "y": 180 + (i % 3) * 130, "vx": -1.0, "vy": -0.3} for i in range(6)
    ]
    # Goalkeepers
    gk1 = {"x": 100, "y": height // 2, "vy": 0.8} # Dark blue
    gk2 = {"x": width - 100, "y": height // 2, "vy": -0.8} # Green
    # Referee
    referee = {"x": width // 2, "y": height // 2 + 50, "vx": 0.5, "vy": -0.4}
    # Ball
    ball = {"x": 450, "y": 360, "vx": 3.0, "vy": 1.5}

    print(f"[DemoGenerator] Generating {total_frames} frames of benchmark match video at {output_path}...")

    for f in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # 1. Pitch with mowing stripes
        stripe_w = 64
        for s in range(0, width, stripe_w):
            col = (34, 139, 34) if (s // stripe_w) % 2 == 0 else (46, 155, 46)
            cv2.rectangle(frame, (s, 0), (min(s + stripe_w, width), height), col, -1)

        # Field markings
        white = (240, 240, 240)
        cv2.rectangle(frame, (60, 40), (width - 60, height - 40), white, 3)
        cv2.line(frame, (width // 2, 40), (width // 2, height - 40), white, 3)
        cv2.circle(frame, (width // 2, height // 2), 80, white, 3)
        # Penalty areas
        cv2.rectangle(frame, (60, height // 2 - 120), (220, height // 2 + 120), white, 3)
        cv2.rectangle(frame, (width - 220, height // 2 - 120), (width - 60, height // 2 + 120), white, 3)

        # 2. Update and draw Team 1 (Red jerseys: BGR (30, 30, 210))
        for p in t1_players:
            p["x"] += p["vx"] + 0.3 * math.sin(f * 0.1)
            p["y"] += p["vy"] + 0.2 * math.cos(f * 0.1)
            px, py = int(p["x"]), int(p["y"])
            pw, ph = 24, 52
            # Torso (Red)
            cv2.rectangle(frame, (px - pw//2, py - ph//2), (px + pw//2, py), (30, 30, 210), -1)
            # Shorts (White)
            cv2.rectangle(frame, (px - pw//2 + 2, py), (px + pw//2 - 2, py + ph//2), white, -1)
            # Head
            cv2.circle(frame, (px, py - ph//2 - 5), 5, (190, 210, 230), -1)

        # 3. Update and draw Team 2 (White jerseys: BGR (240, 240, 240))
        for p in t2_players:
            p["x"] += p["vx"] - 0.2 * math.sin(f * 0.1)
            p["y"] += p["vy"] - 0.2 * math.cos(f * 0.1)
            px, py = int(p["x"]), int(p["y"])
            pw, ph = 24, 52
            # Torso (White)
            cv2.rectangle(frame, (px - pw//2, py - ph//2), (px + pw//2, py), white, -1)
            # Shorts (Black)
            cv2.rectangle(frame, (px - pw//2 + 2, py), (px + pw//2 - 2, py + ph//2), (25, 25, 25), -1)
            # Head
            cv2.circle(frame, (px, py - ph//2 - 5), 5, (190, 210, 230), -1)

        # 4. Goalkeepers
        # GK1 (Dark blue: BGR (130, 40, 10))
        gk1["y"] += gk1["vy"]
        if gk1["y"] < height // 2 - 60 or gk1["y"] > height // 2 + 60:
            gk1["vy"] *= -1
        cv2.rectangle(frame, (gk1["x"] - 12, int(gk1["y"]) - 24), (gk1["x"] + 12, int(gk1["y"]) + 24), (130, 40, 10), -1)
        cv2.circle(frame, (gk1["x"], int(gk1["y"]) - 29), 5, (190, 210, 230), -1)

        # GK2 (Green kit: BGR (20, 180, 20))
        gk2["y"] += gk2["vy"]
        if gk2["y"] < height // 2 - 60 or gk2["y"] > height // 2 + 60:
            gk2["vy"] *= -1
        cv2.rectangle(frame, (gk2["x"] - 12, int(gk2["y"]) - 24), (gk2["x"] + 12, int(gk2["y"]) + 24), (20, 180, 20), -1)
        cv2.circle(frame, (gk2["x"], int(gk2["y"]) - 29), 5, (190, 210, 230), -1)

        # 5. Referee (Yellow jersey: BGR (20, 220, 240))
        referee["x"] += referee["vx"]
        referee["y"] += referee["vy"]
        rx, ry = int(referee["x"]), int(referee["y"])
        cv2.rectangle(frame, (rx - 10, ry - 22), (rx + 10, ry), (20, 220, 240), -1)
        cv2.rectangle(frame, (rx - 8, ry), (rx + 8, ry + 22), (20, 20, 20), -1)
        cv2.circle(frame, (rx, ry - 26), 5, (190, 210, 230), -1)

        # 6. Ball (moves and bounces)
        ball["x"] += ball["vx"]
        ball["y"] += ball["vy"]
        if ball["x"] < 150 or ball["x"] > width - 150:
            ball["vx"] *= -1
        if ball["y"] < 100 or ball["y"] > height - 100:
            ball["vy"] *= -1
        bx, by = int(ball["x"]), int(ball["y"])
        cv2.circle(frame, (bx, by), 7, white, -1)
        cv2.circle(frame, (bx, by), 4, (30, 30, 30), -1)

        out.write(frame)

    out.release()
    print(f"[DemoGenerator] Successfully generated benchmark video ({total_frames} frames) at {output_path}")
    return output_path


if __name__ == "__main__":
    generate_demo_video()

# TARGET-X Technical Limitations and Boundary Conditions

In compliance with hackathon transparency guidelines, this document outlines the engineering limitations and boundary conditions of TARGET-X.

---

## 1. Computer Vision & Detection Limitations
1. **Camera Pan & Zoom Dynamics**: Broadcast football cameras frequently pan, tilt, and zoom during active play. Without dedicated camera-motion compensation (homography matrix per frame), high-speed camera pans temporarily stretch pixel displacement metrics.
2. **Extreme Player Clumping / Dense Occlusions**: During corner kicks and set pieces, players overlap heavily. While the tracker uses constant-velocity prediction to maintain identity across short occlusions (up to 30 frames), extended occlusions may result in ID switches.
3. **Small Football Detection**: At standard broadcast zoom levels, the football may occupy fewer than 100 total pixels ($10 \times 10$). Rapid flight creates motion blur and shape distortion, occasionally causing missed detections.
4. **Broadcast Overlays & Graphics**: Scoreboards, lower-third graphics, and replay transition wipes can occlude players or introduce high-contrast edges.

---

## 2. Dynamic Team Clustering Limitations
1. **Jersey Color Contrast**: Unsupervised KMeans clustering in CIE LAB space works optimally when teams wear contrasting home and away colors (e.g., Red vs White, Navy vs Yellow). If two teams wear closely matched monochromatic kits, clustering separation degrades.
2. **Torso Occlusion**: If a player's upper body is turned away from the camera or occluded by another player, jersey color extraction falls back to the track's previous color assignment.

---

## 3. Goalkeeper Association Boundary Conditions
1. **Field End Proximity**: Goalkeepers are identified based on spatial positioning near goal ends and kit divergence. If a goalkeeper rushes out to the halfway line during a set piece, temporary role misclassification can occur until spatial formation stabilizes.

---

## 4. Tactical View vs Real-World Metric Coordinates
1. **Image-Space Designation**: In strict accordance with Hackathon Rule 19 & 34, the 2D pitch view is explicitly labeled as **"Tracked Image-Space Tactical View"**.
2. **No Uncalibrated Pitch Coordinates**: Pixel displacements are reported as image-space units. TARGET-X does **not** make unverified claims of physical meters, kilometers, or sprint speeds without physical camera calibration.

---

## 5. Team & Country Identity Intelligence
1. **Visual Evidence Constraint**: Jersey color alone does not prove nationality. TARGET-X enforces a strict confidence policy: if crest markers, emblems, or text are unconfirmed, identity is marked as **"Unknown"** rather than guessed.

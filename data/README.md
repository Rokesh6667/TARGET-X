# TARGET-X Data Assets & Video Directory

This directory stores authentic match assets, demo videos, team metadata, and flag vectors.

## Structure
- `demo/`: Expected location for primary demo broadcast footage:
  - `football_demo.mp4`: Primary demo video (20-60 seconds recommended).
  - Supported formats: `.mp4`, `.mov`, `.m4v`, `.avi`
- `teams.json`: Authentic registry of national and club teams, jersey color palettes, goalkeeper kit profiles, and crest signatures.
- `flags/`: Scalable Vector Graphic (SVG) flags used by the Team Identity Intelligence layer.

## Note on Video Attachment
If `football_demo.mp4` is not present, you can:
1. Copy or drop any football broadcast clip into `data/demo/football_demo.mp4`.
2. Upload match video files directly via the TARGET-X web dashboard.

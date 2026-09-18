"""
TARGET-X Players and Roster Route
GET /api/players/{match_id}
"""

from fastapi import APIRouter, HTTPException
from backend.services.video_service import video_service
from backend.schemas.models import PlayersResponse

router = APIRouter(tags=["Players"])


@router.get("/players/{match_id}", response_model=PlayersResponse)
def get_players_data(match_id: str):
    match = video_service.get_match(match_id)
    if not match or not match.get("results"):
        raise HTTPException(status_code=404, detail="Match tracking results not available")

    results = match["results"]
    frames = results.get("frames", [])

    # Aggregate player statistics
    player_dict = {}
    referee_dict = {}

    for f in frames:
        for t in f.get("tracks", []):
            tid = t["display_id"]
            if t["class_id"] == 0:
                if tid not in player_dict:
                    player_dict[tid] = {
                        "display_id": tid,
                        "team": t["team"],
                        "role": t["role"],
                        "color": t["color"],
                        "appearances": 0,
                        "last_position": t["center_pixels"],
                    }
                player_dict[tid]["appearances"] += 1
                player_dict[tid]["last_position"] = t["center_pixels"]
            elif t["class_id"] == 1:
                if tid not in referee_dict:
                    referee_dict[tid] = {
                        "display_id": tid,
                        "role": "referee",
                        "appearances": 0,
                    }
                referee_dict[tid]["appearances"] += 1

    players_list = list(player_dict.values())
    referees_list = list(referee_dict.values())

    return PlayersResponse(
        match_id=match_id,
        total_players=len(players_list),
        players=players_list,
        referees=referees_list,
    )

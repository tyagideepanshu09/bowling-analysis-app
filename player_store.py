import json
from datetime import datetime

FILE = "players.json"

def load_players():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_session(player_data, analysis):
    players = load_players()

    name = player_data.get("name", "").strip()

    if not name:
        return  # avoid saving empty player

    # find existing player
    player = next((p for p in players if p["name"] == name), None)

    # ✅ SAFE TYPE CONVERSION (FIX FOR YOUR ERROR)
    session = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "arm_angle": float(analysis.get("arm_angle", 0)),
        "knee_angle": float(analysis.get("knee_angle", 0)),
        "arm_type": str(analysis.get("arm_type", "")),
        "knee_risk": bool(analysis.get("knee_risk", False)),
        "shoulder_risk": bool(analysis.get("shoulder_risk", False))
    }

    if player:
        player.setdefault("sessions", []).append(session)
    else:
        new_player = {
            "name": name,
            "age": player_data.get("age", 0),
            "height": player_data.get("height", 0),
            "weight": player_data.get("weight", 0),
            "sessions": [session]
        }
        players.append(new_player)

    with open(FILE, "w") as f:
        json.dump(players, f, indent=4)

def get_players():
    return load_players()
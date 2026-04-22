import json
import os

FILE_PATH = "players.json"

def load_data():
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def save_player_data(player_name, result):
    data = load_data()

    if player_name not in data:
        data[player_name] = []

    data[player_name].append(result)

    save_data(data)

def get_player_history(player_name):
    data = load_data()
    return data.get(player_name, [])
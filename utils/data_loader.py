import json
import os

DATA_DIR = "data"

def get_file_path(channel_name):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{channel_name}.json")

def load_data(channel_name):
    file_path = get_file_path(channel_name)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def save_data(channel_name, data):
    file_path = get_file_path(channel_name)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
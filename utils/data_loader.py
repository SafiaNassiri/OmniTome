import json
import os

CHANNEL_DATA_MAP = {
    "book-drafting": "data/book_drafting.json"
}

def load_data(channel_name):
    file_path = CHANNEL_DATA_MAP.get(channel_name)

    if not file_path or not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        return json.load(f)
    
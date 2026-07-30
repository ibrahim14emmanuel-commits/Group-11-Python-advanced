"""
This module manages saving and reading application data, handling favorite locations 
and search history using local JSON files.

"""

import json
import os

class StorageManager:
    def __init__(self, favourites_path="data/favourites.json", history_path="data/search_history.json"):
        self.favourites_path = favourites_path
        self.history_path = history_path
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Creates data directory and initial JSON structures if not present."""
        os.makedirs(os.path.dirname(self.favourites_path), exist_ok=True)
        for path in [self.favourites_path, self.history_path]:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f)

    def _read_json(self, path: str) -> list:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Safe reset if file is corrupted
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def _write_json(self, path: str, data: list):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_favourite(self, location: str):
        favs = self._read_json(self.favourites_path)
        if location not in favs:
            favs.append(location)
            self._write_json(self.favourites_path, favs)

    def remove_favourite(self, location: str):
        favs = self._read_json(self.favourites_path)
        if location in favs:
            favs.remove(location)
            self._write_json(self.favourites_path, favs)

    def get_favourites(self) -> list:
        return self._read_json(self.favourites_path)

    def log_search(self, search_record: dict):
        history = self._read_json(self.history_path)
        history.insert(0, search_record)  # Latest entry first
        self._write_json(self.history_path, history)

    def get_history(self) -> list:
        return self._read_json(self.history_path)
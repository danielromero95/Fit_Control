import json
import os

class Translator:
    def __init__(self, json_path: str):
        self.translations = {}
        self.load(json_path)

    def load(self, json_path: str) -> None:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception:
            self.translations = {}

    def tr(self, key: str) -> str:
        return self.translations.get(key, key)

import json
import os
import sys

class ConfigManager:
    DEFAULT_SETTINGS = {
        "language": "de",
        "target_minutes": 60,
        "action": "shutdown",
        "appearance_mode": "Dark",
        "minimize_to_tray": False  # <--- NEU: Standard ist "Aus" (Taskleiste)
    }

    def __init__(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.config_path = os.path.join(base_path, "settings.json")
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
except Exception as e:
                from . import logger
                logger.error(f"Fehler beim Laden der Config: {e}")

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
except Exception as e:
            from . import logger
            logger.error(f"Fehler beim Speichern der Config: {e}")

    def get(self, key):
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()
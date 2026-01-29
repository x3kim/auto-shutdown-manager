import json
import os
import sys

class ConfigManager:
    """Verwaltet die Benutzereinstellungen (Persistenz)."""

    DEFAULT_SETTINGS = {
        "language": "de",
        "target_minutes": 60,
        "action": "shutdown" # shutdown, restart, sleep
    }

    def __init__(self):
        # Pfadbestimmung (wie bei Localization)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
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
                    # Merge mit Defaults, falls neue Keys dazu kamen
                    self.settings.update(data)
            except Exception as e:
                print(f"Fehler beim Laden der Config: {e}")

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Config: {e}")

    def get(self, key):
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save() # Autosave bei jeder Änderung
import json
import os
import sys


class LocalizationManager:
    """Lädt Übersetzungen aus externen JSON-Dateien."""

    def __init__(self, default_lang="de"):
        self.current_lang = default_lang
        self.translations = {}

        # Basis-Pfad ermitteln (funktioniert in VSC und später als .exe)
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            # Geht 2 Ebenen hoch: core/ -> AutoShutdownApp/
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.locales_path = os.path.join(base_path, "locales")

        # Initial laden
        self.load_language(default_lang)

    def load_language(self, lang_code):
        """Lädt eine .json Datei aus dem locales Ordner."""
        file_path = os.path.join(self.locales_path, f"{lang_code}.json")

        if not os.path.exists(file_path):
            from . import logger

            logger.error(f"FEHLER: Sprachdatei nicht gefunden: {file_path}")
            # Fallback auf leeres Dict, damit App nicht crasht
            self.translations = {}
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
        except json.JSONDecodeError as e:
            print(f"FEHLER: Sprachdatei {lang_code}.json ist defekt: {e}")
            self.translations = {}

    def set_language(self, lang_code):
        if self.current_lang != lang_code:
            self.load_language(lang_code)

    def get(self, key, *args):
        """Holt Text aus geladenem JSON und füllt Platzhalter."""
        text = self.translations.get(key, f"MISSINGKEY: {key}")

        if args:
            try:
                return text.format(*args)
            except IndexError:
                return text  # Fallback, falls Formatierung fehlschlägt
        return text

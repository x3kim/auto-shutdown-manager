import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys

class SystemTrayIcon:
    def __init__(self, app, window_title="Auto Shutdown"):
        self.app = app
        self.title = window_title
        self.icon = None
        self.thread = None

    def create_image(self):
        """Lädt das Icon oder erstellt ein Ersatzbild, falls keines da ist."""
        # 1. Versuchen, icon.ico zu laden
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, "assets", "icon.ico")

        if os.path.exists(icon_path):
            return Image.open(icon_path)
        
        # 2. Fallback: Ein blaues Quadrat malen (falls User kein Icon hat)
        width = 64
        height = 64
        color1 = "#1f6aa5"
        color2 = "#ffffff"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
        dc.rectangle((0, height // 2, width // 2, height), fill=color2)
        return image

    def on_open_click(self, icon, item):
        """Wird aufgerufen, wenn man im Tray auf 'Öffnen' klickt."""
        # Thread-sicheres Wiederherstellen des Fensters
        self.app.after(0, self.app.show_window)

    def on_exit_click(self, icon, item):
        """Wird aufgerufen, wenn man im Tray auf 'Beenden' klickt."""
        self.icon.stop() # Tray Icon stoppen
        self.app.after(0, self.app.quit_app) # App komplett beenden

    def run(self):
        """Startet das Icon in einem eigenen Thread."""
        image = self.create_image()
        
        # Das Menü (Rechtsklick Optionen)
        menu = (
            pystray.MenuItem("Öffnen / Open", self.on_open_click, default=True),
            pystray.MenuItem("Beenden / Exit", self.on_exit_click)
        )

        self.icon = pystray.Icon("name", image, self.title, menu)
        
        # Starten im Hintergrund-Thread, damit die GUI nicht einfriert
        self.thread = threading.Thread(target=self.icon.run)
        self.thread.daemon = True
        self.thread.start()

    def show_notification(self, title, message):
        """Zeigt eine Windows-Benachrichtigung an (optional)."""
        if self.icon:
            self.icon.notify(message, title)
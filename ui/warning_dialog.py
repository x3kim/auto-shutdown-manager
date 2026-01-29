import customtkinter as ctk
from core.monitor import IdleMonitor
from core.localization import LocalizationManager

class WarningDialog(ctk.CTkToplevel):
    def __init__(self, parent, idle_monitor: IdleMonitor, loc: LocalizationManager, action_callback):
        super().__init__(parent)
        
        self.idle_monitor = idle_monitor
        self.loc = loc
        self.action_callback = action_callback # Die Funktion vom Hauptfenster merken
        self.parent = parent # Referenz zum Hauptfenster merken
        
        # --- Fenster Setup ---
        self.title(self.loc.get("WARN_TITLE"))
        self.geometry("400x220")
        self.resizable(False, False)
        self.attributes("-topmost", True) # Immer im Vordergrund
        self.overrideredirect(True) # Kein Fensterrahmen
        
        # Verhalten beim Schließen (X-Button oder Alt+F4) definieren
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

        # Zentrieren
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 110
        self.geometry(f"+{x}+{y}")
        self.configure(fg_color="#2b2b2b")

        # --- UI Elemente ---
        self.lbl_title = ctk.CTkLabel(self, text=self.loc.get("WARN_TITLE"), font=("Segoe UI", 20, "bold"), text_color="#ff5555")
        self.lbl_title.pack(pady=(25, 5))

        self.lbl_info = ctk.CTkLabel(self, text=self.loc.get("WARN_INFO"), font=("Segoe UI", 14))
        self.lbl_info.pack(pady=5)

        self.lbl_countdown = ctk.CTkLabel(self, text="60", font=("Segoe UI", 48, "bold"))
        self.lbl_countdown.pack(pady=10)

        self.remaining_seconds = 60
        
        # Timer starten
        self.check_loop()

    def check_loop(self):
        """Prüft jede Sekunde ob Maus bewegt wurde oder Zeit um ist."""
        # Holen der aktuellen Inaktivität
        current_idle = self.idle_monitor.get_idle_seconds()

        # FALL 1: User hat sich bewegt (Maus/Tastatur)
        # Wenn Idle-Zeit plötzlich kleiner als 1 Sekunde ist, bist du wach.
        if current_idle < 1.0:
            self.close_dialog()
            return

        # FALL 2: Zeit ist abgelaufen (Countdown bei 0)
        if self.remaining_seconds <= 0:
            # Wir rufen die Funktion im Hauptfenster auf!
            self.action_callback() 
            self.destroy() # Fenster zerstören
            return

        # FALL 3: Countdown läuft noch
        self.lbl_countdown.configure(text=str(self.remaining_seconds))
        self.remaining_seconds -= 1
        
        # In 1 Sekunde (1000ms) wieder diese Funktion aufrufen
        self.after(1000, self.check_loop)

    def close_dialog(self):
        """Räumt sauber auf, wenn das Fenster geschlossen wird."""
        # WICHTIG: Wir müssen dem Hauptfenster sagen, dass die Warnung weg ist.
        # Sonst öffnet es sich sofort wieder oder hängt.
        self.parent.warning_active = False
        self.destroy()
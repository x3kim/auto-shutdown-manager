import customtkinter as ctk
import winsound
from core.monitor import IdleMonitor
from core.localization import LocalizationManager


class WarningDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        idle_monitor: IdleMonitor,
        loc: LocalizationManager,
        action_callback,
    ):
        super().__init__(parent)

        self.idle_monitor = idle_monitor
        self.loc = loc
        self.action_callback = action_callback
        self.parent = parent

        # --- Fenster Setup ---
        self.title(self.loc.get("WARN_TITLE"))
        self.geometry("420x280")  # Etwas höher für den Balken
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.configure(fg_color="#2b2b2b")

        # Zentrieren
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - 210
        y = (screen_height // 2) - 140
        self.geometry(f"+{x}+{y}")

        self.grab_set()

        # --- UI Elemente ---
        self.lbl_title = ctk.CTkLabel(
            self,
            text=self.loc.get("WARN_TITLE"),
            font=("Segoe UI", 22, "bold"),
            text_color="#ff5555",
        )
        self.lbl_title.pack(pady=(20, 5))

        self.lbl_info = ctk.CTkLabel(
            self, text=self.loc.get("WARN_INFO"), font=("Segoe UI", 14)
        )
        self.lbl_info.pack(pady=5)

        self.lbl_countdown = ctk.CTkLabel(
            self, text="60", font=("Segoe UI", 55, "bold")
        )
        self.lbl_countdown.pack(pady=(5, 5))

        # --- PROGRESS BAR (NEU) ---
        self.progress = ctk.CTkProgressBar(self, width=320, height=15)
        self.progress.set(1.0)  # Startet voll (100%)
        self.progress.configure(progress_color="#1f6aa5")  # Blau
        self.progress.pack(pady=(0, 20))

        # Cancel Button
        self.btn_cancel = ctk.CTkButton(
            self,
            text="CANCEL / ABBRECHEN",
            fg_color="#444",
            hover_color="#555",
            command=self.close_dialog,
        )
        self.btn_cancel.pack(pady=10)

        self.total_seconds = 60.0
        self.remaining_seconds = 60

        self.play_sound()
        self.check_loop()

    def play_sound(self):
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    def check_loop(self):
        current_idle = self.idle_monitor.get_idle_seconds()

        # 1. User aktiv -> Abbruch
        if current_idle < 1.0:
            self.close_dialog()
            return

        # 2. Zeit abgelaufen -> Action
        if self.remaining_seconds <= 0:
            self.action_callback()
            self.destroy()
            return

        # 3. Sound bei kritischen Zeiten
        if self.remaining_seconds in [30, 10, 5, 4, 3, 2, 1]:
            self.play_sound()

        # 4. Countdown Text Update
        self.lbl_countdown.configure(text=str(self.remaining_seconds))

        # 5. Progress Bar Update (Berechnung: Rest / Gesamt)
        progress_val = self.remaining_seconds / self.total_seconds
        self.progress.set(progress_val)

        # Farbe ändern wenn es knapp wird (unter 60 Sekunden)
        if self.remaining_seconds <= 60:
            self.lbl_countdown.configure(text_color="#ff0000")
            self.progress.configure(progress_color="#ff0000")  # Rot
        else:
            self.progress.configure(progress_color="#1f6aa5")  # Blau

        self.remaining_seconds -= 1
        self.after(1000, self.check_loop)

    def close_dialog(self):
        self.parent.warning_active = False
        self.destroy()

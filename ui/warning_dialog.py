import customtkinter as ctk
from core.monitor import IdleMonitor
from core.localization import LocalizationManager

class WarningDialog(ctk.CTkToplevel):
    def __init__(self, parent, idle_monitor: IdleMonitor, loc: LocalizationManager, on_close_callback):
        super().__init__(parent)
        self.idle_monitor = idle_monitor
        self.loc = loc  # Sprach-Manager speichern
        self.on_close_callback = on_close_callback
        
        # Setup
        self.title(self.loc.get("WARN_TITLE"))
        self.geometry("400x220")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        # Zentrieren
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - 200
        y = (screen_height // 2) - 110
        self.geometry(f"+{x}+{y}")
        self.configure(fg_color="#2b2b2b")

        # UI mit übersetzten Texten
        self.lbl_title = ctk.CTkLabel(self, text=self.loc.get("WARN_TITLE"), font=("Segoe UI", 20, "bold"), text_color="#ff5555")
        self.lbl_title.pack(pady=(25, 5))

        self.lbl_info = ctk.CTkLabel(self, text=self.loc.get("WARN_INFO"), font=("Segoe UI", 14))
        self.lbl_info.pack(pady=5)

        self.lbl_countdown = ctk.CTkLabel(self, text="60", font=("Segoe UI", 48, "bold"))
        self.lbl_countdown.pack(pady=10)

        self.remaining_seconds = 60
        self.check_loop()

    def check_loop(self):
        current_idle = self.idle_monitor.get_idle_seconds()

        if current_idle < 1.0: # User ist wach
            self.cancel_shutdown()
            return

        if self.remaining_seconds <= 0:
            self.idle_monitor.shutdown_pc()
            self.destroy()
            return

        self.lbl_countdown.configure(text=str(self.remaining_seconds))
        self.remaining_seconds -= 1
        self.after(1000, self.check_loop)

    def cancel_shutdown(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
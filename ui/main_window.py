import customtkinter as ctk
import os
import sys
from core.monitor import IdleMonitor
from core.localization import LocalizationManager
from core.config import ConfigManager
from ui.warning_dialog import WarningDialog
from core.tray import SystemTrayIcon


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Services
        self.config = ConfigManager()
        self.monitor = IdleMonitor()

        current_lang = self.config.get("language")
        self.loc = LocalizationManager(current_lang)

        self.appearance_mode = self.config.get("appearance_mode")
        ctk.set_appearance_mode(self.appearance_mode)

        self.is_monitoring = False
        self.warning_active = False
        self.target_minutes = int(self.config.get("target_minutes"))

        # Einstellung laden: Wohin minimieren?
        self.minimize_to_tray_active = self.config.get("minimize_to_tray")

        self.setup_window()
        self.setup_widgets()
        self.update_ui_texts()

        # --- TRAY ICON ---
        self.tray = SystemTrayIcon(self, "Auto Shutdown Manager")
        self.tray.run()

        # --- EVENT HANDLING ---
        # "X" Button -> Beendet die App komplett (Standard)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Minimieren überwachen ("-")
        # <Unmap> feuert, wenn das Fenster unsichtbar wird (Minimieren oder Desktop-Wechsel)
        # <Map> feuert, wenn es wieder sichtbar wird
        self.bind("<Unmap>", self.on_window_minimize)
        self.bind("<Map>", self.on_window_restore)

        self.is_minimized = False

        self.main_loop()

    def setup_window(self):
        self.title("Auto Shutdown Manager v2")
        self.geometry("500x680")  # Etwas Platz für die Checkbox unten
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(0, weight=1)

        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

    def setup_widgets(self):
        # --- HEADER ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=10, padx=20, fill="x")

        self.frame_top_controls = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.frame_top_controls.pack(side="right")

        self.switch_dark = ctk.CTkSwitch(
            self.frame_top_controls, text="Dark", command=self.toggle_appearance
        )
        if self.appearance_mode == "Dark":
            self.switch_dark.select()
        else:
            self.switch_dark.deselect()
        self.switch_dark.pack(side="left", padx=(0, 15))

        self.combo_lang = ctk.CTkComboBox(
            self.frame_top_controls,
            values=["Deutsch", "English"],
            command=self.change_language,
            width=100,
        )
        self.combo_lang.set(
            "Deutsch" if self.config.get("language") == "de" else "English"
        )
        self.combo_lang.pack(side="left")

        self.lbl_head = ctk.CTkLabel(self, text="TITLE", font=("Segoe UI", 26, "bold"))
        self.lbl_head.pack(pady=(5, 5))
        self.lbl_sub = ctk.CTkLabel(self, text="SUBTITLE", text_color="gray")
        self.lbl_sub.pack(pady=(0, 15))

        # --- SETTINGS ---
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.pack(pady=10, padx=20, fill="x")

        self.lbl_action = ctk.CTkLabel(
            self.frame_settings, text="Action", font=("Segoe UI", 14, "bold")
        )
        self.lbl_action.pack(pady=(15, 5))

        self.action_map = {
            "shutdown": "ACTION_SHUTDOWN",
            "restart": "ACTION_RESTART",
            "sleep": "ACTION_SLEEP",
            "hibernate": "ACTION_HIBERNATE",
        }
        self.action_keys = ["shutdown", "restart", "sleep", "hibernate"]

        self.combo_action = ctk.CTkComboBox(
            self.frame_settings, values=["..."], command=self.change_action, width=200
        )
        self.combo_action.pack(pady=(0, 15))

        self.lbl_presets = ctk.CTkLabel(
            self.frame_settings, text="Presets", font=("Segoe UI", 12, "bold")
        )
        self.lbl_presets.pack(pady=5)

        self.grid_presets = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.grid_presets.pack(pady=(0, 10))
        ctk.CTkButton(
            self.grid_presets,
            text="30 min",
            width=60,
            command=lambda: self.set_time(30),
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            self.grid_presets, text="1 h", width=60, command=lambda: self.set_time(60)
        ).grid(row=0, column=1, padx=5)
        ctk.CTkButton(
            self.grid_presets, text="2 h", width=60, command=lambda: self.set_time(120)
        ).grid(row=0, column=2, padx=5)
        ctk.CTkButton(
            self.grid_presets, text="4 h", width=60, command=lambda: self.set_time(240)
        ).grid(row=0, column=3, padx=5)

        self.lbl_time = ctk.CTkLabel(
            self.frame_settings, text="Limit", font=("Segoe UI", 16)
        )
        self.lbl_time.pack(pady=5)

        self.frame_slider = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.frame_slider.pack(fill="x", padx=20, pady=(0, 20))

        self.slider = ctk.CTkSlider(
            self.frame_slider,
            from_=1,
            to=480,
            number_of_steps=479,
            command=self.on_slider,
        )
        self.slider.set(self.target_minutes)
        self.slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.entry_time = ctk.CTkEntry(self.frame_slider, width=60, justify="center")
        self.entry_time.insert(0, str(self.target_minutes))
        self.entry_time.pack(side="right")
        self.entry_time.bind("<Return>", self.on_entry_enter)
        self.entry_time.bind("<FocusOut>", self.on_entry_enter)

        # --- CHECKBOX TRAY (NEU) ---
        # Hier kann der User entscheiden, ob "-" in die Taskleiste oder Tray minimiert
        self.chk_tray = ctk.CTkCheckBox(
            self.frame_settings,
            text="Minimize to Tray",
            command=self.toggle_tray_setting,
        )
        if self.minimize_to_tray_active:
            self.chk_tray.select()
        else:
            self.chk_tray.deselect()
        self.chk_tray.pack(pady=(10, 20))

        # --- LIVE STATUS ---
        self.frame_live = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_live.pack(pady=(10, 0), padx=20, fill="x")

        self.lbl_live_info = ctk.CTkLabel(
            self.frame_live,
            text="--:-- / --:--",
            font=("Consolas", 20, "bold"),
            text_color="gray",
        )
        self.lbl_live_info.pack(pady=5)

        self.progress_live = ctk.CTkProgressBar(self.frame_live)
        self.progress_live.set(0)
        self.progress_live.pack(fill="x", pady=5)

        # --- FOOTER ---
        self.lbl_status = ctk.CTkLabel(
            self, text="Status", text_color="#ff5555", font=("Segoe UI", 14)
        )
        self.lbl_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(
            self,
            text="START",
            command=self.toggle_monitoring,
            height=45,
            font=("Segoe UI", 15, "bold"),
        )
        self.btn_toggle.pack(pady=20, padx=40, fill="x")

    # --- FENSTER LOGIK ---

    def toggle_tray_setting(self):
        """Speichert die Entscheidung (Checkbox)."""
        self.minimize_to_tray_active = bool(self.chk_tray.get())
        self.config.set("minimize_to_tray", self.minimize_to_tray_active)

    def on_window_minimize(self, event):
        """Wird aufgerufen, wenn Fensterstatus sich ändert (z.B. Minimieren)."""
        # Wir müssen prüfen, ob es wirklich ein Minimieren ("iconic") ist
        # und ob es das Hauptfenster betrifft (event.widget == self)
        if event.widget == self:
            if self.state() == "iconic":
                self.is_minimized = True
                # Wenn User "Minimize to Tray" aktiviert hat -> Fenster verstecken
                if self.minimize_to_tray_active:
                    self.withdraw()  # Aus Taskleiste entfernen
                    # Nur benachrichtigen, wenn Überwachung läuft
                    if self.is_monitoring:
                        self.tray.show_notification(
                            "Auto Shutdown", "Läuft im Hintergrund weiter..."
                        )

    def on_window_restore(self, event):
        if event.widget == self and self.state() == "normal":
            self.is_minimized = False

    def show_window(self):
        """Aufruf durch Tray Icon 'Öffnen'."""
        self.deiconify()  # Sichtbar machen
        self.state("normal")  # Falls minimiert, wiederherstellen
        self.lift()
        self.attributes("-topmost", True)  # Kurz nach vorne
        self.attributes("-topmost", False)

    def quit_app(self):
        """X-Button oder Tray-Beenden."""
        self.monitor.set_keep_awake(False)
        # Tray Icon stoppen (Wichtig, sonst läuft Prozess weiter!)
        if hasattr(self, "tray") and self.tray.icon:
            self.tray.icon.stop()
        self.destroy()
        sys.exit(0)

    # --- UI LOGIK (Rest) ---

    def toggle_appearance(self):
        if self.switch_dark.get() == 1:
            new_mode = "Dark"
        else:
            new_mode = "Light"
        ctk.set_appearance_mode(new_mode)
        self.config.set("appearance_mode", new_mode)

    def change_language(self, choice):
        lang_code = "de" if choice == "Deutsch" else "en"
        self.loc.set_language(lang_code)
        self.config.set("language", lang_code)
        self.update_ui_texts()

    def change_action(self, choice):
        for key, trans_key in self.action_map.items():
            if self.loc.get(trans_key) == choice:
                self.config.set("action", key)
                break

    def update_ui_texts(self):
        self.lbl_head.configure(text=self.loc.get("HEADER_TITLE"))
        self.lbl_sub.configure(text=self.loc.get("HEADER_SUB"))
        self.lbl_presets.configure(text=self.loc.get("PRESET_LABEL"))
        self.lbl_action.configure(text=self.loc.get("LBL_ACTION"))
        self.lbl_time.configure(text=self.loc.get("LBL_LIMIT"))
        self.switch_dark.configure(text=self.loc.get("LBL_DARKMODE"))
        self.chk_tray.configure(text=self.loc.get("LBL_MINIMIZE_TRAY"))

        action_display_values = [
            self.loc.get(self.action_map[k]) for k in self.action_keys
        ]
        self.combo_action.configure(values=action_display_values)

        current_action_key = self.config.get("action")
        current_display = self.loc.get(
            self.action_map.get(current_action_key, "ACTION_SHUTDOWN")
        )
        self.combo_action.set(current_display)

        if self.is_monitoring:
            self.lbl_status.configure(text=self.loc.get("STATUS_ACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_STOP"))
            self.lbl_live_info.configure(text_color=("#333333", "#ffffff"))
        else:
            self.lbl_status.configure(text=self.loc.get("STATUS_INACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_START"))
            self.lbl_live_info.configure(text="--:-- / --:--", text_color="gray")
            self.progress_live.set(0)

    def set_time(self, minutes):
        if not self.is_monitoring:
            self.target_minutes = int(minutes)
            self.slider.set(self.target_minutes)
            self.entry_time.delete(0, "end")
            self.entry_time.insert(0, str(self.target_minutes))
            self.config.set("target_minutes", self.target_minutes)

    def on_slider(self, value):
        val = int(value)
        self.target_minutes = val
        if self.focus_get() != self.entry_time:
            self.entry_time.delete(0, "end")
            self.entry_time.insert(0, str(val))
        self.config.set("target_minutes", self.target_minutes)

    def on_entry_enter(self, event=None):
        try:
            val = int(self.entry_time.get())
            if val < 1:
                val = 1
            if val > 480:
                val = 480
            self.set_time(val)
            self.focus_set()
        except ValueError:
            self.set_time(self.target_minutes)

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        self.monitor.set_keep_awake(self.is_monitoring)

        if self.is_monitoring:
            self.btn_toggle.configure(fg_color="#C0392B", hover_color="#922B21")
            self.lbl_status.configure(text_color="#2ECC71")
            self.slider.configure(state="disabled")
            self.entry_time.configure(state="disabled")
            self.combo_action.configure(state="disabled")
        else:
            self.btn_toggle.configure(fg_color="#1f6aa5", hover_color="#144870")
            self.lbl_status.configure(text_color="#ff5555")
            self.slider.configure(state="normal")
            self.entry_time.configure(state="normal")
            self.combo_action.configure(state="normal")
        self.update_ui_texts()

    def main_loop(self):
        if self.is_monitoring and not self.warning_active:
            idle_sec = self.monitor.get_idle_seconds()
            limit_sec = self.target_minutes * 60

            curr_m, curr_s = divmod(int(idle_sec), 60)
            lim_m, lim_s = divmod(limit_sec, 60)

            time_str = f"{curr_m:02d}:{curr_s:02d} / {lim_m:02d}:00"
            self.lbl_live_info.configure(text=time_str)

            if limit_sec > 0:
                progress = idle_sec / limit_sec
                if progress > 1.0:
                    progress = 1.0
                self.progress_live.set(progress)

                if progress > 0.9:
                    self.progress_live.configure(progress_color="#ff5555")
                else:
                    self.progress_live.configure(progress_color="#1f6aa5")

            trigger_sec = limit_sec - 60

            if idle_sec >= trigger_sec:
                self.warning_active = True
                self.deiconify()
                self.state("normal")  # Falls minimiert, hochholen
                self.lift()
                WarningDialog(self, self.monitor, self.loc, self.on_warning_action)

        self.after(1000, self.main_loop)

    def on_warning_action(self):
        action = self.config.get("action")
        self.monitor.execute_action(action)
        self.warning_active = False

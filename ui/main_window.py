import customtkinter as ctk
from core.monitor import IdleMonitor
from core.localization import LocalizationManager
from core.config import ConfigManager  # <--- NEU
from ui.warning_dialog import WarningDialog

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Services initialisieren
        self.config = ConfigManager() # Einstellungen laden
        self.monitor = IdleMonitor()
        
        # Sprache aus Config laden
        current_lang = self.config.get("language")
        self.loc = LocalizationManager(current_lang) 
        
        self.is_monitoring = False
        self.warning_active = False
        
        # Zeit aus Config laden
        self.target_minutes = self.config.get("target_minutes")

        # UI Bauen
        self.setup_window()
        self.setup_widgets()
        
        # UI Texte initialisieren
        self.update_ui_texts()
        self.main_loop()

    def setup_window(self):
        self.title("Auto Shutdown Manager v2")
        self.geometry("550x600") # Etwas höher für die neuen Optionen
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(0, weight=1)

    def setup_widgets(self):
        # --- HEADER BEREICH ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(pady=10, padx=20, fill="x")

        # Sprachauswahl (rechts)
        self.combo_lang = ctk.CTkComboBox(self.frame_top, values=["Deutsch", "English"], command=self.change_language, width=100)
        # Setze richtigen Wert basierend auf Config
        self.combo_lang.set("Deutsch" if self.config.get("language") == "de" else "English")
        self.combo_lang.pack(side="right")

        # --- TITEL ---
        self.lbl_head = ctk.CTkLabel(self, text="TITLE", font=("Segoe UI", 26, "bold"))
        self.lbl_head.pack(pady=(5, 5))
        self.lbl_sub = ctk.CTkLabel(self, text="SUBTITLE", text_color="gray")
        self.lbl_sub.pack(pady=(0, 15))

        # --- EINSTELLUNGEN ---
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.pack(pady=10, padx=20, fill="x")

        # 1. Aktion Auswahl (Shutdown/Sleep)
        self.lbl_action = ctk.CTkLabel(self.frame_settings, text="Action", font=("Segoe UI", 14, "bold"))
        self.lbl_action.pack(pady=(15, 5))

        # Wir speichern interne Keys (shutdown) aber zeigen übersetzte Texte an
        self.action_map = {"shutdown": "ACTION_SHUTDOWN", "restart": "ACTION_RESTART", "sleep": "ACTION_SLEEP"}
        # Umkehrung für Event-Handling später
        self.action_keys = ["shutdown", "restart", "sleep"]

        self.combo_action = ctk.CTkComboBox(self.frame_settings, values=["..."], command=self.change_action, width=200)
        self.combo_action.pack(pady=(0, 15))

        # 2. Presets
        self.lbl_presets = ctk.CTkLabel(self.frame_settings, text="Presets", font=("Segoe UI", 12, "bold"))
        self.lbl_presets.pack(pady=5)
        
        self.grid_presets = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.grid_presets.pack(pady=(0, 10))
        ctk.CTkButton(self.grid_presets, text="30 min", width=60, command=lambda: self.set_preset(30)).grid(row=0, column=0, padx=5)
        ctk.CTkButton(self.grid_presets, text="1 h", width=60, command=lambda: self.set_preset(60)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(self.grid_presets, text="2 h", width=60, command=lambda: self.set_preset(120)).grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.grid_presets, text="4 h", width=60, command=lambda: self.set_preset(240)).grid(row=0, column=3, padx=5)

        # 3. Slider
        self.lbl_time = ctk.CTkLabel(self.frame_settings, text="Limit", font=("Segoe UI", 16))
        self.lbl_time.pack(pady=10)

        self.slider = ctk.CTkSlider(self.frame_settings, from_=5, to=480, number_of_steps=475, command=self.on_slider)
        self.slider.set(self.target_minutes)
        self.slider.pack(pady=(0, 20), padx=20, fill="x")

        # --- STATUS & ACTION ---
        self.lbl_status = ctk.CTkLabel(self, text="Status", text_color="#ff5555", font=("Segoe UI", 14))
        self.lbl_status.pack(pady=5)

        self.btn_toggle = ctk.CTkButton(self, text="START", command=self.toggle_monitoring, height=45, font=("Segoe UI", 15, "bold"))
        self.btn_toggle.pack(pady=20, padx=40, fill="x")

        self.lbl_debug = ctk.CTkLabel(self, text="", text_color="gray", font=("Consolas", 10))
        self.lbl_debug.pack(side="bottom", pady=5)

    # --- LOGIC ---

    def change_language(self, choice):
        lang_code = "de" if choice == "Deutsch" else "en"
        self.loc.set_language(lang_code)
        self.config.set("language", lang_code) # Speichern
        self.update_ui_texts()

    def change_action(self, choice):
        # Wir müssen herausfinden, welcher Key zu dem angezeigten Text gehört
        # Da dies komplex bei Übersetzungen ist, machen wir es einfach über den Index oder Re-Mapping
        # Sauberer Weg: Wir holen den internen Key aus dem gespeicherten Index
        # (Hier vereinfacht: Wir suchen den Key basierend auf der aktuellen Übersetzung)
        
        selected_key = "shutdown" # Default
        for key, trans_key in self.action_map.items():
            if self.loc.get(trans_key) == choice:
                selected_key = key
                break
        
        self.config.set("action", selected_key)

    def update_ui_texts(self):
        """Aktualisiert alle Texte (inkl. Dropdown Inhalte)."""
        self.lbl_head.configure(text=self.loc.get("HEADER_TITLE"))
        self.lbl_sub.configure(text=self.loc.get("HEADER_SUB"))
        self.lbl_presets.configure(text=self.loc.get("PRESET_LABEL"))
        self.lbl_action.configure(text=self.loc.get("LBL_ACTION"))
        
        # Action Dropdown Werte aktualisieren
        action_display_values = [self.loc.get(self.action_map[k]) for k in self.action_keys]
        self.combo_action.configure(values=action_display_values)
        
        # Aktuell gewählte Aktion wieder anzeigen
        current_action_key = self.config.get("action")
        current_display = self.loc.get(self.action_map.get(current_action_key, "ACTION_SHUTDOWN"))
        self.combo_action.set(current_display)

        # Slider Text
        hours = round(self.target_minutes / 60, 1)
        self.lbl_time.configure(text=self.loc.get("LBL_LIMIT", self.target_minutes, hours))

        # Buttons
        if self.is_monitoring:
            self.lbl_status.configure(text=self.loc.get("STATUS_ACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_STOP"))
        else:
            self.lbl_status.configure(text=self.loc.get("STATUS_INACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_START"))

    def set_preset(self, minutes):
        if not self.is_monitoring:
            self.target_minutes = minutes
            self.slider.set(minutes)
            self.config.set("target_minutes", minutes) # Speichern
            self.update_ui_texts()

    def on_slider(self, value):
        self.target_minutes = int(value)
        self.config.set("target_minutes", self.target_minutes) # Speichern (vielleicht zu oft? Egal bei lokaler JSON)
        hours = round(self.target_minutes / 60, 1)
        self.lbl_time.configure(text=self.loc.get("LBL_LIMIT", self.target_minutes, hours))

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.btn_toggle.configure(fg_color="#C0392B", hover_color="#922B21")
            self.lbl_status.configure(text_color="#2ECC71")
            self.slider.configure(state="disabled")
            self.combo_action.configure(state="disabled")
        else:
            self.btn_toggle.configure(fg_color="#1f6aa5", hover_color="#144870")
            self.lbl_status.configure(text_color="#ff5555")
            self.slider.configure(state="normal")
            self.combo_action.configure(state="normal")
        self.update_ui_texts()

    def main_loop(self):
        if self.is_monitoring and not self.warning_active:
            idle_sec = self.monitor.get_idle_seconds()
            m, s = divmod(int(idle_sec), 60)
            self.lbl_debug.configure(text=self.loc.get("DEBUG_IDLE", m, s))

            limit_sec = self.target_minutes * 60
            trigger_sec = limit_sec - 60

            if idle_sec >= trigger_sec:
                self.warning_active = True
                self.deiconify()
                # Wichtig: Wir müssen dem WarningDialog sagen, WAS er tun soll
                # Daher Update in WarningDialog nötig oder wir geben den Befehl weiter
                WarningDialog(self, self.monitor, self.loc, self.on_warning_action)

        self.after(1000, self.main_loop)

    def on_warning_action(self):
        """Callback wenn der Countdown im Popup abgelaufen ist."""
        action = self.config.get("action")
        self.monitor.execute_action(action)
        self.warning_active = False # (Eigentlich egal, da PC ausgeht)

    def on_warning_closed(self):
        """Callback wenn User abgebrochen hat."""
        self.warning_active = False
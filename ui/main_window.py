import customtkinter as ctk
from core.monitor import IdleMonitor
from core.localization import LocalizationManager
from ui.warning_dialog import WarningDialog

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialisierung
        self.monitor = IdleMonitor()
        self.loc = LocalizationManager("de") # Standard Deutsch
        
        self.is_monitoring = False
        self.warning_active = False
        self.target_minutes = 60 # Standard 1 Stunde

        self.setup_window()
        self.setup_widgets()
        
        # Texte einmal initial laden
        self.update_ui_texts()
        
        self.main_loop()

    def setup_window(self):
        self.title("Auto Shutdown Manager")
        self.geometry("550x550") # Etwas größer für Presets
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(0, weight=1)

    def setup_widgets(self):
        # --- SPRACH AUSWAHL (Oben rechts wäre ideal, aber hier einfach oben) ---
        self.frame_lang = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_lang.pack(pady=(10, 0), padx=20, fill="x")
        
        self.lbl_lang = ctk.CTkLabel(self.frame_lang, text="Sprache:", font=("Segoe UI", 12))
        self.lbl_lang.pack(side="left")

        self.combo_lang = ctk.CTkComboBox(self.frame_lang, values=["Deutsch", "English"], command=self.change_language, width=100)
        self.combo_lang.set("Deutsch")
        self.combo_lang.pack(side="right")

        # --- HEADER ---
        self.lbl_head = ctk.CTkLabel(self, text="TITLE", font=("Segoe UI", 26, "bold"))
        self.lbl_head.pack(pady=(10, 5))
        
        self.lbl_sub = ctk.CTkLabel(self, text="SUBTITLE", text_color="gray")
        self.lbl_sub.pack(pady=(0, 15))

        # --- PRESETS (Schnellwahl) ---
        self.frame_presets = ctk.CTkFrame(self)
        self.frame_presets.pack(pady=10, padx=20, fill="x")
        
        self.lbl_presets = ctk.CTkLabel(self.frame_presets, text="Presets", font=("Segoe UI", 12, "bold"))
        self.lbl_presets.pack(pady=5)
        
        self.grid_presets = ctk.CTkFrame(self.frame_presets, fg_color="transparent")
        self.grid_presets.pack(pady=(0, 10))

        # Buttons für 30m, 1h, 2h, 4h
        # Wir nutzen lambda, um Parameter an die Funktion zu übergeben
        ctk.CTkButton(self.grid_presets, text="30 min", width=60, command=lambda: self.set_preset(30)).grid(row=0, column=0, padx=5)
        ctk.CTkButton(self.grid_presets, text="1 h", width=60, command=lambda: self.set_preset(60)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(self.grid_presets, text="2 h", width=60, command=lambda: self.set_preset(120)).grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.grid_presets, text="4 h", width=60, command=lambda: self.set_preset(240)).grid(row=0, column=3, padx=5)

        # --- SLIDER ---
        self.frame_slider = ctk.CTkFrame(self)
        self.frame_slider.pack(pady=10, padx=20, fill="x")

        self.lbl_time = ctk.CTkLabel(self.frame_slider, text="Limit", font=("Segoe UI", 16))
        self.lbl_time.pack(pady=10)

        # Slider bis 480 Minuten (8 Stunden)
        self.slider = ctk.CTkSlider(self.frame_slider, from_=5, to=480, number_of_steps=475, command=self.on_slider)
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
        self.update_ui_texts() # Alle Texte neu setzen

    def update_ui_texts(self):
        """Setzt alle Texte der UI basierend auf der aktuellen Sprache."""
        self.lbl_lang.configure(text=self.loc.get("LANG_LABEL"))
        self.lbl_head.configure(text=self.loc.get("HEADER_TITLE"))
        self.lbl_sub.configure(text=self.loc.get("HEADER_SUB"))
        self.lbl_presets.configure(text=self.loc.get("PRESET_LABEL"))
        
        # Slider Text Update
        hours = round(self.target_minutes / 60, 1)
        self.lbl_time.configure(text=self.loc.get("LBL_LIMIT", self.target_minutes, hours))

        # Status & Button Update
        if self.is_monitoring:
            self.lbl_status.configure(text=self.loc.get("STATUS_ACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_STOP"))
        else:
            self.lbl_status.configure(text=self.loc.get("STATUS_INACTIVE"))
            self.btn_toggle.configure(text=self.loc.get("BTN_START"))

    def set_preset(self, minutes):
        """Wird von den Preset-Buttons aufgerufen."""
        if not self.is_monitoring:
            self.target_minutes = minutes
            self.slider.set(minutes)
            self.update_ui_texts() # Aktualisiert den Text "Limit: X Minuten"

    def on_slider(self, value):
        self.target_minutes = int(value)
        # Wir rufen update_ui_texts auf, um die Zahl im Label zu ändern
        # Performance: Man könnte das Label auch direkt setzen, aber so ist es konsistent.
        hours = round(self.target_minutes / 60, 1)
        self.lbl_time.configure(text=self.loc.get("LBL_LIMIT", self.target_minutes, hours))

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        
        if self.is_monitoring:
            self.btn_toggle.configure(fg_color="#C0392B", hover_color="#922B21")
            self.lbl_status.configure(text_color="#2ECC71")
            self.slider.configure(state="disabled")
            # Presets disablen wäre auch gut
        else:
            self.btn_toggle.configure(fg_color="#1f6aa5", hover_color="#144870")
            self.lbl_status.configure(text_color="#ff5555")
            self.slider.configure(state="normal")
            
        self.update_ui_texts() # Button und Status Text anpassen

    def on_warning_closed(self):
        self.warning_active = False

    def main_loop(self):
        if self.is_monitoring and not self.warning_active:
            idle_sec = self.monitor.get_idle_seconds()
            
            # Debug Anzeige
            m, s = divmod(int(idle_sec), 60)
            self.lbl_debug.configure(text=self.loc.get("DEBUG_IDLE", m, s))

            limit_sec = self.target_minutes * 60
            trigger_sec = limit_sec - 60

            if idle_sec >= trigger_sec:
                self.warning_active = True
                self.deiconify()
                # Wichtig: Wir übergeben hier self.loc an das Warning Window!
                WarningDialog(self, self.monitor, self.loc, self.on_warning_closed)

        self.after(1000, self.main_loop)
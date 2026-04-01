import ctypes
import os


class IdleMonitor:
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    # Konstanten für Windows Power Management
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    def __init__(self):
        self._last_input_info = self.LASTINPUTINFO()
        self._last_input_info.cbSize = ctypes.sizeof(self.LASTINPUTINFO)

    def get_idle_seconds(self) -> float:
        """Gibt die Sekunden seit der letzten Maus/Tastatur-Eingabe zurück."""
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(self._last_input_info))
        millis = ctypes.windll.kernel32.GetTickCount() - self._last_input_info.dwTime
        return millis / 1000.0

    def set_keep_awake(self, enable: bool):
        """
        Verhindert, dass Windows in den Standby geht, während der Timer läuft.
        enable=True: PC bleibt wach.
        enable=False: PC darf wieder normal schlafen (nach Windows-Einstellungen).
        """
        if enable:
            # Sagt Windows: System benötigt! (Display darf ausgehen, aber PC nicht schlafen)
            ctypes.windll.kernel32.SetThreadExecutionState(
                self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED
            )
        else:
            # Reset: Normaler Windows Timer gilt wieder
            ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)

    def execute_action(self, action_type="shutdown"):
        """Führt die gewünschte Power-Aktion aus."""
        # WICHTIG: Vor dem Shutdown den Wach-Modus aufheben, sonst kann es haken
        self.set_keep_awake(False)

        from . import logger

        logger.info(f"Führe Aktion aus: {action_type}")

        if action_type == "shutdown":
            os.system("shutdown /s /t 0 /f")
        elif action_type == "restart":
            os.system("shutdown /r /t 0 /f")
        elif action_type == "hibernate":
            os.system("shutdown /h")
        elif action_type == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

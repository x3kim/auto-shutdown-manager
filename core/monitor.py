import ctypes
import os

class IdleMonitor:
    """Backend-Klasse: Kümmert sich um System-Zeit und Shutdown-Befehle."""
    
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    def __init__(self):
        self._last_input_info = self.LASTINPUTINFO()
        self._last_input_info.cbSize = ctypes.sizeof(self.LASTINPUTINFO)

    def get_idle_seconds(self) -> float:
        """Gibt die Sekunden seit der letzten User-Interaktion zurück."""
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(self._last_input_info))
        millis = ctypes.windll.kernel32.GetTickCount() - self._last_input_info.dwTime
        return millis / 1000.0

    def shutdown_pc(self):
        """Führt den Shutdown aus."""
        # /s = Shutdown, /t 0 = Sofort, /f = Force
        os.system("shutdown /s /t 0 /f")
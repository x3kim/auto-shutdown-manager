import ctypes
import os

class IdleMonitor:
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    def __init__(self):
        self._last_input_info = self.LASTINPUTINFO()
        self._last_input_info.cbSize = ctypes.sizeof(self.LASTINPUTINFO)

    def get_idle_seconds(self) -> float:
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(self._last_input_info))
        millis = ctypes.windll.kernel32.GetTickCount() - self._last_input_info.dwTime
        return millis / 1000.0

    def execute_action(self, action_type="shutdown"):
        """Führt die gewünschte Power-Aktion aus."""
        print(f"Führe Aktion aus: {action_type}")
        
        if action_type == "shutdown":
            os.system("shutdown /s /t 0 /f")
        elif action_type == "restart":
            os.system("shutdown /r /t 0 /f")
        elif action_type == "sleep":
            # Windows Sleep Command (rundll32 ruft die Power-Funktion auf)
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
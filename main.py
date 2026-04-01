import sys
import platform
from customtkinter import CTk
from tkinter import messagebox
from ui.main_window import MainWindow

if platform.system() != "Windows":
    root = CTk()
    root.withdraw()
    root.title("Fehler")
    messagebox.showerror(
        "Plattform-Fehler", "Auto Shutdown Manager läuft nur auf Windows!"
    )
    sys.exit(1)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

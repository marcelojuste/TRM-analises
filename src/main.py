import sys
import uuid
import ctypes
import multiprocessing

from src.views.app import MainWindow

def main():
    if sys.platform.startswith("win"):
        try:
            my_app_id = "trmsistemas.trmanalises.auditor.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        except Exception:
            pass

    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
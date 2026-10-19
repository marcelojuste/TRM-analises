import ctypes
import multiprocessing
import sys

try:
    from tkinterdnd2 import TkinterDnD
    HAS_TKINTER_DND = True
except ImportError:
    HAS_TKINTER_DND = False

from src.views.app import MainWindow


def create_app():
    if HAS_TKINTER_DND:
        class AppWindow(MainWindow, TkinterDnD.DnDWrapper):
            def __init__(self, *args, **kwargs):
                MainWindow.__init__(self, *args, **kwargs)
                self.TkdndVersion = TkinterDnD._require(self)

        return AppWindow()
    else:
        return MainWindow()


def main():
    if sys.platform.startswith("win"):
        try:
            my_app_id = "trmsistemas.trmanalises.auditor.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        except Exception:
            pass

    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
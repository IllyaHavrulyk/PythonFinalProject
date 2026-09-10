from constants import APP_GEOMETRY, APP_TITLE
from ui.main_window import MainWindow


if __name__ == "__main__":
    main_window = MainWindow(APP_TITLE, APP_GEOMETRY)
    main_window.start()

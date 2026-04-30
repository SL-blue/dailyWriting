# main.py

import sys
from PyQt6.QtWidgets import QApplication

from core.logging_config import setup_logging
from core.config import get_settings
from ui.main_window import MainWindow
from ui.theme import apply_theme


def main() -> None:
    # Initialize logging
    logger = setup_logging(debug="--debug" in sys.argv)
    logger.info("Starting DailyWriting application")

    # Create the Qt application object
    app = QApplication(sys.argv)
    app.setApplicationName("DailyWriting")

    # Apply the user's chosen theme before any widgets are constructed
    apply_theme(get_settings().appearance.theme)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the event loop after the event loop ends(exit Python)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

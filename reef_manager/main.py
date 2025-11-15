"""
Punkt wejścia aplikacji Reef Manager PRO.
"""

import sys
from reef_manager.qt_compat import QtWidgets
from reef_manager.ui.main_window import MainWindow


def main():
    """Główna funkcja aplikacji."""
    app = QtWidgets.QApplication(sys.argv)

    # Ustawienia aplikacji
    app.setApplicationName('Reef Manager PRO')
    app.setOrganizationName('Reef Manager')
    app.setApplicationVersion('1.0.0')

    # Tworzenie i wyświetlanie głównego okna
    window = MainWindow()
    window.show()

    # Uruchomienie pętli zdarzeń
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

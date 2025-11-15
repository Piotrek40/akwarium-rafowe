"""
Skrypt pomocniczy do uruchamiania Reef Manager PRO.
Automatycznie wykrywa dostępną bibliotekę Qt (PyQt6 lub PySide6).
"""

import sys

# Próbuj najpierw PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    from reef_manager.ui.main_window import MainWindow
    QT_LIB = "PyQt6"
    print(f"✓ Używam {QT_LIB}")
except ImportError as e1:
    # Jeśli PyQt6 nie działa, spróbuj PySide6
    try:
        # Podmień importy na PySide6
        import importlib.util

        # Tworzymy alias PySide6 -> PyQt6 w sys.modules
        import PySide6.QtWidgets
        import PySide6.QtCore
        import PySide6.QtGui

        sys.modules['PyQt6'] = type(sys)('PyQt6')
        sys.modules['PyQt6.QtWidgets'] = PySide6.QtWidgets
        sys.modules['PyQt6.QtCore'] = PySide6.QtCore
        sys.modules['PyQt6.QtGui'] = PySide6.QtGui

        from PySide6.QtWidgets import QApplication
        from reef_manager.ui.main_window import MainWindow
        QT_LIB = "PySide6"
        print(f"✓ Używam {QT_LIB} (fallback)")
    except ImportError as e2:
        print("❌ BŁĄD: Nie znaleziono ani PyQt6 ani PySide6!")
        print(f"\nBłąd PyQt6: {e1}")
        print(f"Błąd PySide6: {e2}")
        print("\nZainstaluj jedną z bibliotek:")
        print("  pip install PyQt6==6.5.0")
        print("lub")
        print("  pip install PySide6==6.6.0")
        sys.exit(1)


def main():
    """Główna funkcja aplikacji."""
    app = QApplication(sys.argv)

    # Ustawienia aplikacji
    app.setApplicationName('Reef Manager PRO')
    app.setOrganizationName('Reef Manager')
    app.setApplicationVersion('1.0.0')

    print(f"✓ Uruchamiam Reef Manager PRO...")

    # Tworzenie i wyświetlanie głównego okna
    window = MainWindow()
    window.show()

    # Uruchomienie pętli zdarzeń
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

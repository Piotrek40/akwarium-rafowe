"""
Warstwa kompatybilności Qt - działa zarówno z PyQt6 jak i PySide6.
"""

import sys
from datetime import datetime

# Próbuj najpierw PyQt6
try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtCore import pyqtSlot as Slot
    QT_API = "PyQt6"

except ImportError:
    # Jeśli PyQt6 nie działa, użyj PySide6
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        from PySide6.QtCore import Signal, Slot
        QT_API = "PySide6"

    except ImportError:
        raise ImportError(
            "Nie znaleziono ani PyQt6 ani PySide6!\n\n"
            "Zainstaluj jedną z bibliotek:\n"
            "  pip install PyQt6==6.5.0\n"
            "lub\n"
            "  pip install PySide6==6.6.0"
        )


def qDateTime_to_python(qdt) -> datetime:
    """
    Konwertuje QDateTime na Python datetime.
    Działa zarówno z PyQt6 jak i PySide6.

    Args:
        qdt: QDateTime object

    Returns:
        datetime: Python datetime object
    """
    if QT_API == "PyQt6":
        return qdt.toPyDateTime()
    else:  # PySide6
        return qdt.toPython()


# Kompatybilność dla Dialog result codes
# PyQt6: QDialog.DialogCode.Accepted
# PySide6: QDialog.Accepted (bezpośrednio)
class DialogResult:
    """Uniwersalne kody wyniku dialogu - działa z PyQt6 i PySide6."""
    if QT_API == "PyQt6":
        Accepted = QtWidgets.QDialog.DialogCode.Accepted
        Rejected = QtWidgets.QDialog.DialogCode.Rejected
    else:  # PySide6
        Accepted = QtWidgets.QDialog.Accepted
        Rejected = QtWidgets.QDialog.Rejected


# Eksportuj wszystko co potrzebne
__all__ = [
    'QtCore', 'QtGui', 'QtWidgets',
    'Signal', 'Slot', 'QT_API', 'qDateTime_to_python', 'DialogResult'
]

print(f"✓ Używam {QT_API}")

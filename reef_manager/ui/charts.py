"""
Komponenty do wyświetlania wykresów w PyQt6.
Używa matplotlib do rysowania wykresów parametrów wody.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from reef_manager.db.models import WaterMeasurement


class ChartWidget(QWidget):
    """Widget do wyświetlania wykresów parametrów wody."""

    PARAMETERS = {
        'no3': ('Azotany (NO3)', 'mg/l'),
        'po4': ('Fosforany (PO4)', 'mg/l'),
        'kh': ('Twardość węglanowa (KH)', 'dKH'),
        'ph': ('pH', ''),
        'temperature': ('Temperatura', '°C'),
        'salinity': ('Zasolenie', 'SG'),
        'nh3_nh4': ('Amoniak (NH3/NH4)', 'mg/l'),
    }

    DATE_RANGES = {
        'Ostatnie 7 dni': 7,
        'Ostatnie 30 dni': 30,
        'Ostatnie 90 dni': 90,
        'Wszystkie': None,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.measurements: List[WaterMeasurement] = []
        self.init_ui()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        layout = QVBoxLayout()

        # Panel kontrolny
        control_panel = QHBoxLayout()

        # Wybór parametru
        control_panel.addWidget(QLabel('Parametr:'))
        self.param_combo = QComboBox()
        for param_key, (param_name, unit) in self.PARAMETERS.items():
            display_name = f"{param_name} ({unit})" if unit else param_name
            self.param_combo.addItem(display_name, param_key)
        control_panel.addWidget(self.param_combo)

        # Wybór zakresu dat
        control_panel.addWidget(QLabel('Zakres:'))
        self.range_combo = QComboBox()
        for range_name in self.DATE_RANGES.keys():
            self.range_combo.addItem(range_name)
        control_panel.addWidget(self.range_combo)

        # Przycisk odświeżania
        self.refresh_button = QPushButton('Odśwież wykres')
        self.refresh_button.clicked.connect(self.update_chart)
        control_panel.addWidget(self.refresh_button)

        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Wykres matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def set_measurements(self, measurements: List[WaterMeasurement]):
        """
        Ustawia dane pomiarów.

        Args:
            measurements: Lista pomiarów.
        """
        self.measurements = measurements
        self.update_chart()

    def update_chart(self):
        """Aktualizuje wykres na podstawie wybranych parametrów."""
        self.figure.clear()

        if not self.measurements:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Brak danych do wyświetlenia',
                   ha='center', va='center', fontsize=14)
            self.canvas.draw()
            return

        # Pobierz wybrany parametr i zakres
        param_key = self.param_combo.currentData()
        range_name = self.range_combo.currentText()
        days = self.DATE_RANGES[range_name]

        # Filtruj dane według zakresu dat
        filtered_measurements = self.measurements
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_measurements = [
                m for m in self.measurements
                if m.measurement_date >= cutoff_date
            ]

        # Pobierz dane dla wykresu
        dates = []
        values = []
        for measurement in filtered_measurements:
            value = getattr(measurement, param_key)
            if value is not None:
                dates.append(measurement.measurement_date)
                values.append(value)

        if not dates:
            ax = self.figure.add_subplot(111)
            param_name, unit = self.PARAMETERS[param_key]
            ax.text(0.5, 0.5, f'Brak pomiarów dla: {param_name}',
                   ha='center', va='center', fontsize=14)
            self.canvas.draw()
            return

        # Rysuj wykres
        ax = self.figure.add_subplot(111)
        ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=6)

        # Formatowanie
        param_name, unit = self.PARAMETERS[param_key]
        title = f"{param_name}"
        if unit:
            title += f" ({unit})"
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ylabel = f"{param_name}"
        if unit:
            ylabel += f" [{unit}]"
        ax.set_ylabel(ylabel, fontsize=12)

        # Formatuj oś X (daty)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.figure.autofmt_xdate()

        # Siatka
        ax.grid(True, alpha=0.3)

        # Dostosuj layout
        self.figure.tight_layout()

        # Odśwież canvas
        self.canvas.draw()

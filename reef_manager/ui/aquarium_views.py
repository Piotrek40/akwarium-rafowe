"""
Widoki i zakładki dla akwariów w Reef Manager PRO.
"""

from datetime import datetime
from typing import Optional
from reef_manager.qt_compat import QtWidgets, QtCore, Signal

from reef_manager.db.models import Aquarium, WaterMeasurement, AquariumEvent, Inhabitant
from reef_manager.logic.services import MeasurementService, EventService, InhabitantService, ExportService
from reef_manager.logic.rules import RulesEngine
from reef_manager.ui.charts import ChartWidget


class AquariumDetailsWidget(QtWidgets.QWidget):
    """Widget do wyświetlania szczegółów akwarium w zakładkach."""

    measurement_added = Signal()
    event_added = Signal()
    inhabitant_added = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.aquarium: Optional[Aquarium] = None

        # Serwisy
        self.measurement_service = MeasurementService(session)
        self.event_service = EventService(session)
        self.inhabitant_service = InhabitantService(session)

        self.init_ui()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        layout = QtWidgets.QVBoxLayout()

        # Zakładki
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.create_summary_tab(), 'Podsumowanie')
        self.tabs.addTab(self.create_parameters_tab(), 'Parametry')
        self.tabs.addTab(self.create_charts_tab(), 'Wykresy')
        self.tabs.addTab(self.create_events_tab(), 'Wydarzenia')
        self.tabs.addTab(self.create_inhabitants_tab(), 'Obsada')

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_summary_tab(self) -> QtWidgets.QWidget:
        """Tworzy zakładkę podsumowania."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Informacje o akwarium
        self.info_label = QtWidgets.QLabel('Wybierz akwarium z listy')
        self.info_label.setStyleSheet('font-size: 14px; font-weight: bold; padding: 10px;')
        layout.addWidget(self.info_label)

        # Ostatnie parametry
        params_group = QtWidgets.QGroupBox('Ostatnie parametry')
        self.params_layout = QtWidgets.QVBoxLayout()
        self.last_params_label = QtWidgets.QLabel('Brak pomiarów')
        self.params_layout.addWidget(self.last_params_label)
        params_group.setLayout(self.params_layout)
        layout.addWidget(params_group)

        # Alerty i sugestie
        alerts_group = QtWidgets.QGroupBox('Alerty i sugestie')
        self.alerts_layout = QtWidgets.QVBoxLayout()
        self.alerts_label = QtWidgets.QLabel('Brak alertów')
        self.alerts_layout.addWidget(self.alerts_label)
        alerts_group.setLayout(self.alerts_layout)
        layout.addWidget(alerts_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_parameters_tab(self) -> QtWidgets.QWidget:
        """Tworzy zakładkę parametrów."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Formularz dodawania pomiaru
        form_group = QtWidgets.QGroupBox('Dodaj nowy pomiar')
        form_layout = QtWidgets.QFormLayout()

        self.measurement_date_edit = QtWidgets.QDateTimeEdit()
        self.measurement_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.measurement_date_edit.setCalendarPopup(True)
        form_layout.addRow('Data i godzina:', self.measurement_date_edit)

        self.no3_edit = QtWidgets.QLineEdit()
        self.no3_edit.setPlaceholderText('np. 10.5')
        form_layout.addRow('NO3 (mg/l):', self.no3_edit)

        self.po4_edit = QtWidgets.QLineEdit()
        self.po4_edit.setPlaceholderText('np. 0.05')
        form_layout.addRow('PO4 (mg/l):', self.po4_edit)

        self.kh_edit = QtWidgets.QLineEdit()
        self.kh_edit.setPlaceholderText('np. 8.0')
        form_layout.addRow('KH (dKH):', self.kh_edit)

        self.ph_edit = QtWidgets.QLineEdit()
        self.ph_edit.setPlaceholderText('np. 8.2')
        form_layout.addRow('pH:', self.ph_edit)

        self.temp_edit = QtWidgets.QLineEdit()
        self.temp_edit.setPlaceholderText('np. 25.5')
        form_layout.addRow('Temperatura (°C):', self.temp_edit)

        self.salinity_edit = QtWidgets.QLineEdit()
        self.salinity_edit.setPlaceholderText('np. 1.025')
        form_layout.addRow('Zasolenie (SG):', self.salinity_edit)

        self.nh3_edit = QtWidgets.QLineEdit()
        self.nh3_edit.setPlaceholderText('np. 0.0')
        form_layout.addRow('NH3/NH4 (mg/l):', self.nh3_edit)

        self.measurement_comment_edit = QtWidgets.QTextEdit()
        self.measurement_comment_edit.setMaximumHeight(60)
        self.measurement_comment_edit.setPlaceholderText('Opcjonalny komentarz...')
        form_layout.addRow('Komentarz:', self.measurement_comment_edit)

        add_button = QtWidgets.QPushButton('Dodaj pomiar')
        add_button.clicked.connect(self.add_measurement)
        form_layout.addRow('', add_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabela pomiarów
        self.measurements_table = QtWidgets.QTableWidget()
        self.measurements_table.setColumnCount(10)
        self.measurements_table.setHorizontalHeaderLabels([
            'Data', 'NO3', 'PO4', 'KH', 'pH', 'Temp', 'Zasolenie', 'NH3/NH4', 'Komentarz', 'Akcje'
        ])
        self.measurements_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.measurements_table)

        widget.setLayout(layout)
        return widget

    def create_charts_tab(self) -> QtWidgets.QWidget:
        """Tworzy zakładkę wykresów."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)

        widget.setLayout(layout)
        return widget

    def create_events_tab(self) -> QtWidgets.QWidget:
        """Tworzy zakładkę wydarzeń."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Formularz dodawania wydarzenia
        form_group = QtWidgets.QGroupBox('Dodaj nowe wydarzenie')
        form_layout = QtWidgets.QFormLayout()

        self.event_date_edit = QtWidgets.QDateTimeEdit()
        self.event_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.event_date_edit.setCalendarPopup(True)
        form_layout.addRow('Data i godzina:', self.event_date_edit)

        self.event_type_combo = QtWidgets.QComboBox()
        self.event_type_combo.addItems([
            'Podmiana wody',
            'Czyszczenie odpieniacza',
            'Dodanie skały',
            'Śmierć organizmu',
            'Leczenie',
            'Dodanie bakterii',
            'Karmienie',
            'Test wody',
            'Inne'
        ])
        form_layout.addRow('Typ wydarzenia:', self.event_type_combo)

        self.event_desc_edit = QtWidgets.QTextEdit()
        self.event_desc_edit.setMaximumHeight(80)
        self.event_desc_edit.setPlaceholderText('Opis wydarzenia...')
        form_layout.addRow('Opis:', self.event_desc_edit)

        add_event_button = QtWidgets.QPushButton('Dodaj wydarzenie')
        add_event_button.clicked.connect(self.add_event)
        form_layout.addRow('', add_event_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabela wydarzeń
        self.events_table = QtWidgets.QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(['Data', 'Typ', 'Opis', 'Akcje'])
        self.events_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.events_table)

        widget.setLayout(layout)
        return widget

    def create_inhabitants_tab(self) -> QtWidgets.QWidget:
        """Tworzy zakładkę obsady."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Formularz dodawania mieszkańca
        form_group = QtWidgets.QGroupBox('Dodaj nowego mieszkańca')
        form_layout = QtWidgets.QFormLayout()

        self.species_edit = QtWidgets.QLineEdit()
        self.species_edit.setPlaceholderText('np. Amphiprion ocellaris')
        form_layout.addRow('Gatunek/Nazwa:', self.species_edit)

        self.inhabitant_type_combo = QtWidgets.QComboBox()
        self.inhabitant_type_combo.addItems([
            'Ryba', 'Koral', 'Ślimak', 'Krab', 'Krewetka', 'Inne'
        ])
        form_layout.addRow('Typ:', self.inhabitant_type_combo)

        self.intro_date_edit = QtWidgets.QDateTimeEdit()
        self.intro_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.intro_date_edit.setCalendarPopup(True)
        form_layout.addRow('Data wprowadzenia:', self.intro_date_edit)

        self.quantity_edit = QtWidgets.QLineEdit()
        self.quantity_edit.setText('1')
        self.quantity_edit.setPlaceholderText('1')
        form_layout.addRow('Ilość:', self.quantity_edit)

        self.status_combo = QtWidgets.QComboBox()
        self.status_combo.addItems(['Aktywny', 'Padł', 'Przeniesiony'])
        form_layout.addRow('Status:', self.status_combo)

        self.inhabitant_notes_edit = QtWidgets.QTextEdit()
        self.inhabitant_notes_edit.setMaximumHeight(60)
        self.inhabitant_notes_edit.setPlaceholderText('Notatki...')
        form_layout.addRow('Notatki:', self.inhabitant_notes_edit)

        add_inhabitant_button = QtWidgets.QPushButton('Dodaj mieszkańca')
        add_inhabitant_button.clicked.connect(self.add_inhabitant)
        form_layout.addRow('', add_inhabitant_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabela obsady
        self.inhabitants_table = QtWidgets.QTableWidget()
        self.inhabitants_table.setColumnCount(7)
        self.inhabitants_table.setHorizontalHeaderLabels([
            'Gatunek', 'Typ', 'Data wprowadzenia', 'Ilość', 'Status', 'Notatki', 'Akcje'
        ])
        self.inhabitants_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.inhabitants_table)

        widget.setLayout(layout)
        return widget

    def set_aquarium(self, aquarium: Optional[Aquarium]):
        """Ustawia aktywne akwarium."""
        self.aquarium = aquarium
        self.refresh_all()

    def refresh_all(self):
        """Odświeża wszystkie dane."""
        if not self.aquarium:
            self.info_label.setText('Wybierz akwarium z listy')
            return

        self.refresh_summary()
        self.refresh_measurements()
        self.refresh_charts()
        self.refresh_events()
        self.refresh_inhabitants()

    def refresh_summary(self):
        """Odświeża podsumowanie."""
        if not self.aquarium:
            return

        # Informacje o akwarium
        info_text = f"""
        <b>Nazwa:</b> {self.aquarium.name}<br>
        <b>Typ:</b> {self.aquarium.aquarium_type}<br>
        <b>Objętość:</b> {self.aquarium.volume_liters} litrów<br>
        <b>Data startu:</b> {self.aquarium.start_date.strftime('%Y-%m-%d')}<br>
        <b>Opis:</b> {self.aquarium.description or 'Brak opisu'}
        """
        self.info_label.setText(info_text)

        # Ostatnie parametry
        last_measurement = self.measurement_service.get_latest_measurement(self.aquarium.id)
        if last_measurement:
            params_text = f"""
            <b>Data pomiaru:</b> {last_measurement.measurement_date.strftime('%Y-%m-%d %H:%M')}<br>
            <b>NO3:</b> {last_measurement.no3 if last_measurement.no3 is not None else 'N/A'} mg/l<br>
            <b>PO4:</b> {last_measurement.po4 if last_measurement.po4 is not None else 'N/A'} mg/l<br>
            <b>KH:</b> {last_measurement.kh if last_measurement.kh is not None else 'N/A'} dKH<br>
            <b>pH:</b> {last_measurement.ph if last_measurement.ph is not None else 'N/A'}<br>
            <b>Temperatura:</b> {last_measurement.temperature if last_measurement.temperature is not None else 'N/A'} °C<br>
            <b>Zasolenie:</b> {last_measurement.salinity if last_measurement.salinity is not None else 'N/A'} SG<br>
            <b>NH3/NH4:</b> {last_measurement.nh3_nh4 if last_measurement.nh3_nh4 is not None else 'N/A'} mg/l
            """
            self.last_params_label.setText(params_text)

            # Alerty i sugestie
            rules_engine = RulesEngine(self.aquarium.aquarium_type)
            measurement_dict = {
                'no3': last_measurement.no3,
                'po4': last_measurement.po4,
                'kh': last_measurement.kh,
                'ph': last_measurement.ph,
                'temperature': last_measurement.temperature,
                'salinity': last_measurement.salinity,
                'nh3_nh4': last_measurement.nh3_nh4,
            }
            alerts, suggestions = rules_engine.analyze_parameters(measurement_dict)

            alerts_html = '<b>Alerty:</b><br>'
            for alert in alerts:
                alerts_html += f'• {alert}<br>'

            if suggestions:
                alerts_html += '<br><b>Sugestie:</b><br>'
                for suggestion in suggestions:
                    alerts_html += f'• {suggestion}<br>'

            self.alerts_label.setText(alerts_html)
        else:
            self.last_params_label.setText('Brak pomiarów')
            self.alerts_label.setText('Brak danych do analizy')

    def refresh_measurements(self):
        """Odświeża tabelę pomiarów."""
        if not self.aquarium:
            return

        measurements = self.measurement_service.get_measurements(self.aquarium.id)
        self.measurements_table.setRowCount(len(measurements))

        for row, measurement in enumerate(measurements):
            self.measurements_table.setItem(row, 0, QtWidgets.QTableWidgetItem(
                measurement.measurement_date.strftime('%Y-%m-%d %H:%M')
            ))
            self.measurements_table.setItem(row, 1, QtWidgets.QTableWidgetItem(
                str(measurement.no3) if measurement.no3 is not None else ''
            ))
            self.measurements_table.setItem(row, 2, QtWidgets.QTableWidgetItem(
                str(measurement.po4) if measurement.po4 is not None else ''
            ))
            self.measurements_table.setItem(row, 3, QtWidgets.QTableWidgetItem(
                str(measurement.kh) if measurement.kh is not None else ''
            ))
            self.measurements_table.setItem(row, 4, QtWidgets.QTableWidgetItem(
                str(measurement.ph) if measurement.ph is not None else ''
            ))
            self.measurements_table.setItem(row, 5, QtWidgets.QTableWidgetItem(
                str(measurement.temperature) if measurement.temperature is not None else ''
            ))
            self.measurements_table.setItem(row, 6, QtWidgets.QTableWidgetItem(
                str(measurement.salinity) if measurement.salinity is not None else ''
            ))
            self.measurements_table.setItem(row, 7, QtWidgets.QTableWidgetItem(
                str(measurement.nh3_nh4) if measurement.nh3_nh4 is not None else ''
            ))
            self.measurements_table.setItem(row, 8, QtWidgets.QTableWidgetItem(
                measurement.comment or ''
            ))

            # Przycisk usuwania
            delete_btn = QtWidgets.QPushButton('Usuń')
            delete_btn.clicked.connect(lambda checked, m_id=measurement.id: self.delete_measurement(m_id))
            self.measurements_table.setCellWidget(row, 9, delete_btn)

    def refresh_charts(self):
        """Odświeża wykresy."""
        if not self.aquarium:
            return

        measurements = self.measurement_service.get_measurements(self.aquarium.id)
        self.chart_widget.set_measurements(measurements)

    def refresh_events(self):
        """Odświeża tabelę wydarzeń."""
        if not self.aquarium:
            return

        events = self.event_service.get_events(self.aquarium.id)
        self.events_table.setRowCount(len(events))

        for row, event in enumerate(events):
            self.events_table.setItem(row, 0, QtWidgets.QTableWidgetItem(
                event.event_date.strftime('%Y-%m-%d %H:%M')
            ))
            self.events_table.setItem(row, 1, QtWidgets.QTableWidgetItem(event.event_type))
            self.events_table.setItem(row, 2, QtWidgets.QTableWidgetItem(event.description))

            # Przycisk usuwania
            delete_btn = QtWidgets.QPushButton('Usuń')
            delete_btn.clicked.connect(lambda checked, e_id=event.id: self.delete_event(e_id))
            self.events_table.setCellWidget(row, 3, delete_btn)

    def refresh_inhabitants(self):
        """Odświeża tabelę obsady."""
        if not self.aquarium:
            return

        inhabitants = self.inhabitant_service.get_inhabitants(self.aquarium.id, include_inactive=True)
        self.inhabitants_table.setRowCount(len(inhabitants))

        for row, inhabitant in enumerate(inhabitants):
            self.inhabitants_table.setItem(row, 0, QtWidgets.QTableWidgetItem(inhabitant.species_name))
            self.inhabitants_table.setItem(row, 1, QtWidgets.QTableWidgetItem(inhabitant.inhabitant_type))
            self.inhabitants_table.setItem(row, 2, QtWidgets.QTableWidgetItem(
                inhabitant.introduction_date.strftime('%Y-%m-%d')
            ))
            self.inhabitants_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(inhabitant.quantity)))
            self.inhabitants_table.setItem(row, 4, QtWidgets.QTableWidgetItem(inhabitant.status))
            self.inhabitants_table.setItem(row, 5, QtWidgets.QTableWidgetItem(inhabitant.notes or ''))

            # Przycisk usuwania
            delete_btn = QtWidgets.QPushButton('Usuń')
            delete_btn.clicked.connect(lambda checked, i_id=inhabitant.id: self.delete_inhabitant(i_id))
            self.inhabitants_table.setCellWidget(row, 6, delete_btn)

    def add_measurement(self):
        """Dodaje nowy pomiar."""
        if not self.aquarium:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        try:
            measurement_date = self.measurement_date_edit.dateTime().toPyDateTime()

            # Pobierz wartości (mogą być puste)
            no3 = self._parse_float(self.no3_edit.text())
            po4 = self._parse_float(self.po4_edit.text())
            kh = self._parse_float(self.kh_edit.text())
            ph = self._parse_float(self.ph_edit.text())
            temperature = self._parse_float(self.temp_edit.text())
            salinity = self._parse_float(self.salinity_edit.text())
            nh3_nh4 = self._parse_float(self.nh3_edit.text())
            comment = self.measurement_comment_edit.toPlainText()

            # Walidacja - przynajmniej jeden parametr musi być podany
            if all(v is None for v in [no3, po4, kh, ph, temperature, salinity, nh3_nh4]):
                QtWidgets.QMessageBox.warning(self, 'Błąd', 'Podaj przynajmniej jeden parametr')
                return

            # Dodaj pomiar
            self.measurement_service.add_measurement(
                aquarium_id=self.aquarium.id,
                measurement_date=measurement_date,
                no3=no3,
                po4=po4,
                kh=kh,
                ph=ph,
                temperature=temperature,
                salinity=salinity,
                nh3_nh4=nh3_nh4,
                comment=comment
            )

            # Wyczyść formularz
            self.no3_edit.clear()
            self.po4_edit.clear()
            self.kh_edit.clear()
            self.ph_edit.clear()
            self.temp_edit.clear()
            self.salinity_edit.clear()
            self.nh3_edit.clear()
            self.measurement_comment_edit.clear()
            self.measurement_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())

            # Odśwież
            self.refresh_all()
            self.measurement_added.emit()

            QtWidgets.QMessageBox.information(self, 'Sukces', 'Pomiar dodany pomyślnie')

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, 'Błąd', f'Nieprawidłowe dane: {str(e)}')

    def add_event(self):
        """Dodaje nowe wydarzenie."""
        if not self.aquarium:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        event_date = self.event_date_edit.dateTime().toPyDateTime()
        event_type = self.event_type_combo.currentText()
        description = self.event_desc_edit.toPlainText()

        if not description.strip():
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Podaj opis wydarzenia')
            return

        self.event_service.add_event(
            aquarium_id=self.aquarium.id,
            event_date=event_date,
            event_type=event_type,
            description=description
        )

        # Wyczyść formularz
        self.event_desc_edit.clear()
        self.event_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())

        # Odśwież
        self.refresh_events()
        self.event_added.emit()

        QtWidgets.QMessageBox.information(self, 'Sukces', 'Wydarzenie dodane pomyślnie')

    def add_inhabitant(self):
        """Dodaje nowego mieszkańca."""
        if not self.aquarium:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        species_name = self.species_edit.text().strip()
        if not species_name:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Podaj gatunek/nazwę')
            return

        try:
            inhabitant_type = self.inhabitant_type_combo.currentText()
            intro_date = self.intro_date_edit.dateTime().toPyDateTime()
            quantity = int(self.quantity_edit.text())
            status_map = {'Aktywny': 'active', 'Padł': 'dead', 'Przeniesiony': 'transferred'}
            status = status_map[self.status_combo.currentText()]
            notes = self.inhabitant_notes_edit.toPlainText()

            self.inhabitant_service.add_inhabitant(
                aquarium_id=self.aquarium.id,
                species_name=species_name,
                inhabitant_type=inhabitant_type,
                introduction_date=intro_date,
                quantity=quantity,
                status=status,
                notes=notes
            )

            # Wyczyść formularz
            self.species_edit.clear()
            self.quantity_edit.setText('1')
            self.inhabitant_notes_edit.clear()
            self.intro_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())

            # Odśwież
            self.refresh_inhabitants()
            self.inhabitant_added.emit()

            QtWidgets.QMessageBox.information(self, 'Sukces', 'Mieszkaniec dodany pomyślnie')

        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, 'Błąd', f'Nieprawidłowe dane: {str(e)}')

    def delete_measurement(self, measurement_id: int):
        """Usuwa pomiar."""
        reply = QtWidgets.QMessageBox.question(
            self, 'Potwierdzenie',
            'Czy na pewno chcesz usunąć ten pomiar?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.measurement_service.delete_measurement(measurement_id)
            self.refresh_all()

    def delete_event(self, event_id: int):
        """Usuwa wydarzenie."""
        reply = QtWidgets.QMessageBox.question(
            self, 'Potwierdzenie',
            'Czy na pewno chcesz usunąć to wydarzenie?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.event_service.delete_event(event_id)
            self.refresh_events()

    def delete_inhabitant(self, inhabitant_id: int):
        """Usuwa mieszkańca."""
        reply = QtWidgets.QMessageBox.question(
            self, 'Potwierdzenie',
            'Czy na pewno chcesz usunąć tego mieszkańca?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.inhabitant_service.delete_inhabitant(inhabitant_id)
            self.refresh_inhabitants()

    @staticmethod
    def _parse_float(value: str) -> Optional[float]:
        """Parsuje wartość float, zwraca None jeśli pusta lub nieprawidłowa."""
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            raise ValueError(f'Nieprawidłowa liczba: {value}')

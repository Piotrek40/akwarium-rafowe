"""
Główne okno aplikacji Reef Manager PRO.
"""

from datetime import datetime
from reef_manager.qt_compat import QtWidgets, QtCore, Signal

from reef_manager.db.database import get_database
from reef_manager.logic.services import AquariumService, BackupService, ExportService
from reef_manager.ui.aquarium_views import AquariumDetailsWidget


class AddAquariumDialog(QtWidgets.QDialog):
    """Dialog do dodawania nowego akwarium."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Dodaj nowe akwarium')
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        layout = QtWidgets.QFormLayout()

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText('np. Reef 80l')
        layout.addRow('Nazwa akwarium:', self.name_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['reef', 'FOWLR', 'freshwater'])
        layout.addRow('Typ akwarium:', self.type_combo)

        self.volume_edit = QtWidgets.QLineEdit()
        self.volume_edit.setPlaceholderText('np. 80')
        layout.addRow('Objętość (litry):', self.volume_edit)

        self.start_date_edit = QtWidgets.QDateTimeEdit()
        self.start_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat('yyyy-MM-dd')
        layout.addRow('Data startu:', self.start_date_edit)

        self.description_edit = QtWidgets.QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText('Opcjonalny opis...')
        layout.addRow('Opis:', self.description_edit)

        # Przyciski
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Zwraca dane z formularza."""
        return {
            'name': self.name_edit.text().strip(),
            'aquarium_type': self.type_combo.currentText(),
            'volume_liters': float(self.volume_edit.text()),
            'start_date': self.start_date_edit.dateTime().toPyDateTime(),
            'description': self.description_edit.toPlainText()
        }


class EditAquariumDialog(QtWidgets.QDialog):
    """Dialog do edycji akwarium."""

    def __init__(self, aquarium, parent=None):
        super().__init__(parent)
        self.aquarium = aquarium
        self.setWindowTitle('Edytuj akwarium')
        self.setModal(True)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        layout = QtWidgets.QFormLayout()

        self.name_edit = QtWidgets.QLineEdit()
        layout.addRow('Nazwa akwarium:', self.name_edit)

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(['reef', 'FOWLR', 'freshwater'])
        layout.addRow('Typ akwarium:', self.type_combo)

        self.volume_edit = QtWidgets.QLineEdit()
        layout.addRow('Objętość (litry):', self.volume_edit)

        self.start_date_edit = QtWidgets.QDateTimeEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat('yyyy-MM-dd')
        layout.addRow('Data startu:', self.start_date_edit)

        self.description_edit = QtWidgets.QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow('Opis:', self.description_edit)

        # Przyciski
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def load_data(self):
        """Wczytuje dane akwarium do formularza."""
        self.name_edit.setText(self.aquarium.name)
        self.type_combo.setCurrentText(self.aquarium.aquarium_type)
        self.volume_edit.setText(str(self.aquarium.volume_liters))
        self.start_date_edit.setDateTime(QtCore.QtCore.QDateTime(self.aquarium.start_date))
        self.description_edit.setPlainText(self.aquarium.description or '')

    def get_data(self):
        """Zwraca dane z formularza."""
        return {
            'name': self.name_edit.text().strip(),
            'aquarium_type': self.type_combo.currentText(),
            'volume_liters': float(self.volume_edit.text()),
            'start_date': self.start_date_edit.dateTime().toPyDateTime(),
            'description': self.description_edit.toPlainText()
        }


class MainWindow(QtWidgets.QMainWindow):
    """Główne okno aplikacji Reef Manager PRO."""

    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.session = self.db.get_session()
        self.aquarium_service = AquariumService(self.session)

        self.setWindowTitle('Reef Manager PRO')
        self.setGeometry(100, 100, 1400, 800)

        self.init_ui()
        self.refresh_aquarium_list()

    def init_ui(self):
        """Inicjalizuje interfejs użytkownika."""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QHBoxLayout()

        # Lewy panel - lista akwariów
        left_panel = QtWidgets.QVBoxLayout()

        left_panel.addWidget(QtWidgets.QLabel('<b>Lista akwariów</b>'))

        self.aquarium_list = QtWidgets.QListWidget()
        self.aquarium_list.currentItemChanged.connect(self.on_aquarium_selected)
        left_panel.addWidget(self.aquarium_list)

        # Przyciski zarządzania akwariami
        add_button = QtWidgets.QPushButton('Dodaj akwarium')
        add_button.clicked.connect(self.add_aquarium)
        left_panel.addWidget(add_button)

        edit_button = QtWidgets.QPushButton('Edytuj akwarium')
        edit_button.clicked.connect(self.edit_aquarium)
        left_panel.addWidget(edit_button)

        delete_button = QtWidgets.QPushButton('Usuń akwarium')
        delete_button.clicked.connect(self.delete_aquarium)
        left_panel.addWidget(delete_button)

        # Separator
        left_panel.addWidget(QtWidgets.QLabel(''))

        # Przyciski eksportu i backupu
        export_measurements_button = QtWidgets.QPushButton('Eksportuj pomiary (CSV)')
        export_measurements_button.clicked.connect(self.export_measurements)
        left_panel.addWidget(export_measurements_button)

        export_events_button = QtWidgets.QPushButton('Eksportuj wydarzenia (CSV)')
        export_events_button.clicked.connect(self.export_events)
        left_panel.addWidget(export_events_button)

        backup_button = QtWidgets.QPushButton('Zrób backup bazy')
        backup_button.clicked.connect(self.create_backup)
        left_panel.addWidget(backup_button)

        # Info o bazie danych
        db_path_label = QtWidgets.QLabel(f'<small>Baza danych:<br>{self.db.get_db_path()}</small>')
        db_path_label.setWordWrap(True)
        left_panel.addWidget(db_path_label)

        left_panel.addStretch()

        # Prawy panel - szczegóły akwarium
        self.aquarium_details = AquariumDetailsWidget(self.session)

        # Łączenie layoutów
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(300)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.aquarium_details, stretch=1)

        central_widget.setLayout(main_layout)

    def refresh_aquarium_list(self):
        """Odświeża listę akwariów."""
        self.aquarium_list.clear()
        aquariums = self.aquarium_service.get_all_aquariums()

        for aquarium in aquariums:
            display_text = f"{aquarium.name} ({aquarium.aquarium_type}, {aquarium.volume_liters}l)"
            item = self.aquarium_list.addItem(display_text)
            # Zapisz ID akwarium w danych elementu
            self.aquarium_list.item(self.aquarium_list.count() - 1).setData(QtCore.Qt.ItemDataRole.UserRole, aquarium.id)

        # Automatycznie wybierz pierwsze akwarium
        if self.aquarium_list.count() > 0:
            self.aquarium_list.setCurrentRow(0)

    def on_aquarium_selected(self, current, previous):
        """Obsługuje zmianę wybranego akwarium."""
        if current is None:
            self.aquarium_details.set_aquarium(None)
            return

        aquarium_id = current.data(QtCore.Qt.ItemDataRole.UserRole)
        aquarium = self.aquarium_service.get_aquarium(aquarium_id)
        self.aquarium_details.set_aquarium(aquarium)

    def add_aquarium(self):
        """Dodaje nowe akwarium."""
        dialog = AddAquariumDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()

                if not data['name']:
                    QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nazwa akwarium jest wymagana')
                    return

                if data['volume_liters'] <= 0:
                    QtWidgets.QMessageBox.warning(self, 'Błąd', 'Objętość musi być większa niż 0')
                    return

                self.aquarium_service.create_aquarium(**data)
                self.refresh_aquarium_list()
                QtWidgets.QMessageBox.information(self, 'Sukces', 'Akwarium dodane pomyślnie')

            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, 'Błąd', f'Nieprawidłowe dane: {str(e)}')

    def edit_aquarium(self):
        """Edytuje wybrane akwarium."""
        current_item = self.aquarium_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        aquarium_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        aquarium = self.aquarium_service.get_aquarium(aquarium_id)

        dialog = EditAquariumDialog(aquarium, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()

                if not data['name']:
                    QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nazwa akwarium jest wymagana')
                    return

                if data['volume_liters'] <= 0:
                    QtWidgets.QMessageBox.warning(self, 'Błąd', 'Objętość musi być większa niż 0')
                    return

                self.aquarium_service.update_aquarium(aquarium_id, **data)
                self.refresh_aquarium_list()
                QtWidgets.QMessageBox.information(self, 'Sukces', 'Akwarium zaktualizowane pomyślnie')

            except ValueError as e:
                QtWidgets.QMessageBox.warning(self, 'Błąd', f'Nieprawidłowe dane: {str(e)}')

    def delete_aquarium(self):
        """Usuwa wybrane akwarium."""
        current_item = self.aquarium_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        reply = QtWidgets.QMessageBox.question(
            self, 'Potwierdzenie',
            'Czy na pewno chcesz usunąć to akwarium? Wszystkie powiązane dane (pomiary, wydarzenia, obsada) zostaną usunięte!',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            aquarium_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.aquarium_service.delete_aquarium(aquarium_id)
            self.refresh_aquarium_list()
            QtWidgets.QMessageBox.information(self, 'Sukces', 'Akwarium usunięte pomyślnie')

    def export_measurements(self):
        """Eksportuje pomiary do CSV."""
        current_item = self.aquarium_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        aquarium_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        aquarium = self.aquarium_service.get_aquarium(aquarium_id)

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Zapisz pomiary jako CSV',
            f'pomiary_{aquarium.name.replace(" ", "_")}.csv',
            'CSV Files (*.csv)'
        )

        if filename:
            try:
                ExportService.export_measurements_to_csv(aquarium_id, filename, self.session)
                QtWidgets.QMessageBox.information(self, 'Sukces', f'Pomiary wyeksportowane do:\n{filename}')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Błąd eksportu: {str(e)}')

    def export_events(self):
        """Eksportuje wydarzenia do CSV."""
        current_item = self.aquarium_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, 'Błąd', 'Nie wybrano akwarium')
            return

        aquarium_id = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        aquarium = self.aquarium_service.get_aquarium(aquarium_id)

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Zapisz wydarzenia jako CSV',
            f'wydarzenia_{aquarium.name.replace(" ", "_")}.csv',
            'CSV Files (*.csv)'
        )

        if filename:
            try:
                ExportService.export_events_to_csv(aquarium_id, filename, self.session)
                QtWidgets.QMessageBox.information(self, 'Sukces', f'Wydarzenia wyeksportowane do:\n{filename}')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Błąd eksportu: {str(e)}')

    def create_backup(self):
        """Tworzy kopię zapasową bazy danych."""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wybierz folder dla backupu')

        if folder:
            try:
                backup_path = BackupService.create_backup(folder)
                QtWidgets.QMessageBox.information(
                    self, 'Sukces',
                    f'Kopia zapasowa bazy danych utworzona:\n{backup_path}'
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Błąd', f'Błąd tworzenia backupu: {str(e)}')

    def closeEvent(self, event):
        """Obsługuje zamknięcie aplikacji."""
        self.session.close()
        event.accept()

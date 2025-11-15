"""
Testy jednostkowe dla walidacji danych.
"""

import pytest
from datetime import datetime
from reef_manager.db.database import Database
from reef_manager.db.models import Aquarium, WaterMeasurement
from reef_manager.logic.services import AquariumService, MeasurementService


class TestValidation:
    """Testy walidacji danych."""

    @pytest.fixture
    def test_db(self):
        """Tworzy testową bazę danych w pamięci."""
        db = Database(':memory:')
        yield db

    @pytest.fixture
    def test_session(self, test_db):
        """Tworzy testową sesję."""
        session = test_db.get_session()
        yield session
        session.close()

    def test_create_valid_aquarium(self, test_session):
        """Test: tworzenie poprawnego akwarium."""
        service = AquariumService(test_session)

        aquarium = service.create_aquarium(
            name='Test Reef',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now(),
            description='Test aquarium'
        )

        assert aquarium.id is not None
        assert aquarium.name == 'Test Reef'
        assert aquarium.volume_liters == 100.0

    def test_measurement_valid_values(self, test_session):
        """Test: dodawanie pomiarów z poprawnymi wartościami."""
        # Najpierw utwórz akwarium
        aquarium_service = AquariumService(test_session)
        aquarium = aquarium_service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now()
        )

        # Dodaj pomiar
        measurement_service = MeasurementService(test_session)
        measurement = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime.now(),
            no3=10.0,
            po4=0.05,
            kh=8.0,
            ph=8.2,
            temperature=25.0,
            salinity=1.025
        )

        assert measurement.id is not None
        assert measurement.no3 == 10.0
        assert measurement.po4 == 0.05

    def test_measurement_partial_values(self, test_session):
        """Test: dodawanie pomiarów z częściowymi wartościami (niektóre None)."""
        aquarium_service = AquariumService(test_session)
        aquarium = aquarium_service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now()
        )

        measurement_service = MeasurementService(test_session)
        measurement = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime.now(),
            no3=10.0,
            po4=None,  # Pominięty parametr
            kh=None,
            ph=8.2,
            temperature=None,
            salinity=1.025
        )

        assert measurement.id is not None
        assert measurement.no3 == 10.0
        assert measurement.po4 is None
        assert measurement.ph == 8.2

    def test_measurement_negative_values_allowed(self, test_session):
        """Test: czy system akceptuje wartości (SQLite nie ma built-in constraints)."""
        aquarium_service = AquariumService(test_session)
        aquarium = aquarium_service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now()
        )

        measurement_service = MeasurementService(test_session)

        # Techniczne wartości ujemne mogą być dodane do bazy
        # (walidacja powinna być w GUI)
        measurement = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime.now(),
            no3=-5.0  # Wartość nieprawidłowa, ale technicznie dopuszczalna w bazie
        )

        # Sprawdź że została zapisana (ale GUI powinno to walidować)
        assert measurement.no3 == -5.0

    def test_get_latest_measurement(self, test_session):
        """Test: pobieranie ostatniego pomiaru."""
        aquarium_service = AquariumService(test_session)
        aquarium = aquarium_service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now()
        )

        measurement_service = MeasurementService(test_session)

        # Dodaj kilka pomiarów
        m1 = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime(2024, 1, 1, 10, 0),
            no3=10.0
        )

        m2 = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime(2024, 1, 2, 10, 0),
            no3=12.0
        )

        m3 = measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime(2024, 1, 3, 10, 0),
            no3=15.0
        )

        # Pobierz ostatni pomiar
        latest = measurement_service.get_latest_measurement(aquarium.id)

        assert latest is not None
        assert latest.no3 == 15.0
        assert latest.id == m3.id

    def test_delete_aquarium_cascades(self, test_session):
        """Test: usunięcie akwarium usuwa powiązane pomiary."""
        aquarium_service = AquariumService(test_session)
        aquarium = aquarium_service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now()
        )

        measurement_service = MeasurementService(test_session)
        measurement_service.add_measurement(
            aquarium_id=aquarium.id,
            measurement_date=datetime.now(),
            no3=10.0
        )

        # Usuń akwarium
        aquarium_service.delete_aquarium(aquarium.id)

        # Sprawdź że pomiary też zostały usunięte
        measurements = measurement_service.get_measurements(aquarium.id)
        assert len(measurements) == 0

    def test_aquarium_type_validation(self, test_session):
        """Test: różne typy akwariów są akceptowane."""
        service = AquariumService(test_session)

        types = ['reef', 'FOWLR', 'freshwater', 'custom_type']

        for aq_type in types:
            aquarium = service.create_aquarium(
                name=f'Test {aq_type}',
                aquarium_type=aq_type,
                volume_liters=100.0,
                start_date=datetime.now()
            )
            assert aquarium.aquarium_type == aq_type

    def test_empty_string_handling(self, test_session):
        """Test: obsługa pustych stringów."""
        service = AquariumService(test_session)

        aquarium = service.create_aquarium(
            name='Test',
            aquarium_type='reef',
            volume_liters=100.0,
            start_date=datetime.now(),
            description=''  # Pusty opis
        )

        assert aquarium.description == ''

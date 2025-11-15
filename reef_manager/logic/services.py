"""
Logika biznesowa i serwisy dla Reef Manager PRO.
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from reef_manager.db.models import Aquarium, WaterMeasurement, AquariumEvent, Inhabitant
from reef_manager.db.database import get_database


class AquariumService:
    """Serwis do zarządzania akwariami."""

    def __init__(self, session: Session):
        self.session = session

    def create_aquarium(self, name: str, aquarium_type: str, volume_liters: float,
                       start_date: datetime, description: str = "") -> Aquarium:
        """Tworzy nowe akwarium."""
        aquarium = Aquarium(
            name=name,
            aquarium_type=aquarium_type,
            volume_liters=volume_liters,
            start_date=start_date,
            description=description
        )
        self.session.add(aquarium)
        self.session.commit()
        return aquarium

    def get_all_aquariums(self) -> List[Aquarium]:
        """Pobiera wszystkie akwaria."""
        return self.session.query(Aquarium).order_by(Aquarium.name).all()

    def get_aquarium(self, aquarium_id: int) -> Optional[Aquarium]:
        """Pobiera akwarium po ID."""
        return self.session.query(Aquarium).filter(Aquarium.id == aquarium_id).first()

    def update_aquarium(self, aquarium_id: int, **kwargs) -> Optional[Aquarium]:
        """Aktualizuje akwarium."""
        aquarium = self.get_aquarium(aquarium_id)
        if aquarium:
            for key, value in kwargs.items():
                if hasattr(aquarium, key):
                    setattr(aquarium, key, value)
            self.session.commit()
        return aquarium

    def delete_aquarium(self, aquarium_id: int) -> bool:
        """Usuwa akwarium."""
        aquarium = self.get_aquarium(aquarium_id)
        if aquarium:
            self.session.delete(aquarium)
            self.session.commit()
            return True
        return False


class MeasurementService:
    """Serwis do zarządzania pomiarami parametrów wody."""

    def __init__(self, session: Session):
        self.session = session

    def add_measurement(self, aquarium_id: int, measurement_date: datetime,
                       no3: Optional[float] = None, po4: Optional[float] = None,
                       kh: Optional[float] = None, ph: Optional[float] = None,
                       temperature: Optional[float] = None, salinity: Optional[float] = None,
                       nh3_nh4: Optional[float] = None, comment: str = "") -> WaterMeasurement:
        """Dodaje nowy pomiar."""
        measurement = WaterMeasurement(
            aquarium_id=aquarium_id,
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
        self.session.add(measurement)
        self.session.commit()
        return measurement

    def get_measurements(self, aquarium_id: int, limit: Optional[int] = None) -> List[WaterMeasurement]:
        """Pobiera pomiary dla akwarium."""
        query = self.session.query(WaterMeasurement).filter(
            WaterMeasurement.aquarium_id == aquarium_id
        ).order_by(desc(WaterMeasurement.measurement_date))

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_latest_measurement(self, aquarium_id: int) -> Optional[WaterMeasurement]:
        """Pobiera ostatni pomiar dla akwarium."""
        measurements = self.get_measurements(aquarium_id, limit=1)
        return measurements[0] if measurements else None

    def get_measurements_in_range(self, aquarium_id: int, start_date: datetime,
                                  end_date: datetime) -> List[WaterMeasurement]:
        """Pobiera pomiary w zakresie dat."""
        return self.session.query(WaterMeasurement).filter(
            WaterMeasurement.aquarium_id == aquarium_id,
            WaterMeasurement.measurement_date >= start_date,
            WaterMeasurement.measurement_date <= end_date
        ).order_by(WaterMeasurement.measurement_date).all()

    def delete_measurement(self, measurement_id: int) -> bool:
        """Usuwa pomiar."""
        measurement = self.session.query(WaterMeasurement).filter(
            WaterMeasurement.id == measurement_id
        ).first()
        if measurement:
            self.session.delete(measurement)
            self.session.commit()
            return True
        return False


class EventService:
    """Serwis do zarządzania wydarzeniami."""

    def __init__(self, session: Session):
        self.session = session

    def add_event(self, aquarium_id: int, event_date: datetime, event_type: str,
                  description: str, related_params: str = "") -> AquariumEvent:
        """Dodaje nowe wydarzenie."""
        event = AquariumEvent(
            aquarium_id=aquarium_id,
            event_date=event_date,
            event_type=event_type,
            description=description,
            related_params=related_params
        )
        self.session.add(event)
        self.session.commit()
        return event

    def get_events(self, aquarium_id: int, limit: Optional[int] = None) -> List[AquariumEvent]:
        """Pobiera wydarzenia dla akwarium."""
        query = self.session.query(AquariumEvent).filter(
            AquariumEvent.aquarium_id == aquarium_id
        ).order_by(desc(AquariumEvent.event_date))

        if limit:
            query = query.limit(limit)

        return query.all()

    def delete_event(self, event_id: int) -> bool:
        """Usuwa wydarzenie."""
        event = self.session.query(AquariumEvent).filter(
            AquariumEvent.id == event_id
        ).first()
        if event:
            self.session.delete(event)
            self.session.commit()
            return True
        return False


class InhabitantService:
    """Serwis do zarządzania obsadą."""

    def __init__(self, session: Session):
        self.session = session

    def add_inhabitant(self, aquarium_id: int, species_name: str, inhabitant_type: str,
                      introduction_date: datetime, quantity: int = 1, status: str = 'active',
                      notes: str = "") -> Inhabitant:
        """Dodaje nowego mieszkańca."""
        inhabitant = Inhabitant(
            aquarium_id=aquarium_id,
            species_name=species_name,
            inhabitant_type=inhabitant_type,
            introduction_date=introduction_date,
            quantity=quantity,
            status=status,
            notes=notes
        )
        self.session.add(inhabitant)
        self.session.commit()
        return inhabitant

    def get_inhabitants(self, aquarium_id: int, include_inactive: bool = False) -> List[Inhabitant]:
        """Pobiera mieszkańców akwarium."""
        query = self.session.query(Inhabitant).filter(
            Inhabitant.aquarium_id == aquarium_id
        )

        if not include_inactive:
            query = query.filter(Inhabitant.status == 'active')

        return query.order_by(Inhabitant.species_name).all()

    def update_inhabitant(self, inhabitant_id: int, **kwargs) -> Optional[Inhabitant]:
        """Aktualizuje mieszkańca."""
        inhabitant = self.session.query(Inhabitant).filter(
            Inhabitant.id == inhabitant_id
        ).first()
        if inhabitant:
            for key, value in kwargs.items():
                if hasattr(inhabitant, key):
                    setattr(inhabitant, key, value)
            self.session.commit()
        return inhabitant

    def delete_inhabitant(self, inhabitant_id: int) -> bool:
        """Usuwa mieszkańca."""
        inhabitant = self.session.query(Inhabitant).filter(
            Inhabitant.id == inhabitant_id
        ).first()
        if inhabitant:
            self.session.delete(inhabitant)
            self.session.commit()
            return True
        return False


class BackupService:
    """Serwis do zarządzania kopiami zapasowymi."""

    @staticmethod
    def create_backup(backup_dir: Optional[str] = None) -> str:
        """
        Tworzy kopię zapasową bazy danych.

        Args:
            backup_dir: Katalog do zapisu kopii. Jeśli None, używa domyślnego.

        Returns:
            str: Ścieżka do pliku kopii zapasowej.
        """
        db = get_database()
        db_path = db.get_db_path()

        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(db_path), 'backups')

        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'reef_manager_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)

        shutil.copy2(db_path, backup_path)
        return backup_path


class ExportService:
    """Serwis do eksportu danych."""

    @staticmethod
    def export_measurements_to_csv(aquarium_id: int, output_path: str, session: Session):
        """Eksportuje pomiary do CSV."""
        import csv

        measurements = session.query(WaterMeasurement).filter(
            WaterMeasurement.aquarium_id == aquarium_id
        ).order_by(WaterMeasurement.measurement_date).all()

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Data', 'NO3', 'PO4', 'KH', 'pH', 'Temperatura', 'Zasolenie', 'NH3/NH4', 'Komentarz']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for m in measurements:
                writer.writerow({
                    'Data': m.measurement_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'NO3': m.no3 if m.no3 is not None else '',
                    'PO4': m.po4 if m.po4 is not None else '',
                    'KH': m.kh if m.kh is not None else '',
                    'pH': m.ph if m.ph is not None else '',
                    'Temperatura': m.temperature if m.temperature is not None else '',
                    'Zasolenie': m.salinity if m.salinity is not None else '',
                    'NH3/NH4': m.nh3_nh4 if m.nh3_nh4 is not None else '',
                    'Komentarz': m.comment if m.comment else ''
                })

    @staticmethod
    def export_events_to_csv(aquarium_id: int, output_path: str, session: Session):
        """Eksportuje wydarzenia do CSV."""
        import csv

        events = session.query(AquariumEvent).filter(
            AquariumEvent.aquarium_id == aquarium_id
        ).order_by(AquariumEvent.event_date).all()

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Data', 'Typ', 'Opis', 'Powiązane parametry']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for e in events:
                writer.writerow({
                    'Data': e.event_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Typ': e.event_type,
                    'Opis': e.description,
                    'Powiązane parametry': e.related_params if e.related_params else ''
                })

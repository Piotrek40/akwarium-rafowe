"""
Zarządzanie połączeniem z bazą danych SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from reef_manager.db.models import Base


class Database:
    """Klasa zarządzająca połączeniem z bazą danych."""

    def __init__(self, db_path: str = None):
        """
        Inicjalizacja bazy danych.

        Args:
            db_path: Ścieżka do pliku bazy danych. Jeśli None, użyje domyślnej lokalizacji.
        """
        if db_path is None:
            # Domyślna lokalizacja w katalogu użytkownika
            user_home = os.path.expanduser('~')
            app_dir = os.path.join(user_home, '.reef_manager')
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, 'reef_manager.db')

        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Stwórz tabele jeśli nie istnieją
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """
        Zwraca nową sesję bazy danych.

        Returns:
            Session: Sesja SQLAlchemy.
        """
        return self.SessionLocal()

    def get_db_path(self) -> str:
        """
        Zwraca ścieżkę do pliku bazy danych.

        Returns:
            str: Ścieżka do pliku bazy danych.
        """
        return self.db_path


# Globalna instancja bazy danych
_db_instance = None


def get_database(db_path: str = None) -> Database:
    """
    Zwraca globalną instancję bazy danych (singleton).

    Args:
        db_path: Ścieżka do pliku bazy danych (używana tylko przy pierwszym wywołaniu).

    Returns:
        Database: Instancja bazy danych.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance

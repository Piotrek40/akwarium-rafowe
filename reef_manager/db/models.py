"""
Modele bazy danych dla Reef Manager PRO.
Używa SQLAlchemy ORM do definiowania tabel.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Aquarium(Base):
    """Model akwarium."""
    __tablename__ = 'aquariums'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    aquarium_type = Column(String(50), nullable=False)  # reef, FOWLR, freshwater
    volume_liters = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relacje
    measurements = relationship('WaterMeasurement', back_populates='aquarium', cascade='all, delete-orphan')
    events = relationship('AquariumEvent', back_populates='aquarium', cascade='all, delete-orphan')
    inhabitants = relationship('Inhabitant', back_populates='aquarium', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Aquarium(id={self.id}, name='{self.name}', type='{self.aquarium_type}')>"


class WaterMeasurement(Base):
    """Model pomiaru parametrów wody."""
    __tablename__ = 'water_measurements'

    id = Column(Integer, primary_key=True)
    aquarium_id = Column(Integer, ForeignKey('aquariums.id'), nullable=False)
    measurement_date = Column(DateTime, nullable=False, default=datetime.now)

    # Parametry wody
    no3 = Column(Float)  # Azotany (mg/l)
    po4 = Column(Float)  # Fosforany (mg/l)
    kh = Column(Float)   # Twardość węglanowa (dKH)
    ph = Column(Float)   # pH
    temperature = Column(Float)  # Temperatura (°C)
    salinity = Column(Float)     # Zasolenie (SG)
    nh3_nh4 = Column(Float)      # Amoniak (mg/l)

    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relacja
    aquarium = relationship('Aquarium', back_populates='measurements')

    def __repr__(self):
        return f"<WaterMeasurement(id={self.id}, aquarium_id={self.aquarium_id}, date={self.measurement_date})>"


class AquariumEvent(Base):
    """Model wydarzenia w akwarium."""
    __tablename__ = 'aquarium_events'

    id = Column(Integer, primary_key=True)
    aquarium_id = Column(Integer, ForeignKey('aquariums.id'), nullable=False)
    event_date = Column(DateTime, nullable=False, default=datetime.now)
    event_type = Column(String(50), nullable=False)  # water_change, cleaning, death, addition, treatment, bacteria
    description = Column(Text, nullable=False)
    related_params = Column(Text)  # JSON string z powiązanymi parametrami
    created_at = Column(DateTime, default=datetime.now)

    # Relacja
    aquarium = relationship('Aquarium', back_populates='events')

    def __repr__(self):
        return f"<AquariumEvent(id={self.id}, type='{self.event_type}', date={self.event_date})>"


class Inhabitant(Base):
    """Model mieszkańca akwarium (ryba, koral, ślimak itp.)."""
    __tablename__ = 'inhabitants'

    id = Column(Integer, primary_key=True)
    aquarium_id = Column(Integer, ForeignKey('aquariums.id'), nullable=False)
    species_name = Column(String(200), nullable=False)
    inhabitant_type = Column(String(50), nullable=False)  # fish, coral, snail, crab, shrimp, other
    introduction_date = Column(DateTime, nullable=False, default=datetime.now)
    quantity = Column(Integer, default=1)
    status = Column(String(50), default='active')  # active, dead, transferred
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    # Relacja
    aquarium = relationship('Aquarium', back_populates='inhabitants')

    def __repr__(self):
        return f"<Inhabitant(id={self.id}, species='{self.species_name}', type='{self.inhabitant_type}')>"

"""
Kompleksowy test aplikacji Reef Manager PRO.
Sprawdza wszystkie importy, logikę i podstawowe funkcje.
"""

import sys
import os

# Dodaj katalog projektu do sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("REEF MANAGER PRO - KOMPREHENSYWNY TEST")
print("=" * 70)

# Test 1: Qt Compat
print("\n[TEST 1] Qt Compatibility Layer")
try:
    from reef_manager.qt_compat import (
        QtWidgets, QtCore, Signal, qDateTime_to_python, DialogResult, QT_API
    )
    print(f"  ✓ Qt compat importuje się poprawnie")
    print(f"  ✓ Używamy: {QT_API}")
    print(f"  ✓ DialogResult.Accepted = {DialogResult.Accepted}")

    # Test konwersji QDateTime
    now = QtCore.QDateTime.currentDateTime()
    py_datetime = qDateTime_to_python(now)
    print(f"  ✓ qDateTime_to_python działa: {type(py_datetime).__name__}")
except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    sys.exit(1)

# Test 2: Modele bazy danych
print("\n[TEST 2] Modele bazy danych")
try:
    from reef_manager.db.models import Aquarium, WaterMeasurement, AquariumEvent, Inhabitant
    from reef_manager.db.database import Database
    print("  ✓ Modele importują się poprawnie")

    # Test tworzenia bazy w pamięci
    db = Database(':memory:')
    print("  ✓ Baza danych w pamięci utworzona")

    session = db.get_session()
    print("  ✓ Sesja utworzona")
    session.close()
except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Silnik reguł
print("\n[TEST 3] Silnik reguł")
try:
    from reef_manager.logic.rules import RulesEngine

    engine = RulesEngine('reef')
    measurement = {
        'no3': 10.0,
        'po4': 0.05,
        'kh': 8.0,
        'ph': 8.2,
        'temperature': 25.0,
        'salinity': 1.025,
    }

    alerts, suggestions = engine.analyze_parameters(measurement)
    print(f"  ✓ Silnik reguł działa")
    print(f"  ✓ Wygenerowano {len(alerts)} alertów")
    print(f"  ✓ Pierwszy alert: {alerts[0][:50]}...")

    # Test wysokiego NO3
    measurement_bad = {'no3': 100.0}
    alerts_bad, suggestions_bad = engine.analyze_parameters(measurement_bad)
    assert len([a for a in alerts_bad if 'NO3' in a and 'wysokie' in a]) > 0
    print(f"  ✓ Wykrywanie wysokiego NO3 działa")

except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Serwisy
print("\n[TEST 4] Serwisy logiki biznesowej")
try:
    from reef_manager.logic.services import (
        AquariumService, MeasurementService, EventService,
        InhabitantService, BackupService, ExportService
    )
    from datetime import datetime

    # Test z bazą w pamięci
    db = Database(':memory:')
    session = db.get_session()

    # Test AquariumService
    aq_service = AquariumService(session)
    aquarium = aq_service.create_aquarium(
        name="Test Reef",
        aquarium_type="reef",
        volume_liters=100.0,
        start_date=datetime.now(),
        description="Test"
    )
    print(f"  ✓ AquariumService - utworzono akwarium ID={aquarium.id}")

    # Test MeasurementService
    meas_service = MeasurementService(session)
    measurement = meas_service.add_measurement(
        aquarium_id=aquarium.id,
        measurement_date=datetime.now(),
        no3=10.0,
        po4=0.05
    )
    print(f"  ✓ MeasurementService - dodano pomiar ID={measurement.id}")

    # Test EventService
    event_service = EventService(session)
    event = event_service.add_event(
        aquarium_id=aquarium.id,
        event_date=datetime.now(),
        event_type="water_change",
        description="Test podmiana"
    )
    print(f"  ✓ EventService - dodano wydarzenie ID={event.id}")

    # Test InhabitantService
    inh_service = InhabitantService(session)
    inhabitant = inh_service.add_inhabitant(
        aquarium_id=aquarium.id,
        species_name="Amphiprion ocellaris",
        inhabitant_type="fish",
        introduction_date=datetime.now(),
        quantity=2
    )
    print(f"  ✓ InhabitantService - dodano mieszkańca ID={inhabitant.id}")

    session.close()

except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: UI Components (tylko import, bez uruchamiania)
print("\n[TEST 5] Komponenty UI")
try:
    from reef_manager.ui.charts import ChartWidget
    print("  ✓ ChartWidget importuje się poprawnie")

    from reef_manager.ui.aquarium_views import AquariumDetailsWidget
    print("  ✓ AquariumDetailsWidget importuje się poprawnie")

    from reef_manager.ui.main_window import MainWindow
    print("  ✓ MainWindow importuje się poprawnie")

except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Main entry point
print("\n[TEST 6] Punkt wejścia aplikacji")
try:
    import reef_manager.main
    print("  ✓ reef_manager.main importuje się poprawnie")
except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Podsumowanie
print("\n" + "=" * 70)
print("WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE! ✓")
print("=" * 70)
print("\nAplikacja jest gotowa do uruchomienia:")
print("  python -m reef_manager.main")
print("\nLub z testami jednostkowymi:")
print("  pytest")
print("=" * 70)

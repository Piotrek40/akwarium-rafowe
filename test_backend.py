"""
Test backendu (bez GUI) - baza danych, logika, silnik reguł.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("REEF MANAGER PRO - TEST BACKENDU (BEZ GUI)")
print("=" * 70)

# Test 1: Modele bazy danych
print("\n[TEST 1] Modele bazy danych")
try:
    from reef_manager.db.models import Aquarium, WaterMeasurement, AquariumEvent, Inhabitant
    from reef_manager.db.database import Database
    print("  ✓ Modele importują się poprawnie")

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

# Test 2: Silnik reguł
print("\n[TEST 2] Silnik reguł")
try:
    from reef_manager.logic.rules import RulesEngine

    # Test dla akwarium reef
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
    print(f"  ✓ Silnik reguł dla 'reef' działa")
    print(f"  ✓ Alert: {alerts[0]}")
    assert any('w normie' in a.lower() for a in alerts), "Powinien być alert 'w normie'"

    # Test wysokiego NO3
    measurement_bad = {'no3': 100.0, 'po4': 0.05, 'kh': 8.0}
    alerts_bad, suggestions_bad = engine.analyze_parameters(measurement_bad)
    assert any('NO3' in a and 'wysokie' in a for a in alerts_bad), "Powinien wykryć wysoki NO3"
    print(f"  ✓ Wykrywanie wysokiego NO3 działa")
    print(f"  ✓ Sugestia: {suggestions_bad[0]}")

    # Test krytycznego amoniaku
    measurement_nh3 = {'nh3_nh4': 0.5}
    alerts_nh3, suggestions_nh3 = engine.analyze_parameters(measurement_nh3)
    assert any('KRYTYCZNIE' in a or 'amoniak' in a.lower() for a in alerts_nh3), "Powinien wykryć krytyczny amoniak"
    print(f"  ✓ Wykrywanie krytycznego amoniaku działa")

    # Test różnych typów akwariów
    for aq_type in ['reef', 'fowlr', 'freshwater']:
        engine_test = RulesEngine(aq_type)
        measurement_test = {'no3': 10.0, 'po4': 0.1}
        alerts_test, _ = engine_test.analyze_parameters(measurement_test)
        print(f"  ✓ Silnik reguł dla '{aq_type}' działa")

except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Serwisy
print("\n[TEST 3] Serwisy logiki biznesowej")
try:
    from reef_manager.logic.services import (
        AquariumService, MeasurementService, EventService,
        InhabitantService
    )
    from datetime import datetime

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

    # Test pobrania akwariów
    all_aquariums = aq_service.get_all_aquariums()
    assert len(all_aquariums) == 1
    print(f"  ✓ Pobieranie listy akwariów działa")

    # Test MeasurementService
    meas_service = MeasurementService(session)
    measurement = meas_service.add_measurement(
        aquarium_id=aquarium.id,
        measurement_date=datetime.now(),
        no3=10.0,
        po4=0.05,
        kh=8.0
    )
    print(f"  ✓ MeasurementService - dodano pomiar ID={measurement.id}")

    # Test pobierania ostatniego pomiaru
    latest = meas_service.get_latest_measurement(aquarium.id)
    assert latest.id == measurement.id
    print(f"  ✓ Pobieranie ostatniego pomiaru działa")

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

    # Test usuwania
    aq_service.delete_aquarium(aquarium.id)
    all_aquariums = aq_service.get_all_aquariums()
    assert len(all_aquariums) == 0
    print(f"  ✓ Usuwanie akwarium (cascade) działa")

    session.close()

except Exception as e:
    print(f"  ✗ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Podsumowanie
print("\n" + "=" * 70)
print("WSZYSTKIE TESTY BACKENDU PRZESZŁY POMYŚLNIE! ✓")
print("=" * 70)
print("\nLogika aplikacji (baza danych, silnik reguł) działa poprawnie.")
print("GUI można przetestować uruchamiając aplikację na Windows.")
print("=" * 70)

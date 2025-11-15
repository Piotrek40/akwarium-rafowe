"""
Testy jednostkowe dla silnika reguł.
"""

import pytest
from reef_manager.logic.rules import RulesEngine


class TestRulesEngine:
    """Testy dla silnika reguł."""

    def test_reef_parameters_all_ok(self):
        """Test: wszystkie parametry w normie dla akwarium reef."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.05,
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
            'nh3_nh4': 0.0
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        assert any('Wszystkie parametry w normie' in alert for alert in alerts)
        assert len(suggestions) == 0

    def test_high_no3_alert(self):
        """Test: wysoki NO3 generuje alert."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 50.0,  # Za wysoki
            'po4': 0.05,
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Sprawdź czy jest alert o wysokim NO3
        assert any('NO3' in alert and 'za wysokie' in alert for alert in alerts)
        # Sprawdź czy są sugestie
        assert len(suggestions) > 0
        assert any('podmian' in s.lower() for s in suggestions)

    def test_low_po4_alert(self):
        """Test: niski PO4 generuje alert."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.01,  # Za niski
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Sprawdź czy jest alert o niskim PO4
        assert any('PO4' in alert and 'za niskie' in alert for alert in alerts)

    def test_critical_ammonia(self):
        """Test: krytycznie wysoki amoniak."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.05,
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
            'nh3_nh4': 0.5  # Krytycznie wysoki
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Sprawdź czy jest krytyczny alert
        assert any('KRYTYCZNIE' in alert or 'amoniak' in alert.lower() for alert in alerts)
        # Sprawdź czy są natychmiastowe sugestie
        assert any('NATYCHMIAST' in s or 'Wymień' in s for s in suggestions)

    def test_elevated_ammonia(self):
        """Test: podwyższony amoniak."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.05,
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
            'nh3_nh4': 0.1  # Podwyższony
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Sprawdź czy jest alert o podwyższonym amoniaku
        assert any('amoniak' in alert.lower() for alert in alerts)

    def test_high_temperature(self):
        """Test: wysoka temperatura."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.05,
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 28.0,  # Za wysoka
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        assert any('Temperatura' in alert and 'za wysokie' in alert for alert in alerts)
        assert any('grzałk' in s.lower() or 'chiller' in s.lower() for s in suggestions)

    def test_low_kh(self):
        """Test: niski KH."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': 0.05,
            'kh': 6.0,  # Za niski
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        assert any('KH' in alert and 'za niskie' in alert for alert in alerts)

    def test_multiple_parameters_out_of_range(self):
        """Test: wiele parametrów poza zakresem."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 50.0,  # Za wysoki
            'po4': 0.15,  # Za wysoki
            'kh': 6.0,    # Za niski
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Powinny być co najmniej 3 alerty
        assert len([a for a in alerts if 'za' in a.lower()]) >= 3

    def test_partial_measurements(self):
        """Test: częściowe pomiary (niektóre parametry None)."""
        engine = RulesEngine('reef')
        measurement = {
            'no3': 10.0,
            'po4': None,  # Brak pomiaru
            'kh': 8.0,
            'ph': None,   # Brak pomiaru
            'temperature': 25.0,
            'salinity': None,  # Brak pomiaru
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Nie powinno być błędów, tylko alerty dla zmierzonych parametrów
        assert len(alerts) > 0

    def test_fowlr_aquarium_type(self):
        """Test: zakres parametrów dla akwarium FOWLR."""
        engine = RulesEngine('FOWLR')
        measurement = {
            'no3': 30.0,  # OK dla FOWLR, ale za wysokie dla reef
            'po4': 0.15,  # OK dla FOWLR
            'kh': 8.0,
            'ph': 8.2,
            'temperature': 25.0,
            'salinity': 1.025,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Dla FOWLR te wartości powinny być OK
        assert any('Wszystkie parametry w normie' in alert for alert in alerts)

    def test_freshwater_aquarium_type(self):
        """Test: zakres parametrów dla akwarium słodkowodnego."""
        engine = RulesEngine('freshwater')
        measurement = {
            'no3': 20.0,
            'po4': 0.5,
            'kh': 6.0,
            'ph': 7.0,
            'temperature': 24.0,
        }

        alerts, suggestions = engine.analyze_parameters(measurement)

        # Wszystko powinno być OK
        assert any('Wszystkie parametry w normie' in alert for alert in alerts)

    def test_parameter_status(self):
        """Test: sprawdzanie statusu pojedynczego parametru."""
        engine = RulesEngine('reef')

        assert engine.get_parameter_status('no3', 10.0) == 'OK'
        assert engine.get_parameter_status('no3', 1.0) == 'LOW'
        assert engine.get_parameter_status('no3', 50.0) == 'HIGH'
        assert engine.get_parameter_status('no3', None) == 'UNKNOWN'
        assert engine.get_parameter_status('invalid_param', 10.0) == 'UNKNOWN'

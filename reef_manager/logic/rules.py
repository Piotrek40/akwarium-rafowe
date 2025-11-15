"""
Silnik reguł dla Reef Manager PRO.
Generuje alerty i sugestie na podstawie parametrów wody.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParameterRange:
    """Zakres parametru z nazwą i jednostką."""
    min_value: float
    max_value: float
    unit: str
    name: str


class RulesEngine:
    """Silnik reguł do analizy parametrów wody i generowania alertów."""

    # Zakresy docelowe dla różnych typów akwariów
    RANGES = {
        'reef': {
            'no3': ParameterRange(2.0, 20.0, 'mg/l', 'Azotany (NO3)'),
            'po4': ParameterRange(0.02, 0.10, 'mg/l', 'Fosforany (PO4)'),
            'kh': ParameterRange(7.0, 9.0, 'dKH', 'Twardość węglanowa (KH)'),
            'ph': ParameterRange(7.8, 8.4, '', 'pH'),
            'temperature': ParameterRange(24.0, 26.0, '°C', 'Temperatura'),
            'salinity': ParameterRange(1.023, 1.026, 'SG', 'Zasolenie'),
        },
        'fowlr': {  # Fish Only With Live Rock
            'no3': ParameterRange(5.0, 40.0, 'mg/l', 'Azotany (NO3)'),
            'po4': ParameterRange(0.05, 0.20, 'mg/l', 'Fosforany (PO4)'),
            'kh': ParameterRange(7.0, 10.0, 'dKH', 'Twardość węglanowa (KH)'),
            'ph': ParameterRange(7.8, 8.4, '', 'pH'),
            'temperature': ParameterRange(24.0, 27.0, '°C', 'Temperatura'),
            'salinity': ParameterRange(1.020, 1.026, 'SG', 'Zasolenie'),
        },
        'freshwater': {
            'no3': ParameterRange(5.0, 40.0, 'mg/l', 'Azotany (NO3)'),
            'po4': ParameterRange(0.1, 2.0, 'mg/l', 'Fosforany (PO4)'),
            'kh': ParameterRange(4.0, 8.0, 'dKH', 'Twardość węglanowa (KH)'),
            'ph': ParameterRange(6.5, 7.5, '', 'pH'),
            'temperature': ParameterRange(22.0, 26.0, '°C', 'Temperatura'),
        }
    }

    def __init__(self, aquarium_type: str = 'reef'):
        """
        Inicjalizacja silnika reguł.

        Args:
            aquarium_type: Typ akwarium ('reef', 'FOWLR', 'freshwater').
        """
        self.aquarium_type = aquarium_type.lower()
        if self.aquarium_type not in self.RANGES:
            self.aquarium_type = 'reef'  # Domyślnie

    def analyze_parameters(self, measurement: Dict[str, Optional[float]]) -> Tuple[List[str], List[str]]:
        """
        Analizuje parametry wody i generuje alerty oraz sugestie.

        Args:
            measurement: Słownik z pomiarami (klucze: 'no3', 'po4', 'kh', 'ph', 'temperature', 'salinity', 'nh3_nh4').

        Returns:
            Tuple[List[str], List[str]]: (lista alertów, lista sugestii).
        """
        alerts = []
        suggestions = []

        ranges = self.RANGES[self.aquarium_type]

        # Sprawdź każdy parametr
        for param_name, param_range in ranges.items():
            value = measurement.get(param_name)

            if value is None:
                continue

            # Sprawdź czy wartość jest poza zakresem
            if value < param_range.min_value:
                alerts.append(
                    f"⚠️ {param_range.name} za niskie: {value} {param_range.unit} "
                    f"(zakres: {param_range.min_value}-{param_range.max_value} {param_range.unit})"
                )
                suggestions.extend(self._get_low_suggestions(param_name))

            elif value > param_range.max_value:
                alerts.append(
                    f"⚠️ {param_range.name} za wysokie: {value} {param_range.unit} "
                    f"(zakres: {param_range.min_value}-{param_range.max_value} {param_range.unit})"
                )
                suggestions.extend(self._get_high_suggestions(param_name))

        # Sprawdź amoniak (jeśli jest)
        nh3_nh4 = measurement.get('nh3_nh4')
        if nh3_nh4 is not None and nh3_nh4 > 0.0:
            if nh3_nh4 > 0.25:
                alerts.append(f"🚨 KRYTYCZNIE wysoki amoniak: {nh3_nh4} mg/l - wymaga natychmiastowej reakcji!")
                suggestions.append("NATYCHMIAST: Wymień 30-50% wody")
                suggestions.append("Sprawdź czy filtr biologiczny działa prawidłowo")
            elif nh3_nh4 > 0.05:
                alerts.append(f"⚠️ Podwyższony amoniak: {nh3_nh4} mg/l")
                suggestions.append("Rozważ podmianę wody (20-30%)")
                suggestions.append("Sprawdź czy nie ma martwych organizmów")

        # Jeśli wszystko OK
        if not alerts:
            alerts.append("✅ Wszystkie parametry w normie")

        return alerts, suggestions

    def _get_low_suggestions(self, param: str) -> List[str]:
        """Zwraca sugestie dla niskich wartości parametru."""
        suggestions_map = {
            'no3': ["Zwiększ karmienie (ostrożnie)", "Sprawdź czy nie ma wycieków w filtrze"],
            'po4': ["Zwiększ karmienie", "Rozważ dodanie nawozów dla korali"],
            'kh': ["Dodaj preparat podnoszący KH", "Sprawdź system buforowania"],
            'ph': ["Sprawdź poziom CO2 w pomieszczeniu", "Rozważ użycie bufora pH", "Zwiększ aerację"],
            'temperature': ["Sprawdź grzałkę", "Zwiększ temperaturę pomieszczenia"],
            'salinity': ["Dodaj soli morskiej", "Uzupełnij ewaporację wodą słoną"],
        }
        return suggestions_map.get(param, [])

    def _get_high_suggestions(self, param: str) -> List[str]:
        """Zwraca sugestie dla wysokich wartości parametru."""
        suggestions_map = {
            'no3': [
                "Wykonaj podmianę wody (20-30%)",
                "Zmniejsz karmienie",
                "Sprawdź czy filtr działa prawidłowo",
                "Rozważ użycie żywicy antyazotanowej lub reaktora NO3"
            ],
            'po4': [
                "Wykonaj podmianę wody",
                "Zmniejsz karmienie",
                "Użyj absorbera fosforanów (np. GFO)",
                "Sprawdź jakość soli morskiej"
            ],
            'kh': [
                "Zmniejsz dozowanie buforu KH",
                "Wykonaj podmianę wody",
                "Sprawdź czy woda RO jest czysta"
            ],
            'ph': [
                "Zwiększ aerację",
                "Sprawdź poziom KH",
                "Sprawdź wentylację pomieszczenia",
                "Rozważ użycie reaktora wapniowego"
            ],
            'temperature': [
                "Sprawdź grzałkę - może być uszkodzona",
                "Zmniejsz oświetlenie",
                "Zwiększ wentylację",
                "Rozważ użycie wentylatora lub chillera"
            ],
            'salinity': [
                "Uzupełnij ewaporację wodą RO/DI",
                "Wykonaj podmianę wody",
                "Sprawdź refraktometr/densymetr"
            ],
        }
        return suggestions_map.get(param, [])

    def get_parameter_status(self, param_name: str, value: Optional[float]) -> str:
        """
        Zwraca status parametru (OK, LOW, HIGH, UNKNOWN).

        Args:
            param_name: Nazwa parametru.
            value: Wartość parametru.

        Returns:
            str: Status ('OK', 'LOW', 'HIGH', 'UNKNOWN').
        """
        if value is None:
            return 'UNKNOWN'

        ranges = self.RANGES[self.aquarium_type]
        param_range = ranges.get(param_name)

        if param_range is None:
            return 'UNKNOWN'

        if value < param_range.min_value:
            return 'LOW'
        elif value > param_range.max_value:
            return 'HIGH'
        else:
            return 'OK'

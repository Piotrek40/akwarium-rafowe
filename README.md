# Reef Manager PRO

Desktopowa aplikacja do zarządzania akwariami rafowymi (i innymi typami akwariów) - działająca offline na Windows 11.

## Funkcje

- **Zarządzanie wieloma akwariami** - dodawaj, edytuj i śledź różne akwaria
- **Pomiary parametrów wody** - loguj NO3, PO4, KH, pH, temperaturę, zasolenie i amoniak
- **Wykresy** - wizualizuj zmiany parametrów w czasie
- **Dziennik wydarzeń** - zapisuj podmiany wody, czyszczenie, śmierci organizmów i inne wydarzenia
- **Obsada** - prowadź listę ryb, korali, ślimaków i innych mieszkańców
- **Silnik reguł** - automatyczne alerty i sugestie na podstawie parametrów wody
- **Eksport danych** - eksportuj pomiary i wydarzenia do CSV
- **Backup** - twórz kopie zapasowe bazy danych

## Wymagania systemowe

- Windows 11
- Python 3.8 lub nowszy

## Instalacja

### Krok 1: Sprawdź wersję Pythona

Otwórz PowerShell lub Command Prompt i sprawdź wersję Pythona:

```bash
python --version
```

Powinieneś zobaczyć Python 3.8 lub nowszy. Jeśli nie masz Pythona, pobierz go z [python.org](https://www.python.org/downloads/).

### Krok 2: Sklonuj lub rozpakuj projekt

Jeśli używasz git:

```bash
git clone <repository-url>
cd akwarium-rafowe
```

Lub rozpakuj projekt do wybranego folderu i otwórz ten folder w terminalu.

### Krok 3: Utwórz wirtualne środowisko

W folderze projektu wykonaj:

```bash
python -m venv venv
```

### Krok 4: Aktywuj wirtualne środowisko

**PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**Command Prompt:**
```bash
venv\Scripts\activate.bat
```

Po aktywacji zobaczysz `(venv)` na początku linii poleceń.

### Krok 5: Zainstaluj zależności

```bash
pip install -r requirements.txt
```

Instalacja może potrwać kilka minut.

## Uruchomienie aplikacji

### Sposób 1: Bezpośrednie uruchomienie

```bash
python -m reef_manager.main
```

### Sposób 2: Jako moduł

```bash
python reef_manager/main.py
```

**Ważne:** Upewnij się, że jesteś w głównym katalogu projektu (tam gdzie znajduje się folder `reef_manager/`) i że wirtualne środowisko jest aktywowane (widoczne `(venv)` w terminalu).

## Struktura projektu

```
akwarium-rafowe/
│
├── reef_manager/              # Główny pakiet aplikacji
│   ├── __init__.py
│   ├── main.py               # Punkt wejścia aplikacji
│   │
│   ├── db/                   # Warstwa bazy danych
│   │   ├── __init__.py
│   │   ├── models.py         # Modele SQLAlchemy
│   │   └── database.py       # Zarządzanie połączeniem
│   │
│   ├── logic/                # Logika biznesowa
│   │   ├── __init__.py
│   │   ├── rules.py          # Silnik reguł i alertów
│   │   └── services.py       # Serwisy do operacji na danych
│   │
│   ├── ui/                   # Interfejs użytkownika
│   │   ├── __init__.py
│   │   ├── main_window.py    # Główne okno aplikacji
│   │   ├── aquarium_views.py # Widoki akwariów (zakładki)
│   │   └── charts.py         # Komponenty wykresów
│   │
│   └── tests/                # Testy jednostkowe
│       ├── __init__.py
│       ├── test_rules.py     # Testy silnika reguł
│       └── test_validation.py # Testy walidacji
│
├── requirements.txt          # Zależności Python
└── README.md                 # Ten plik
```

## Lokalizacja bazy danych

Baza danych SQLite jest automatycznie tworzona przy pierwszym uruchomieniu aplikacji w lokalizacji:

```
C:\Users\<TwojaNazwaUżytkownika>\.reef_manager\reef_manager.db
```

Ścieżka jest wyświetlana w lewym dolnym rogu aplikacji.

## Tworzenie kopii zapasowej

### Przez aplikację (zalecane)

1. Uruchom aplikację
2. Kliknij przycisk "Zrób backup bazy" w lewym panelu
3. Wybierz folder gdzie chcesz zapisać kopię
4. Kopia zostanie zapisana z timestampem, np. `reef_manager_backup_20240115_143022.db`

### Ręcznie

Skopiuj plik bazy danych z lokalizacji:
```
C:\Users\<TwojaNazwaUżytkownika>\.reef_manager\reef_manager.db
```

Do bezpiecznej lokalizacji (np. zewnętrzny dysk, chmura).

## Eksport danych do CSV

### Pomiary parametrów wody

1. Wybierz akwarium z listy
2. Kliknij "Eksportuj pomiary (CSV)"
3. Wybierz lokalizację i nazwę pliku
4. Plik CSV będzie zawierał wszystkie pomiary dla wybranego akwarium

### Wydarzenia

1. Wybierz akwarium z listy
2. Kliknij "Eksportuj wydarzenia (CSV)"
3. Wybierz lokalizację i nazwę pliku
4. Plik CSV będzie zawierał wszystkie wydarzenia dla wybranego akwarium

## Uruchamianie testów

Testy jednostkowe sprawdzają poprawność działania silnika reguł i walidacji danych.

### Uruchomienie wszystkich testów

```bash
pytest
```

### Uruchomienie z dodatkowymi informacjami

```bash
pytest -v
```

### Uruchomienie konkretnego pliku testów

```bash
pytest reef_manager/tests/test_rules.py
```

### Co testują testy?

**test_rules.py:**
- Poprawność generowania alertów dla parametrów poza zakresem
- Działanie silnika reguł dla różnych typów akwariów (reef, FOWLR, freshwater)
- Wykrywanie krytycznych wartości (np. wysoki amoniak)
- Generowanie odpowiednich sugestii

**test_validation.py:**
- Tworzenie akwariów i pomiarów
- Poprawność zapisu i odczytu danych
- Kaskadowe usuwanie (usunięcie akwarium usuwa powiązane dane)
- Obsługa wartości None i częściowych pomiarów

## Typy akwariów i zakresy parametrów

### Reef (akwarium rafowe)
- NO3: 2-20 mg/l
- PO4: 0.02-0.10 mg/l
- KH: 7-9 dKH
- pH: 7.8-8.4
- Temperatura: 24-26°C
- Zasolenie: 1.023-1.026 SG

### FOWLR (Fish Only With Live Rock)
- NO3: 5-40 mg/l
- PO4: 0.05-0.20 mg/l
- KH: 7-10 dKH
- pH: 7.8-8.4
- Temperatura: 24-27°C
- Zasolenie: 1.020-1.026 SG

### Freshwater (słodkowodne)
- NO3: 5-40 mg/l
- PO4: 0.1-2.0 mg/l
- KH: 4-8 dKH
- pH: 6.5-7.5
- Temperatura: 22-26°C

## Rozwiązywanie problemów

### Błąd: "python" nie jest rozpoznawany

Upewnij się, że Python jest dodany do PATH. Podczas instalacji Pythona zaznacz opcję "Add Python to PATH".

### Błąd importu PyQt6

Upewnij się, że:
1. Wirtualne środowisko jest aktywowane (widoczne `(venv)`)
2. Zainstalowałeś zależności: `pip install -r requirements.txt`

### Aplikacja się nie uruchamia

1. Sprawdź czy jesteś w głównym katalogu projektu
2. Sprawdź czy wirtualne środowisko jest aktywowane
3. Uruchom: `python -m reef_manager.main`

### Błąd przy tworzeniu wykresów

Jeśli matplotlib ma problemy, spróbuj:
```bash
pip uninstall matplotlib
pip install matplotlib==3.8.2
```

### Problem z uprawnieniami do pliku bazy danych

Upewnij się, że masz prawa zapisu do folderu:
```
C:\Users\<TwojaNazwaUżytkownika>\.reef_manager\
```

## Jak używać aplikacji?

### Pierwsze uruchomienie

1. **Dodaj swoje pierwsze akwarium:**
   - Kliknij "Dodaj akwarium"
   - Wypełnij formularz (nazwa, typ, objętość, data startu)
   - Kliknij OK

2. **Dodaj pomiar parametrów:**
   - Wybierz akwarium z listy po lewej
   - Przejdź do zakładki "Parametry"
   - Wypełnij formularz pomiarów (możesz pominąć niektóre parametry)
   - Kliknij "Dodaj pomiar"

3. **Sprawdź alerty:**
   - Przejdź do zakładki "Podsumowanie"
   - Zobacz alerty i sugestie wygenerowane przez silnik reguł

4. **Zobacz wykresy:**
   - Przejdź do zakładki "Wykresy"
   - Wybierz parametr i zakres dat
   - Kliknij "Odśwież wykres"

### Codzienne użytkowanie

- **Logowanie pomiarów:** Regularnie dodawaj pomiary w zakładce "Parametry"
- **Dziennik wydarzeń:** Zapisuj ważne wydarzenia (podmiany wody, czyszczenie) w zakładce "Wydarzenia"
- **Obsada:** Prowadź listę organizmów w zakładce "Obsada"
- **Monitoring:** Sprawdzaj zakładkę "Podsumowanie" aby zobaczyć aktualny stan i alerty

## Technologie

- **Python 3.8+** - język programowania
- **PyQt6** - framework GUI
- **SQLAlchemy** - ORM do zarządzania bazą danych
- **SQLite** - baza danych (offline, lokalnie)
- **matplotlib** - biblioteka do wykresów
- **pytest** - framework do testów jednostkowych

## Licencja

Projekt stworzony na potrzeby osobiste / edukacyjne.

## Wsparcie

W razie problemów:
1. Sprawdź sekcję "Rozwiązywanie problemów" powyżej
2. Upewnij się, że masz zainstalowane wszystkie wymagania
3. Sprawdź czy używasz Python 3.8 lub nowszy

## Autor

Reef Manager PRO - stworzone przez Claude Code

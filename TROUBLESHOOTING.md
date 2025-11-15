# Rozwiązywanie problemów - Reef Manager PRO

## Problem: "DLL load failed while importing QtWidgets" na Windows

To najczęstszy problem z PyQt6 na Windows 11. Oto sprawdzone rozwiązania:

### Diagnoza

Najpierw uruchom skrypt diagnostyczny aby zobaczyć co dokładnie jest nie tak:

```bash
python diagnose.py
```

### Rozwiązanie 1: Użyj starszej wersji PyQt6 (POLECANE)

```bash
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt6==6.5.0
python -m reef_manager.main
```

### Rozwiązanie 2: Zainstaluj Visual C++ Redistributables

PyQt6 wymaga Microsoft Visual C++ Redistributables:

1. Pobierz: [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Zainstaluj
3. **Zrestartuj komputer**
4. Spróbuj ponownie uruchomić aplikację

### Rozwiązanie 3: Użyj PySide6 zamiast PyQt6

PySide6 to oficjalna biblioteka Qt dla Pythona i często działa lepiej na Windows:

```bash
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PySide6==6.6.0
python run_app.py
```

**Uwaga:** Użyj `run_app.py` zamiast `reef_manager/main.py` - ten skrypt automatycznie wykrywa dostępną bibliotekę Qt.

### Rozwiązanie 4: Stwórz nowe czyste venv

Czasem problem jest z nakładającymi się środowiskami (conda + venv):

```bash
# Usuń stare venv
Remove-Item -Recurse -Force venv

# Dezaktywuj conda jeśli jest aktywne
conda deactivate

# Stwórz nowe czyste venv używając systemowego Pythona
py -m venv venv

# Aktywuj
venv\Scripts\Activate.ps1

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python -m reef_manager.main
```

---

## Problem: "ModuleNotFoundError: No module named 'reef_manager'"

### Przyczyna

Uruchamiasz aplikację z **złego katalogu**.

### Rozwiązanie

Upewnij się że jesteś w katalogu głównym projektu (tam gdzie jest folder `reef_manager/`):

```bash
# ZŁY katalog:
C:\Users\PC1\Desktop\akwarium\reef_manager>

# DOBRY katalog:
C:\Users\PC1\Desktop\akwarium>
```

Wróć do głównego katalogu:

```bash
cd C:\Users\PC1\Desktop\akwarium
```

Potem uruchom:

```bash
python -m reef_manager.main
```

---

## Problem: Conda i venv konfliktują

### Objawy

Widzisz `(base) (venv)` w terminalu i aplikacja nie działa.

### Rozwiązanie

Dezaktywuj conda przed aktywacją venv:

```bash
conda deactivate
venv\Scripts\Activate.ps1
python -m reef_manager.main
```

---

## Problem: Testy nie działają

### Jeśli pytest-qt powoduje problemy:

```bash
pip uninstall -y pytest-qt
pytest
```

---

## Problem: Import matplotlib nie działa

### Rozwiązanie

```bash
pip uninstall matplotlib
pip install matplotlib==3.8.2
```

---

## Problem: Brak uprawnień do tworzenia bazy danych

### Objawy

Błąd przy próbie utworzenia bazy danych w `C:\Users\<nazwa>\.reef_manager\`

### Rozwiązanie

Uruchom PowerShell jako administrator lub zmień lokalizację bazy danych w kodzie.

---

## Szybka ściąga - Kompletna reinstalacja

Jeśli nic nie działa, zacznij od zera:

```bash
# 1. Usuń venv
Remove-Item -Recurse -Force venv

# 2. Dezaktywuj conda
conda deactivate

# 3. Stwórz nowe venv
python -m venv venv

# 4. Aktywuj
venv\Scripts\Activate.ps1

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Zainstaluj pakiety jeden po drugim
pip install SQLAlchemy==2.0.25
pip install matplotlib==3.8.2
pip install PyQt6==6.5.0
# lub: pip install PySide6==6.6.0

# 7. Uruchom diagnostykę
python diagnose.py

# 8. Uruchom aplikację
python -m reef_manager.main
# lub jeśli używasz PySide6: python run_app.py
```

---

## Nadal nie działa?

Uruchom **pełną diagnostykę** i prześlij wynik:

```bash
python diagnose.py > diagnostyka.txt
```

Otwórz `diagnostyka.txt` i sprawdź co jest nie tak.

---

## Windows-specific: Sprawdź zainstalowane Visual C++ Redistributables

1. Otwórz "Dodaj lub usuń programy" (Win + X → Apps)
2. Wyszukaj "Microsoft Visual C++"
3. Upewnij się że masz zainstalowane wersje 2015-2022 (x64)
4. Jeśli nie ma, zainstaluj z: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Testowanie bez GUI (czy reszta działa)

Możesz przetestować czy logika aplikacji działa bez GUI:

```bash
python -c "from reef_manager.db import models, database; from reef_manager.logic import rules, services; print('✓ Backend działa poprawnie')"
```

Jeśli to działa, problem jest tylko z biblioteką Qt (PyQt6/PySide6).

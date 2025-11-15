# Szybki Start - Reef Manager PRO (Windows 11)

## Co zrobić jeśli aplikacja nie uruchamia się?

### KROK 1: Upewnij się że jesteś w dobrym katalogu

```bash
cd C:\Users\PC1\Desktop\akwarium
```

**WAŻNE:** Musisz być w katalogu głównym (tam gdzie jest folder `reef_manager/`), **NIE** wewnątrz `reef_manager/`!

### KROK 2: Aktywuj wirtualne środowisko

```bash
venv\Scripts\Activate.ps1
```

Jeśli widzisz błąd, użyj:
```bash
venv\Scripts\activate.bat
```

Powinieneś zobaczyć `(venv)` na początku linii.

### KROK 3: Zainstaluj PySide6 (działa lepiej na Windows!)

Diagnostyka pokazała że masz **PySide6 zainstalowany i działa** ✓

Jeśli jednak nie jest zainstalowany:

```bash
pip install PySide6==6.6.0 SQLAlchemy==2.0.25 matplotlib==3.8.2
```

### KROK 4: Uruchom aplikację

```bash
python -m reef_manager.main
```

Powinieneś zobaczyć:
```
✓ Używam PySide6
```

A potem otwarte okno aplikacji!

---

## Kompletna reinstalacja (jeśli nic nie pomaga)

Jeśli nadal nie działa, zacznij od zera:

```bash
# 1. Usuń stare venv
Remove-Item -Recurse -Force venv

# 2. Dezaktywuj conda (jeśli aktywne)
conda deactivate

# 3. Stwórz nowe venv
python -m venv venv

# 4. Aktywuj
venv\Scripts\Activate.ps1

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Zainstaluj TYLKO PySide6 (stabilniejsze na Windows)
pip install PySide6==6.6.0
pip install SQLAlchemy==2.0.25
pip install matplotlib==3.8.2

# 7. Uruchom
python -m reef_manager.main
```

---

## Często zadawane pytania

### Dlaczego PySide6 zamiast PyQt6?

PySide6 jest oficjalną biblioteką Qt dla Pythona i często działa **stabilniej na Windows 11**. Kod został napisany tak, żeby działał z obiema bibliotekami.

### Co zrobić z błędem "DLL load failed"?

To oznacza problem z PyQt6. Rozwiązanie: użyj PySide6 (patrz KROK 3).

### Co zrobić jeśli widzę "(base) (venv)"?

Conda i venv nakładają się. Dezaktywuj conda przed aktywacją venv:

```bash
conda deactivate
venv\Scripts\Activate.ps1
```

### Gdzie jest baza danych?

```
C:\Users\<TwojaNazwa>\.reef_manager\reef_manager.db
```

### Jak zrobić backup?

W aplikacji: Przycisk "Zrób backup bazy" → wybierz folder

### Jak uruchomić testy?

```bash
pytest
```

---

## Teraz spróbuj!

1. Otwórz PowerShell
2. `cd C:\Users\PC1\Desktop\akwarium`
3. `venv\Scripts\Activate.ps1`
4. `python -m reef_manager.main`

Gotowe! Aplikacja powinna się uruchomić.

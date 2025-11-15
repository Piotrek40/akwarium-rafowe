"""
Skrypt diagnostyczny dla Reef Manager PRO.
Sprawdza konfigurację środowiska i wykrywa problemy.
"""

import sys
import os

print("=" * 60)
print("REEF MANAGER PRO - DIAGNOSTYKA ŚRODOWISKA")
print("=" * 60)

# 1. Sprawdź wersję Pythona
print(f"\n1. Python:")
print(f"   Wersja: {sys.version}")
print(f"   Ścieżka: {sys.executable}")

# 2. Sprawdź sys.path
print(f"\n2. Python Path (sys.path):")
for i, path in enumerate(sys.path[:5], 1):
    print(f"   {i}. {path}")

# 3. Sprawdź czy venv jest aktywowany
print(f"\n3. Wirtualne środowisko:")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print(f"   ✓ VENV aktywowany")
    print(f"   Prefix: {sys.prefix}")
else:
    print(f"   ✗ VENV NIE aktywowany!")
    print(f"   Prefix: {sys.prefix}")

# 4. Sprawdź zainstalowane pakiety Qt
print(f"\n4. Biblioteki Qt:")

# PyQt6
try:
    import PyQt6
    print(f"   ✓ PyQt6 zainstalowany")
    print(f"     Wersja: {PyQt6.__version__ if hasattr(PyQt6, '__version__') else 'unknown'}")
    try:
        from PyQt6.QtWidgets import QApplication
        print(f"     ✓ PyQt6.QtWidgets importuje się poprawnie")
    except Exception as e:
        print(f"     ✗ PyQt6.QtWidgets BŁĄD: {e}")
except ImportError:
    print(f"   ✗ PyQt6 NIE zainstalowany")

# PySide6
try:
    import PySide6
    print(f"   ✓ PySide6 zainstalowany")
    print(f"     Wersja: {PySide6.__version__}")
    try:
        from PySide6.QtWidgets import QApplication
        print(f"     ✓ PySide6.QtWidgets importuje się poprawnie")
    except Exception as e:
        print(f"     ✗ PySide6.QtWidgets BŁĄD: {e}")
except ImportError:
    print(f"   ✗ PySide6 NIE zainstalowany")

# 5. Sprawdź inne pakiety
print(f"\n5. Inne wymagane pakiety:")

packages = {
    'SQLAlchemy': 'sqlalchemy',
    'matplotlib': 'matplotlib',
    'pytest': 'pytest'
}

for name, module in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"   ✓ {name}: {version}")
    except ImportError:
        print(f"   ✗ {name}: NIE zainstalowany")

# 6. Sprawdź Visual C++ Redistributables (pośrednio)
print(f"\n6. System:")
print(f"   Platforma: {sys.platform}")
if sys.platform == 'win32':
    print(f"   ℹ  Uwaga: PyQt6 na Windows wymaga Visual C++ Redistributables")
    print(f"      Pobierz z: https://aka.ms/vs/17/release/vc_redist.x64.exe")

# 7. Rekomendacje
print(f"\n7. REKOMENDACJE:")
print(f"=" * 60)

# Sprawdź PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 działa - możesz uruchomić aplikację:")
    print("  python -m reef_manager.main")
except Exception as e:
    print(f"✗ PyQt6 nie działa (błąd: {type(e).__name__})")
    print("\nSPRÓBUJ TYCH KROKÓW (kolejno):")
    print("\n  KROK 1: Odinstaluj i zainstaluj starszą wersję PyQt6")
    print("    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip")
    print("    pip install PyQt6==6.5.0")
    print("\n  KROK 2: Jeśli nie pomoże, zainstaluj Visual C++ Redistributables")
    print("    Pobierz: https://aka.ms/vs/17/release/vc_redist.x64.exe")
    print("    Zainstaluj i zrestartuj komputer")
    print("\n  KROK 3: Jeśli nadal nie działa, użyj PySide6 (alternatywa)")
    print("    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip")
    print("    pip install PySide6==6.6.0")
    print("    python run_app.py")

print("\n" + "=" * 60)
print("Koniec diagnostyki")
print("=" * 60)

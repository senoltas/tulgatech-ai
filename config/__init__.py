from pathlib import Path

# Proje kök dizini (tulgatech_ai)
BASE_DIR = Path(__file__).resolve().parent.parent

# Standart klasörler
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"

# İstersen otomatik oluştur (zararsız)
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

"""
update_db.py — Vervang de ruwe database met de meest recente versie uit de survey-app.

Wat dit script doet:
  1. Controleer of de brondatabase bestaat.
  2. Als er al een database.db in data/raw/ staat, hernoem die naar database_old.db
     (een eventuele bestaande database_old.db wordt overschreven).
  3. Kopieer de brondatabase naar data/raw/database.db.

Gebruik:
    python scripts/update_db.py
    (uitvoeren vanuit de bradley_terry/ root)
"""

import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Paden — pas SOURCE_DB aan als de survey-app ergens anders komt te staan
# ---------------------------------------------------------------------------
SOURCE_DB = Path(
    r"C:\Users\Thijs\OneDrive\Documents\Studie\EPA\Second_year\Afstuderen\Project"
    r"\core-usage\surveys\survey-intersection-safety\database.db"
)

# Script staat in scripts/, dus de root is één niveau omhoog
ROOT_DIR    = Path(__file__).parent.parent
RAW_DIR     = ROOT_DIR / "data" / "raw"
DEST_DB     = RAW_DIR / "database.db"
DEST_DB_OLD = RAW_DIR / "database_old.db"

# ---------------------------------------------------------------------------
# Valideer bronbestand
# ---------------------------------------------------------------------------
if not SOURCE_DB.exists():
    raise FileNotFoundError(
        f"Bronbestand niet gevonden:\n  {SOURCE_DB}\n"
        "Controleer of de survey-app draait en het pad klopt."
    )

# ---------------------------------------------------------------------------
# Zorg dat de doelmap bestaat
# ---------------------------------------------------------------------------
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Hernoem bestaande database naar database_old.db
# ---------------------------------------------------------------------------
if DEST_DB.exists():
    shutil.copy2(DEST_DB, DEST_DB_OLD)  # copy2 behoudt metadata (aanmaakdatum etc.)
    print(f"Bestaande database gearchiveerd als:\n  {DEST_DB_OLD}")
else:
    print("Geen bestaande database gevonden — eerste keer kopiëren.")

# ---------------------------------------------------------------------------
# Kopieer de nieuwe database
# ---------------------------------------------------------------------------
shutil.copy2(SOURCE_DB, DEST_DB)
print(f"Nieuwe database gekopieerd naar:\n  {DEST_DB}")
print("Klaar.")

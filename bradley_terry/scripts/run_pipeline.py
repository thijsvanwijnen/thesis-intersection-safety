"""
run_pipeline.py — Voer alle vijf Bradley-Terry notebooks sequentieel uit.

Wat dit script doet:
  NB01 → NB02 → NB03 → NB04 → NB05, elk via `jupyter nbconvert --execute`.
  De notebooks worden in-place bijgewerkt (outputs worden opgeslagen).
  Bij een fout in een notebook stopt het script direct.

Gebruik:
    python scripts/run_pipeline.py
    (uitvoeren vanuit de bradley_terry/ root)
"""

import subprocess
import sys
import time
from pathlib import Path

# Script staat in scripts/, notebooks staan in de bovenliggende map
ROOT_DIR     = Path(__file__).parent.parent
NOTEBOOK_DIR = ROOT_DIR / "notebooks"

NOTEBOOKS = [
    "NB01_export_and_reshape.ipynb",
    "NB02_wins_matrix.ipynb",
    "NB03_bt_model.ipynb",
    "NB04_validate.ipynb",
    "NB05_normalize_export.ipynb",
]

# ---------------------------------------------------------------------------
# Hulpfunctie: voer één notebook uit en geef terug of het gelukt is
# ---------------------------------------------------------------------------
def run_notebook(path: Path) -> bool:
    """Voer notebook uit via nbconvert en sla de outputs op in-place."""
    print(f"\n{'='*60}")
    print(f"  Starten: {path.name}")
    print(f"{'='*60}")

    cmd = [
        sys.executable, "-m", "nbconvert",
        "--to", "notebook",
        "--execute",
        "--inplace",
        # Geen tijdslimiet per cel; grote datasets kunnen lang duren
        "--ExecutePreprocessor.timeout=-1",
        str(path),
    ]

    start = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n  FOUT in {path.name} (exitcode {result.returncode})")
        return False

    print(f"\n  Klaar: {path.name}  ({elapsed:.1f}s)")
    return True


# ---------------------------------------------------------------------------
# Hoofdlus: notebooks één voor één uitvoeren
# ---------------------------------------------------------------------------
total_start = time.time()

for nb_name in NOTEBOOKS:
    nb_path = NOTEBOOK_DIR / nb_name

    if not nb_path.exists():
        print(f"FOUT: notebook niet gevonden: {nb_path}")
        sys.exit(1)

    success = run_notebook(nb_path)

    if not success:
        print(f"\nPipeline gestopt bij {nb_name}.")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------------
total_elapsed = time.time() - total_start
print(f"\n{'='*60}")
print(f"  Pipeline voltooid in {total_elapsed:.1f}s")
print(f"  Output: {ROOT_DIR / 'data' / 'output' / 'bt_scores.csv'}")
print(f"{'='*60}\n")

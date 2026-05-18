"""
run_pipeline.py — Voer alle CV-pipeline notebooks sequentieel uit.

Wat dit script doet:
  NB00 → NB01 → NB02 → NB03 → NB04 → NB05, elk via `jupyter nbconvert --execute`.
  De notebooks worden in-place bijgewerkt (outputs worden opgeslagen).
  Bij een fout in een notebook stopt het script direct.

  NB06 (explainability) wordt overgeslagen; dat is een stretch goal en
  vereist dat NB05 al een volledig score-bestand heeft geproduceerd.

Gebruik:
    python scripts/run_pipeline.py
    (uitvoeren vanuit de cv/ root) 
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

import nbformat

# Windows-fix: ZMQ/tornado vereist de selector event loop, niet de standaard proactor
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Script staat in cv/scripts/, notebooks staan in cv/pipeline/
ROOT_DIR     = Path(__file__).parent.parent
NOTEBOOK_DIR = ROOT_DIR / "pipeline"

NOTEBOOKS = [
    "NB00_augment_training_data.ipynb",
    "NB01_data_audit.ipynb",
    "NB02_baseline_resnet.ipynb",
    "NB03_dinov2.ipynb",
    "NB04_comparison.ipynb",
    "NB05_predict_network.ipynb",
    # NB06_explainability.ipynb is een stretch goal — niet opgenomen in de standaard run
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
        # Geen tijdslimiet per cel; grote datasets en GPU-training kunnen lang duren
        "--ExecutePreprocessor.timeout=-1",
        str(path),
    ]

    # Voeg ontbrekende cel-ID's toe zodat nbformat geen MissingIDFieldWarning gooit
    # nbformat.normalize bestaat pas vanaf v5.1; stil falen bij oudere versies
    nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
    if hasattr(nbformat, "normalize"):
        nbformat.normalize(nb)
    nbformat.write(nb, path)

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
print(f"  Output: {ROOT_DIR / 'outputs' / 'cv_scores_full_network.csv'}")
print(f"{'='*60}\n")

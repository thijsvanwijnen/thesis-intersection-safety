"""
update_data.py — Manual data sync for the nb-model pipeline.

Run this before NB01_data_prep.ipynb to pull the latest files from upstream
pipelines into data/. Data updates between pipeline phases are done
manually by running this script so that reruns are always tied to a known
snapshot of the upstream data.

Usage:
    python update_data.py
"""
import shutil
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # scripts/../ = nb-model/
DATA         = PROJECT_ROOT / "data" / "raw"           # data/raw/ input directory
PARENT       = PROJECT_ROOT.parent                     # Project root (one level up)

# ── Auto-copied sources ────────────────────────────────────────────────────────
# Each entry: (source_path, destination_filename, "required" | "optional")
SOURCES = [
    # CV pipeline output — intersection safety scores from NB05
    (
        PARENT / "cv" / "outputs" / "cv_scores_full_network.csv",
        "cv_scores_full_network.csv",
        "required",
    ),
    # Bradley-Terry scores — useful for context and validation
    (
        PARENT / "bradley_terry" / "data" / "output" / "bt_scores.csv",
        "bt_scores.csv",
        "optional",
    ),
    # Intersection features — will be exported from intersections_stratified.gpkg
    # once the feature-extraction step is built. Uncomment when available.
    # (
    #     PARENT / "intersections" / "data" / "processed" / "intersection_features.csv",
    #     "intersection_features.csv",
    #     "required",
    # ),
]

# ── Manually placed files ──────────────────────────────────────────────────────
# These have no upstream pipeline output yet; place them in data/raw/ by hand.
MANUAL_FILES = [
    (
        "crash_counts.csv",
        "BRON 2019-2024 injury crash counts aggregated per intersection.\n"
        "  Columns: intersection_id, crash_count, exposure\n"
        "  Source: aggregate BRON CSVs from intersections/data/raw/BRON/\n"
        "  Note: exposure unit is TBD (single number per intersection).",
    ),
    (
        "intersection_features.csv",
        "Infrastructure variables per intersection.\n"
        "  Columns: intersection_id, n_legs, speed_limit, dim_type, dim_priority,\n"
        "           intensity_major, intensity_minor\n"
        "  Source: export from intersections/data/processed/intersections_stratified.gpkg\n"
        "  (requires geopandas; see HANDOVER_nb_to_enriched.md for join strategy).",
    ),
]


def copy_source(src: Path, dest_name: str, required: bool) -> bool:
    """Copy one source file to data/. Returns True on success."""
    dest = DATA / dest_name
    if not src.exists():
        tag = "MISSING (required)" if required else "not found (optional, skipping)"
        print(f"  x  {dest_name:<42} {tag}")
        print(f"       Expected: {src}")
        return not required   # only fail on required
    shutil.copy2(src, dest)
    size_kb = src.stat().st_size / 1024
    print(f"  ok {dest_name:<42} copied  ({size_kb:.1f} KB)")
    return True


def check_manual(filename: str, description: str):
    """Report whether a manually-placed file is present in data/."""
    path = DATA / filename
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  ok {filename:<42} present ({size_kb:.1f} KB)")
    else:
        print(f"  x  {filename:<42} NOT FOUND — place manually")
        for line in description.strip().split("\n"):
            print(f"       {line.strip()}")


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    print(f"\n=== update_data.py ===")
    print(f"Destination: {DATA}\n")

    print("--- Pipeline outputs (auto-copied) ---")
    all_ok = True
    for src, dest, req in SOURCES:
        ok = copy_source(src, dest, req == "required")
        if not ok:
            all_ok = False

    print("\n--- Manual files (check presence) ---")
    for filename, desc in MANUAL_FILES:
        check_manual(filename, desc)

    print()
    if all_ok:
        print("Done. Run NB01 -> NB02 -> NB03 -> NB04, or use nb_model.py.")
    else:
        print("Some required files are missing. See messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

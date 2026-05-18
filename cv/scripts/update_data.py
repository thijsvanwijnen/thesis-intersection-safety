"""
update_data.py — Refresh cv/data/raw/ with the latest upstream outputs.

Run this from the cv/ folder whenever the BT scores are updated:
    python scripts/update_data.py

After running, re-execute NB00 → NB01 to regenerate the augmented labels
and split assignment before retraining.
"""

import shutil
from pathlib import Path

CV_ROOT      = Path(__file__).parent.parent   # cv/scripts/ → cv/
PROJECT_ROOT = CV_ROOT.parent


def copy(src: Path, dst: Path) -> None:
    """Copy src to dst, printing status. Skips if src does not exist."""
    if not src.exists():
        print(f"  [SKIP]  {src.relative_to(PROJECT_ROOT)}  (not found)")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  [OK]    {src.relative_to(PROJECT_ROOT)}  →  {dst.relative_to(PROJECT_ROOT)}")


print("Updating cv/data/raw/...\n")

# Latest BT scores from the bradley_terry pipeline
copy(
    src=PROJECT_ROOT / "bradley_terry" / "data" / "output" / "bt_scores.csv",
    dst=CV_ROOT / "data" / "raw" / "bt_scores.csv",
)

# Sampled legs from the intersections pipeline (needed for strat columns + bearings)
copy(
    src=PROJECT_ROOT / "intersections" / "data" / "processed" / "sampled_legs_directional_clean.csv",
    dst=CV_ROOT / "data" / "raw" / "sampled_legs_directional_clean.csv",
)

# Full-city leg selection produced by the full-city reprojection script (NB05 input)
copy(
    src=PROJECT_ROOT / "intersections" / "data" / "processed" / "full_city_leg_selection.csv",
    dst=CV_ROOT / "data" / "raw" / "full_city_leg_selection.csv",
)

print("\nDone. Re-run NB00 → NB01 to regenerate bt_scores_augmented.csv and split_assignment.csv.")

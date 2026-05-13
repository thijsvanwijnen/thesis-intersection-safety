"""
prepare_survey_images_new.py

Converts the raw pairwise_design.csv (produced by the intersections pipeline,
with 16+ columns including intersection IDs) into the 6-column format the
survey database generator expects.

Also copies photos from an optional vault directory for new intersections
that are not yet in assets/images/.

Usage
-----
    python prepare_survey_images_new.py

    # Override the vault path on the command line (overrides VAULT_DIR below):
    python prepare_survey_images_new.py --vault D:\\other\\vault\\path

After running, restart the survey so the database is rebuilt from the
new pairwise_design.csv:
    start_survey.bat  (or: python pixelsurvey-core\\survey_gen.py intersection-safety)

The 6 output columns are:
    task_id, set_id,
    alt1_att1_streetview  (/assets/images/<id>.jpeg),
    alt1_att2_intensiteit,
    alt2_att1_streetview  (/assets/images/<id>.jpeg),
    alt2_att2_intensiteit
"""

import argparse
import os
import shutil

import pandas as pd

# ---------------------------------------------------------------------------
# Paths — all anchored to this script's directory
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

_DESIGN_DIR = os.path.join(_HERE, "recipes", "recipe-intersection-safety", "experiments")

# The raw design CSV (16-column version with intersection_a / intersection_b).
# On first run this is auto-created as a backup from pairwise_design.csv.
# On subsequent runs the script reads from here so pairwise_design.csv can
# safely be overwritten each time.
RAW_DESIGN_CSV = os.path.join(_DESIGN_DIR, "pairwise_design_raw.csv")

# The survey-ready output (6-column). survey.yaml points here.
OUTPUT_CSV = os.path.join(_DESIGN_DIR, "pairwise_design.csv")

# Where Dash serves static images from.
IMAGES_DIR = os.path.join(
    _HERE, "surveys", "survey-intersection-safety", "assets", "images"
)

# ---------------------------------------------------------------------------
# VAULT DIRECTORY — update this line when the folder name changes.
# The vault must contain one subfolder per intersection_id (named by ID),
# each holding exactly one photo (.jpeg / .jpg / .png).
# Set to None to skip vault copying (only use photos already in IMAGES_DIR).
# ---------------------------------------------------------------------------
VAULT_DIR = r"D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_new"

# Required columns in the raw design; script will abort if any are missing.
REQUIRED_COLS = {
    "task_id", "set_id",
    "intersection_a", "intersection_b",
    "alt1_att2_intensiteit", "alt2_att2_intensiteit",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_in_vault(vault_dir: str, intersection_id: int) -> str | None:
    """Return path to the single photo in vault/<id>/, or None if absent."""
    folder = os.path.join(vault_dir, str(intersection_id))
    if not os.path.isdir(folder):
        return None
    photos = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpeg", ".jpg", ".png"))
    ]
    return os.path.join(folder, photos[0]) if photos else None


def resolve_image_url(intersection_id: int, vault_dir: str | None) -> str | None:
    """
    Return the Dash-relative URL for an intersection photo.

    1. If {id}.jpeg/.jpg/.png already exists in IMAGES_DIR → use it directly.
    2. Else if vault_dir is given and the photo is in the vault → copy it, then use it.
    3. Otherwise → return None (photo missing).
    """
    # Check existing files (try jpeg first, then jpg, then png)
    for ext in (".jpeg", ".jpg", ".png"):
        candidate = os.path.join(IMAGES_DIR, f"{intersection_id}{ext}")
        if os.path.exists(candidate):
            return f"/assets/images/{intersection_id}{ext}"

    # Try copying from vault
    if vault_dir:
        src = find_in_vault(vault_dir, intersection_id)
        if src:
            ext = os.path.splitext(src)[1].lower()
            dest = os.path.join(IMAGES_DIR, f"{intersection_id}{ext}")
            shutil.copy2(src, dest)
            print(f"  Copied {intersection_id}{ext} from vault")
            return f"/assets/images/{intersection_id}{ext}"

    return None  # no photo available


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare survey-ready pairwise_design.csv from raw intersection design"
    )
    parser.add_argument(
        "--vault",
        default=VAULT_DIR,  # uses VAULT_DIR constant; override here or via CLI
        metavar="DIR",
        help=(
            "Path to vault directory containing one subfolder per intersection_id, "
            "each holding one photo. Defaults to VAULT_DIR in the script. "
            "Pass an explicit path to override."
        ),
    )
    args = parser.parse_args()

    # Ensure the images folder exists
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load the raw design
    #    On first run: backup pairwise_design.csv → pairwise_design_raw.csv.
    #    On later runs: read from pairwise_design_raw.csv so the source is
    #    never overwritten and the script is safely re-runnable.
    # ------------------------------------------------------------------
    if not os.path.exists(RAW_DESIGN_CSV):
        # First run — create the backup from the current pairwise_design.csv
        if not os.path.exists(OUTPUT_CSV):
            raise FileNotFoundError(
                f"Neither {RAW_DESIGN_CSV} nor {OUTPUT_CSV} found. "
                "Place the raw (16-column) design CSV at one of those paths."
            )
        shutil.copy2(OUTPUT_CSV, RAW_DESIGN_CSV)
        print(f"Created raw backup → {RAW_DESIGN_CSV}")

    raw = pd.read_csv(RAW_DESIGN_CSV)
    print(f"Loaded {RAW_DESIGN_CSV}")
    print(f"  {len(raw)} tasks  |  columns: {list(raw.columns)}")

    # Abort early if the expected columns are missing
    missing_cols = REQUIRED_COLS - set(raw.columns)
    if missing_cols:
        raise ValueError(
            f"Raw design CSV is missing required columns: {missing_cols}\n"
            "Make sure you are running this script on the full-detail CSV "
            "(with intersection_a / intersection_b columns), not on an already-"
            "filtered 6-column version."
        )

    # ------------------------------------------------------------------
    # 2. Resolve image URLs for each intersection
    # ------------------------------------------------------------------
    url_cache: dict[int, str | None] = {}
    missing_ids: list[int] = []

    def get_url(intersection_id: int) -> str | None:
        """Cached lookup so each intersection is processed only once."""
        if intersection_id not in url_cache:
            url = resolve_image_url(intersection_id, args.vault)
            url_cache[intersection_id] = url
            if url is None:
                missing_ids.append(intersection_id)
        return url_cache[intersection_id]

    raw["alt1_att1_streetview"] = raw["intersection_a"].apply(get_url)
    raw["alt2_att1_streetview"] = raw["intersection_b"].apply(get_url)

    # ------------------------------------------------------------------
    # 3. Report
    # ------------------------------------------------------------------
    n_complete = len(
        raw.dropna(subset=["alt1_att1_streetview", "alt2_att1_streetview"])
    )
    n_total = len(raw)
    unique_missing = sorted(set(missing_ids))

    if unique_missing:
        print(
            f"\n  {len(unique_missing)} intersection(s) have no photo "
            f"(tasks with missing photos will show a broken image):\n"
            f"  {unique_missing}"
        )
        if args.vault:
            print(f"  Photos were looked for in: {args.vault}")
        else:
            print("  Tip: set VAULT_DIR in the script to copy photos automatically.")

    print(f"\n  {n_complete}/{n_total} tasks have both photos available")

    # ------------------------------------------------------------------
    # 4. Write the 6-column survey-ready CSV
    # ------------------------------------------------------------------
    survey_cols = [
        "task_id",
        "set_id",
        "alt1_att1_streetview",
        "alt1_att2_intensiteit",
        "alt2_att1_streetview",
        "alt2_att2_intensiteit",
    ]
    raw[survey_cols].to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote survey-ready CSV → {OUTPUT_CSV}")
    print("Next step: rebuild the database by running start_survey.bat")


if __name__ == "__main__":
    main()

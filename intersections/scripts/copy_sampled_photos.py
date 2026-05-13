"""
copy_sampled_photos.py

Copies all directional photos referenced in sampled_legs_directional.csv
from the TU Delft server to the local HDD, preserving the H3 folder structure.

Which files are copied:
  - photo_filepath  — the selected/primary photo for every row
  - stitch_left_filepath  } only for rows where requires_stitch=True
  - stitch_right_filepath }

Run from the intersections/ folder:
    python scripts/copy_sampled_photos.py

Flags:
    --dry-run   Print what would be copied without actually copying.
    --csv PATH  Override the default CSV path.
"""

import argparse
import os
import shutil
import sys

import pandas as pd


# ---------------------------------------------------------------------------
# Roots — change these if the paths ever move
# ---------------------------------------------------------------------------
SERVER_IMAGES_ROOT = r"\\tudelft.net\staff-umbrella\SLIRotterdam\images"
HDD_IMAGES_ROOT    = r"D:\rotterdam_aiis_2025\vault-production\vault_v1\images"

DEFAULT_CSV = os.path.join(
    os.path.dirname(__file__),        # scripts/
    "..", "data", "processed", "sampled_legs_directional_clean.csv"
)


def collect_paths(df: pd.DataFrame) -> list[str]:
    """Return a sorted list of unique relative file paths that need to be copied."""
    paths = set()

    # Primary selected photo — always needed
    paths.update(df["photo_filepath"].dropna())

    # Stitch helper photos — only for rows that require stitching
    stitched = df[df["requires_stitch"] == True]
    paths.update(stitched["stitch_left_filepath"].dropna())
    paths.update(stitched["stitch_right_filepath"].dropna())

    return sorted(paths)


def copy_file(rel_path: str, src_root: str, dst_root: str, dry_run: bool) -> str:
    """
    Copy one file from src_root/rel_path to dst_root/rel_path.
    Creates destination subdirectories if they don't exist.
    Returns: 'copied', 'skipped' (already exists), or 'missing' (source not found).
    """
    # Normalise any forward-slashes that pandas may have read
    rel_path = rel_path.replace("/", os.sep)

    src = os.path.join(src_root, rel_path)
    dst = os.path.join(dst_root, rel_path)

    if not os.path.exists(src):
        return "missing"

    if os.path.exists(dst):
        return "skipped"

    if not dry_run:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    return "copied"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be copied without doing anything.")
    parser.add_argument("--csv", default=DEFAULT_CSV,
                        help="Path to sampled_legs_directional.csv")
    args = parser.parse_args()

    csv_path = os.path.normpath(args.csv)
    if not os.path.exists(csv_path):
        sys.exit(f"CSV not found: {csv_path}")

    # Check that the server root is reachable before starting
    if not os.path.exists(SERVER_IMAGES_ROOT):
        sys.exit(f"Server root not reachable: {SERVER_IMAGES_ROOT}\n"
                 "Connect to the TU Delft VPN / network first.")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    paths = collect_paths(df)
    print(f"Unique photos to process: {len(paths)}")
    if args.dry_run:
        print("--- DRY RUN — nothing will be copied ---\n")

    counts = {"copied": 0, "skipped": 0, "missing": 0}

    for i, rel_path in enumerate(paths, start=1):
        status = copy_file(rel_path, SERVER_IMAGES_ROOT, HDD_IMAGES_ROOT, args.dry_run)
        counts[status] += 1

        # Progress update every 50 files
        if i % 50 == 0 or i == len(paths):
            print(f"  [{i}/{len(paths)}]  copied={counts['copied']}  "
                  f"skipped={counts['skipped']}  missing={counts['missing']}")

        if args.dry_run and status == "missing":
            print(f"    MISSING  {rel_path}")
        elif args.dry_run:
            print(f"    {status.upper():7s}  {rel_path}")

    print(f"\nDone.\n  Copied : {counts['copied']}\n  Skipped: {counts['skipped']} (already on HDD)\n  Missing: {counts['missing']} (not on server)")


if __name__ == "__main__":
    main()

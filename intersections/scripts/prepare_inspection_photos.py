"""
prepare_inspection_photos.py

Copies every reprojected leg photo to a flat 'to_check' folder and stamps
a label box at the top showing the intersection ID and leg bearing.

Source structure (per notebook 07):
    reprojected_directional_fov90_dist20_new/
        {intersection_id}/
            leg_{bearing}.jpeg

Output (flat):
    reprojected_directional_fov90_dist20_new_to_check/
        {intersection_id}_leg_{bearing}.jpeg

The label box makes it easy to note down intersection + leg IDs when
inspecting photos and deciding which ones to remove from the analysis.

Run from anywhere:
    python scripts/prepare_inspection_photos.py

Flags:
    --dry-run   Print file list without writing anything.
    --src PATH  Override source folder.
    --dst PATH  Override destination folder.
"""

import argparse
import os
import sys

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------
VAULT_ROOT = r"D:\rotterdam_aiis_2025\vault-production\vault_v1"
SRC_DIR    = os.path.join(VAULT_ROOT, "reprojected_directional_fov90_dist20_new")
DST_DIR    = os.path.join(VAULT_ROOT, "reprojected_directional_fov90_dist20_new_to_check")

# CSV with photo metadata (used to look up distance to intersection)
CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "data", "processed", "sampled_legs_directional_clean.csv"
)

# Label box appearance
BOX_HEIGHT   = 100  # pixels added at the top of the image (3 text lines)
BOX_COLOR    = (255, 255, 255)   # white background
TEXT_COLOR   = (0, 0, 0)         # black text
FONT_SIZE    = 26
PADDING      = 10   # left/top margin inside the box


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a readable TrueType font; fall back to PIL default."""
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    # PIL built-in bitmap font — always available, but small and fixed-size
    return ImageFont.load_default()


def add_label(img: Image.Image, intersection_id: str, bearing: str,
              dist_m: float | None) -> Image.Image:
    """
    Return a new image with a white label box prepended at the top.
    The box contains three text lines:
        Intersection: {intersection_id}
        Leg bearing:  {bearing}°
        Distance:     {dist_m} m
    """
    w, h = img.size

    # Create a new canvas tall enough for the label + original image
    new_img = Image.new("RGB", (w, h + BOX_HEIGHT), BOX_COLOR)
    new_img.paste(img, (0, BOX_HEIGHT))   # original photo below the box

    draw = ImageDraw.Draw(new_img)
    font = load_font(FONT_SIZE)
    line_step = FONT_SIZE + 4   # vertical spacing between lines

    dist_str = f"{dist_m:.1f} m" if dist_m is not None else "n/a"

    lines = [
        f"Intersection:  {intersection_id}",
        f"Leg bearing:   {bearing}°",
        f"Distance:      {dist_str}",
    ]
    for i, line in enumerate(lines):
        draw.text((PADDING, PADDING + i * line_step), line, font=font, fill=TEXT_COLOR)

    return new_img


def collect_jobs(src_dir: str) -> list[tuple[str, str, str]]:
    """
    Walk src_dir and return a list of (src_path, intersection_id, bearing) tuples.
    Expected structure: src_dir/{intersection_id}/leg_{bearing}.jpeg
    """
    jobs = []
    for intersection_id in sorted(os.listdir(src_dir)):
        sub = os.path.join(src_dir, intersection_id)
        if not os.path.isdir(sub):
            continue
        for fname in os.listdir(sub):
            if not fname.lower().endswith(".jpeg") and not fname.lower().endswith(".jpg"):
                continue
            # Parse bearing from "leg_278.jpeg" → "278"
            stem = os.path.splitext(fname)[0]          # "leg_278"
            bearing = stem.split("_", 1)[-1]            # "278"
            src_path = os.path.join(sub, fname)
            jobs.append((src_path, intersection_id, bearing))
    return jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="List what would be created without writing files.")
    parser.add_argument("--src", default=SRC_DIR, help="Source folder (reprojected photos).")
    parser.add_argument("--dst", default=DST_DIR, help="Destination folder (flat to-check).")
    args = parser.parse_args()

    if not os.path.exists(args.src):
        sys.exit(f"Source folder not found: {args.src}")

    # Build a lookup (intersection_id_str, bearing_str) → photo_dist_m from the CSV.
    # bearing_str uses the same :.0f rounding that notebook 07 uses for filenames.
    csv_path = os.path.normpath(CSV_PATH)
    dist_lookup: dict[tuple[str, str], float] = {}
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            key = (str(int(row["intersection_id"])), f"{row['leg_bearing']:.0f}")
            dist_lookup[key] = float(row["photo_dist_m"])
        print(f"Loaded distance data for {len(dist_lookup)} legs from CSV.")
    else:
        print(f"Warning: CSV not found at {csv_path} — distance will show as n/a.")

    jobs = collect_jobs(args.src)
    print(f"Found {len(jobs)} photos in {args.src}")

    if not jobs:
        sys.exit("Nothing to do.")

    if args.dry_run:
        print("--- DRY RUN — nothing will be written ---\n")
    else:
        os.makedirs(args.dst, exist_ok=True)

    for i, (src_path, intersection_id, bearing) in enumerate(jobs, start=1):
        # Flat output filename: {intersection_id}_leg_{bearing}.jpeg
        out_name = f"{intersection_id}_leg_{bearing}.jpeg"
        out_path = os.path.join(args.dst, out_name)

        if args.dry_run:
            print(f"  {out_name}")
            continue

        if os.path.exists(out_path):
            # Already done — skip (useful for reruns)
            if i % 50 == 0 or i == len(jobs):
                print(f"  [{i}/{len(jobs)}] skipping already-existing files...")
            continue

        # Look up distance from CSV; None if not found
        dist_m = dist_lookup.get((intersection_id, bearing))

        # Open, annotate, save
        img       = Image.open(src_path).convert("RGB")
        annotated = add_label(img, intersection_id, bearing, dist_m)
        annotated.save(out_path, "JPEG", quality=92)

        # Progress line every 50 files
        if i % 50 == 0 or i == len(jobs):
            print(f"  [{i}/{len(jobs)}] written to {args.dst}")

    if not args.dry_run:
        print(f"\nDone. {len(jobs)} photos saved to:\n  {args.dst}")


if __name__ == "__main__":
    main()

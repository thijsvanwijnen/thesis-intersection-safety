import pandas as pd
import shutil
import os

# --- Config ---
# Paths are anchored to this script's directory so it works from any working directory.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Source: the merged survey design from the intersections pipeline.
SURVEY_DESIGN_CSV = os.path.join(
    _HERE, "..", "intersections", "data", "processed", "survey_design.csv"
)

# Source: vault folder containing one subfolder per intersection, each with one photo.
VAULT_DIR = r"D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional"

# Destination: where Dash serves static images from.
IMAGES_DIR = os.path.join(
    _HERE, "surveys", "survey-intersection-safety", "assets", "images"
)

# Destination: the pairwise design CSV that the survey reads at startup.
OUTPUT_CSV = os.path.join(
    _HERE, "recipes", "recipe-intersection-safety", "experiments", "pairwise_design.csv"
)


def find_photo(intersection_id: int) -> str | None:
    """
    Return the path to the single photo in the vault folder for this intersection.
    Returns None if the folder or photo does not exist yet (vault still being built).
    """
    folder = os.path.join(VAULT_DIR, str(intersection_id))
    if not os.path.isdir(folder):
        return None

    # Each folder contains exactly one photo — pick the first image file found.
    photos = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpeg", ".jpg", ".png"))
    ]
    return os.path.join(folder, photos[0]) if photos else None


def copy_photo(src_path: str, intersection_id: int) -> str:
    """
    Copy the photo to assets/images/ using the intersection ID as the filename.
    Returns the Dash-relative URL path (/assets/images/<name>).
    """
    ext = os.path.splitext(src_path)[1].lower()
    dest_name = f"{intersection_id}{ext}"
    dest_path = os.path.join(IMAGES_DIR, dest_name)

    # Only copy if the file isn't already there (speeds up re-runs).
    if not os.path.exists(dest_path):
        shutil.copy2(src_path, dest_path)
        print(f"  Copied {intersection_id}{ext}")
    else:
        print(f"  Skipped {intersection_id}{ext} (already present)")

    return f"/assets/images/{dest_name}"


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)

    design = pd.read_csv(SURVEY_DESIGN_CSV)
    print(f"Loaded survey_design.csv — {len(design)} tasks, "
          f"{design['intersection_a'].nunique() + design['intersection_b'].nunique()} intersection references")

    # Build a cache so each intersection is processed only once.
    url_cache: dict[int, str] = {}
    missing: list[int] = []

    def get_url(intersection_id: int) -> str | None:
        if intersection_id not in url_cache:
            src = find_photo(intersection_id)
            if src is None:
                missing.append(intersection_id)
                url_cache[intersection_id] = None
            else:
                url_cache[intersection_id] = copy_photo(src, intersection_id)
        return url_cache[intersection_id]

    # Replace the old H3 image paths with vault URLs where available.
    design["alt1_att1_streetview"] = design["intersection_a"].apply(get_url)
    design["alt2_att1_streetview"] = design["intersection_b"].apply(get_url)

    matched = len(design.dropna(subset=["alt1_att1_streetview", "alt2_att1_streetview"]))
    print(f"\n{matched}/{len(design)} tasks have both vault photos available "
          f"({len(set(missing))} intersections missing from vault)")

    # If nothing matched at all, fall back to the test photos already in assets/images/.
    # This lets you verify the survey renders correctly before the full vault is ready.
    if matched == 0:
        fallback = sorted(
            f for f in os.listdir(IMAGES_DIR)
            if f.lower().endswith((".jpeg", ".jpg", ".png"))
        )
        if not fallback:
            raise FileNotFoundError(
                f"No vault photos found AND no fallback images in {IMAGES_DIR}. "
                "Add at least one image to assets/images/ to use fallback mode."
            )
        print(f"\n⚠️  FALLBACK MODE: no vault photos matched.")
        print(f"   Cycling {len(fallback)} existing image(s) from assets/images/ across all tasks.")
        print("   This is for visual testing only — photos do not correspond to the correct intersections.\n")
        fallback_urls = [f"/assets/images/{f}" for f in fallback]
        design["alt1_att1_streetview"] = [fallback_urls[i % len(fallback_urls)] for i in range(len(design))]
        design["alt2_att1_streetview"] = [fallback_urls[(i + 1) % len(fallback_urls)] for i in range(len(design))]

    # Write only the columns the survey needs.
    survey_cols = [
        "task_id",
        "set_id",
        "alt1_att1_streetview",
        "alt1_att2_intensiteit",
        "alt2_att1_streetview",
        "alt2_att2_intensiteit",
    ]
    design[survey_cols].to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone — wrote {len(design)} tasks to {OUTPUT_CSV}")
    print(f"Images in: {IMAGES_DIR}")


if __name__ == "__main__":
    main()

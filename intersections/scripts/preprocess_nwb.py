"""
preprocess_nwb.py
-----------------
One-time preprocessing step: filter the national NWB Wegvakken file down to
Rotterdam and write the result to data/processed/.

Run once (or re-run whenever you receive a new NWB release):
    python scripts/preprocess_nwb.py

Output files
------------
data/processed/wegvakken_rotterdam.gpkg       — all Rotterdam segments, no BST filter
data/processed/wegvakken_rotterdam_bst.gpkg   — Rotterdam segments, BST_CODE filtered
                                                (matches the working dataset used in notebooks)
"""

import os
import time
import geopandas as gpd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Resolve project root relative to this script's location, so the script can
# be run from any working directory.
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEGVAKKEN_PATH   = os.path.join(PROJECT_DIR, "data", "raw",       "Wegvakken.gpkg")
OUT_ALL_PATH     = os.path.join(PROJECT_DIR, "data", "processed", "wegvakken_rotterdam.gpkg")
OUT_BST_PATH     = os.path.join(PROJECT_DIR, "data", "processed", "wegvakken_rotterdam_bst.gpkg")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Municipality name used in NWB GME_NAAM column.
GEMEENTE = "Rotterdam"

# BST_CODE values included in the analysis pipeline.
# Only "normal" road types — excludes slip roads (AFR/OPR), side carriageways (NRB), etc.
INCLUDE_BST = {"RB", "ERF", "HR"}

# Road manager filter: only keep roads managed by the gemeente (municipality).
# WEGBEHSRT='R' = Rijk (national), 'P' = Provincie, 'G' = Gemeente, 'W' = Waterschap.
# Filtering on 'G' removes highways and provincial roads, which would otherwise
# inflate junction counts at motorway on/off-ramps.
WEGBEHSRT_GEMEENTE = "G"

# ---------------------------------------------------------------------------
# Load national file
# ---------------------------------------------------------------------------

print(f"Loading {WEGVAKKEN_PATH} ...")
print("  (this is the large national file — takes ~30–60 s depending on your machine)")
t0 = time.time()
wegvakken_nl = gpd.read_file(WEGVAKKEN_PATH)
print(f"  Loaded {len(wegvakken_nl):,} segments nationally ({time.time() - t0:.0f}s)")

# ---------------------------------------------------------------------------
# Filter to Rotterdam
# ---------------------------------------------------------------------------

# Keep only segments within the municipality of Rotterdam.
# GME_NAAM is the municipality name field in NWB.
wegvakken_rot = wegvakken_nl[wegvakken_nl["GME_NAAM"] == GEMEENTE].copy()
print(f"  Rotterdam segments: {len(wegvakken_rot):,}")

# Drop the national file from memory — we no longer need it.
del wegvakken_nl

# ---------------------------------------------------------------------------
# Apply gemeente + BST_CODE filter
# ---------------------------------------------------------------------------

# First filter to gemeente-managed roads only (WEGBEHSRT='G').
# This removes Rijk highways and provincial roads before the BST filter,
# preventing motorway junction nodes from appearing as intersections.
wegvakken_bst = wegvakken_rot[wegvakken_rot["WEGBEHSRT"] == WEGBEHSRT_GEMEENTE].copy()
print(f"  Rotterdam gemeente-managed segments: {len(wegvakken_bst):,}")

# Then filter on BST_CODE — keep only "normal" road types.
wegvakken_bst = wegvakken_bst[wegvakken_bst["BST_CODE"].isin(INCLUDE_BST)].copy()
print(f"  Rotterdam BST-filtered segments: {len(wegvakken_bst):,}")

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------

print(f"\nWriting {OUT_ALL_PATH} ...")
wegvakken_rot.to_file(OUT_ALL_PATH, driver="GPKG")
print(f"  Done ({len(wegvakken_rot):,} features)")

print(f"Writing {OUT_BST_PATH} ...")
wegvakken_bst.to_file(OUT_BST_PATH, driver="GPKG")
print(f"  Done ({len(wegvakken_bst):,} features)")

print("\nPreprocessing complete.")
print(f"  wegvakken_rotterdam.gpkg     → all BST codes, use for full exploration")
print(f"  wegvakken_rotterdam_bst.gpkg → {INCLUDE_BST}")
print("  Load in notebooks with gpd.read_file(...) — no national file needed.")

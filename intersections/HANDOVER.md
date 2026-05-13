# Intersections Pipeline — Handover for Downstream Projects

This file documents what the `intersections/` pipeline produced and how to use it.
Intended as context for Claude sessions in other project forks (e.g. `cv/`).

---

## What this project does

Selects one street-level photo per approach leg of Rotterdam intersections,
stratifies intersections into 6 groups, samples ~150 for a Bradley-Terry
paired-comparison survey on perceived road safety.

**Pipeline:** NB00→NB01→NB02→NB04→NB05→NB05b→NB05c→NB06→NB07
(NB03 independent branch, adds strata)

---

## Key paths

| What | Path |
|---|---|
| Project root | `C:\Users\Thijs\OneDrive\Documents\Studie\EPA\Second_year\Afstuderen\Project\intersections` |
| Processed data | `…\intersections\data\processed\` |
| Reprojected photos | `D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_new\` |
| Raw directional photos (HDD) | `D:\rotterdam_aiis_2025\vault-production\vault_v1\images\` |
| Raw directional photos (server) | `\\tudelft.net\staff-umbrella\SLIRotterdam\images\` |
| Photo index | `D:\…\vault_v1\image_index.csv` or `data\raw\image_index.csv` (local copy) |

---

## Final sample: `sampled_legs_directional_clean.csv`

**308 rows — one row per sampled intersection leg.**
This is the authoritative list of photos used in the survey.

Key columns:

| Column | Description |
|---|---|
| `intersection_id` | NWB junction ID (JTE_ID), e.g. `176268014` |
| `leg_bearing` | Bearing of the approach leg in degrees (0–360) |
| `photo_filename` | image_id, e.g. `364_02668` |
| `photo_dist_m` | Distance from photo location to intersection centroid (metres) |
| `selected_direction` | Which camera was chosen: `front` (295×), `right` (6×), `left` (5×), `back` (2×) |
| `photo_filepath` | Relative path to the selected photo, e.g. `88196ba2.../364_02668_front.jpg` |
| `filepath_front/right/back/left` | Relative paths to all 4 directions for this image_id |
| `requires_stitch` | True (276×) if the leg falls between two camera directions → image was stitched |
| `stitch_left_filepath` | Left source image for stitched photos |
| `stitch_right_filepath` | Right source image for stitched photos |
| `stitch_inter_col_frac` | Fractional column where intersection falls in the stitched image |
| `dim_type` | Stratum: `T` (3-arm) or `4+` (4+-arm) |
| `dim_priority` | Stratum: `VRI` / `voorrang` / `geen_voorrang` |
| `dim_risk` | Risk level: `laag` / `midden` / `hoog` / `_` (unknown) |
| `dim_speed` | Speed limit: `30` / `50+` / `_` (unknown) |
| `is_centrum` | Boolean — within Rotterdam city centre polygon |
| `WVK_ID` | NWB road segment ID of the approach leg |
| `intensity_wvk` | Traffic intensity on the approach leg (vehicle/day) |
| `direction_patched` | True if NB05b swapped a back-direction leg |
| `quality_patched` | True if NB05c swapped a manually rejected photo |

**To resolve photo paths:**
```python
HDD_ROOT    = r"D:\rotterdam_aiis_2025\vault-production\vault_v1\images"
SERVER_ROOT = r"\\tudelft.net\staff-umbrella\SLIRotterdam\images"
ROOT = HDD_ROOT if os.path.exists(HDD_ROOT) else SERVER_ROOT
full_path = os.path.join(ROOT, row["photo_filepath"].replace("/", os.sep))
```

---

## Reprojected photos

NB07 converted the selected photos to standard-format crops (FOV=90°, ~20m from intersection).

**Location:** `D:\…\reprojected_directional_fov90_dist20_new\{intersection_id}\leg_{bearing:.0f}.jpeg`

Example: intersection `176268014`, leg bearing `290.5°` → `…\176268014\leg_291.jpeg`

- Format: JPEG, quality=90
- ~308 files across ~308 subdirectories (one per intersection)
- Filename convention: bearing rounded to nearest integer with `:.0f`

**To look up the reprojected path for a row in `sampled_legs_directional_clean.csv`:**
```python
REPRO_ROOT = r"D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_new"
path = os.path.join(REPRO_ROOT, str(row["intersection_id"]), f"leg_{row['leg_bearing']:.0f}.jpeg")
```

---

## Survey design: `survey_design_v2.csv`

**504 rows — one row per comparison pair.**
145 unique intersections appear across the pairs.

Key columns:

| Column | Description |
|---|---|
| `task_id` | Sequential pair number |
| `set_id` | Rater set this pair belongs to |
| `pair_id` | Unique hash ID for the pair |
| `is_anchor` | True (98×) — anchor pairs shown to all raters for inter-rater reliability |
| `pair_type` | `backbone` (134) / `hub_spoke` (264) / `diagonal` (12) / `within` (94) |
| `is_cross_stratum` | True if the two intersections are from different strata |
| `intersection_a` / `intersection_b` | intersection_id of each item in the pair |
| `alt1_att1_streetview` | Relative photo path for intersection_a |
| `alt2_att1_streetview` | Relative photo path for intersection_b |
| `alt1_att2_intensiteit` / `alt2_att2_intensiteit` | Traffic intensity label: `Laag` / `Middelmatig` / `Hoog` |
| `intensity_wvk_a` / `intensity_wvk_b` | Raw traffic intensity (vehicle/day) |
| `stratum_a` / `stratum_b` | Stratum label, e.g. `4+_VRI`, `T_geen_voorrang` |

---

## Strata breakdown

6 strata (dim_type × dim_priority), sampled with equal strategy (N_PER_STRATUM=70):

| Stratum | N intersections |
|---|---|
| 4+\_VRI | 68 |
| 4+\_geen\_voorrang | 65 |
| 4+\_voorrang | 67 |
| T\_VRI | 12 *(small population)* |
| T\_geen\_voorrang | 61 |
| T\_voorrang | 35 |
| **Total** | **308** |

Stratum label format: `{dim_type}_{dim_priority}`, e.g. `4+_VRI`, `T_voorrang`.

---

## Rater schedules: `data/processed/rater_schedules_v2/`

One CSV per rater (14 raters total). Each rater gets 40 pairs including 7 anchor pairs.
Files are named by rater ID.

---

## Intersections spatial file: `intersections_stratified.gpkg`

4,858 total Rotterdam intersections with strata labels. CRS: **EPSG:28992 (RD New)**.

Key columns: `JTE_ID` (= `intersection_id` in CSVs), `geometry` (Point), `street_count`,
`max_dist_m`, `ideal_dist_m`, `dim_type`, `dim_risk`, `dim_priority`, `dim_speed`, `is_centrum`.

Join to CSVs on: `intersections_stratified.JTE_ID == sampled_legs.intersection_id`

---

## Technical constants

| Parameter | Value |
|---|---|
| CRS | EPSG:28992 (RD New, metres) |
| Image mode | directional (4 shots per location: front/back/left/right) |
| Reprojection FOV | 90° horizontal |
| Target photo distance | ~20m from intersection |
| Merge threshold (dual carriageways) | 25m |
| Bayonet threshold | 6m |
| Minimum photo distance filter (NB05) | 15m |

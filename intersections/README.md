# Rotterdam Intersection Photo Analysis — Intersections Fork

## Project overview
This fork selects and processes panoramic street-level photos of road intersections
in Rotterdam for use in a safety study based on pairwise expert comparisons.

Photos are taken from a vehicle-mounted 360° camera system and stored on an external
HDD (~706k images). The goal is to produce geometrically consistent flat images —
one per approach leg per intersection — along with a structured pairwise comparison
schedule for Bradley-Terry score estimation.

The road network is derived from **NWB** (Nationaal Wegenbestand), not OpenStreetMap.

---

## Notebook pipeline

The main pipeline runs in numbered order. Each notebook reads from `data/processed/`
and writes its outputs there. See `data_description.md` for full file descriptions.

```
00 → 01 → 02 → 04 → 05 → 06 → 07
               ↓
               03  (stratification — can run after 01)
```

### Main pipeline

| Notebook | Purpose | Key output |
|---|---|---|
| `00_prepare_data_nwb.ipynb` | Extract junction points from NWB; filter to Rotterdam ring area | `intersections.gpkg` |
| `01_merge_junctions.ipynb` | Merge duplicate junctions from dual carriageways (~25m) and bayonet artefacts (~7m) | `intersections_merged.gpkg`, `wegvakken_rotterdam_bst_merged.gpkg` |
| `02_image_extraction.ipynb` | Filter 706k panoramas to those within 5–55m of an intersection | `selected_photos_near_intersections.csv` |
| `03_stratified_sampling.ipynb` | Assign stratum labels to intersections (type × speed × priority) | `intersections_stratified.gpkg` |
| `04_leg_photo_selection.ipynb` | Select the best approach photo per intersection leg by bearing | `leg_photo_selection.csv` |
| `05_sampling.ipynb` | Draw a stratified sample of intersection legs for expert elicitation | `sampled_legs.csv` |
| `06_bt_pairs.ipynb` | Generate within-stratum and bridging pairs for Bradley-Terry estimation | pair schedule CSV |
| `07_reprojection.ipynb` | Reproject selected panoramas to flat perspective images (1500×880px) | per-leg JPEG files |

### Variant notebooks

| Notebook | Purpose |
|---|---|
| `02b_image_extraction_shp.ipynb` | Shapefile-based variant of notebook 02 |
| `04b_leg_photo_selection_shp.ipynb` | Shapefile-based variant of notebook 04 |

### EDA and exploration notebooks

| Notebook | Purpose |
|---|---|
| `eda_BRON.ipynb` | Validate BRON crash data (encoding, year structure, JTE_ID join) |
| `eda_snelheden.ipynb` | Validate Snelheden_WKD speed data; work out join strategy to intersections |
| `eda_vri.ipynb` | Validate VRI (traffic light) location data |
| `eda_OSM_voorrangswegen.ipynb` | OSM priority road classification for intersection stratification |
| `eda_pipeline_funnel.ipynb` | Track record counts through each pipeline step |
| `eda_shapefile_sander.ipynb` | Explore shapefile from external collaborator |
| `exp_eda_nwb*.ipynb` | NWB dataset exploration (carriageways, bayonets, junctions, distributions) |
| `exp_eda_intersection_size.ipynb` | Evaluate intersection size and leg count distributions |
| `exp_image_cropping_comparison.ipynb` | Compare simple crop vs perspective reprojection |
| `util_image_sampling.ipynb` | Copy sample images from external HDD for local testing |
| `util_photo_export_list.ipynb` | Generate export lists for reprojected photos |

---

## Data

- **Source photos:** 706,743 equirectangular panoramas (360°, 12288×6144px, ~10MB each)
  stored on external HDD at `D:\rotterdam_aiis_2025\vault-production\vault_v1\`
- **Photo index:** `data/raw/Recording.csv` — tab-delimited (`sep="\t"`), RD New coordinates (EPSG:28992)
- **Road network:** `data/raw/Wegvakken.gpkg` — full national NWB file, filtered to Rotterdam in notebook 00
- **Area of interest:** `data/raw/rotterdam_ring.geojson` — custom Rotterdam ring polygon
- **Crash data:** `data/raw/BRON/{year}/Ongevallengegevens/` — BRON records 2020–2024 (`encoding="latin-1"`, semicolon-delimited)
- **Speed limits:** `data/raw/snelheden_WKD/Snelheden.shp` — national speed limits per road segment
- **Traffic lights:** `data/raw/vri_locaties.gpkg` — VRI point locations for Rotterdam

See `data_description.md` for a full description of every raw and processed file.

---

## Folder structure

```
intersections/
├── CLAUDE.md                        Claude Code instructions for this fork
├── README.md                        This file
├── data_description.md              Full description of all raw and processed files
├── methodology_notes.md             Design decisions and parameter justifications
├── notebooks/                       All notebooks (run main pipeline in order)
├── data/
│   ├── raw/                         Original input data — never modified
│   │   ├── Recording.csv
│   │   ├── Wegvakken.gpkg
│   │   ├── rotterdam_ring.geojson
│   │   ├── vri_locaties.gpkg
│   │   ├── BRON/                    Crash records per year
│   │   └── snelheden_WKD/
│   └── processed/                   Outputs produced by the notebooks
├── figures/                         Maps and plots for reporting
├── output/                          Final deliverables
├── scripts/                         Standalone helper scripts
└── old_scripts/                     Archived scripts, no longer in use
```

---

## Dependencies

```bash
conda activate afstuderen
conda install -c conda-forge geopandas shapely pandas matplotlib networkx
pip install py360convert
```

---

## Key parameters

| Parameter | Value | Set in |
|---|---|---|
| Buffer distance (photo selection) | 5–55m from intersection centroid | notebook 02 |
| Intersection definition | `street_count ≥ 3` | notebook 00 |
| BST filter | `BST_CODE` ∈ {RB, ERF, HR}, `WEGBEHSRT = G` | notebook 00 |
| Dual carriageway merge threshold | 25m | notebook 01 |
| Bayonet merge threshold | 7m | notebook 01 |
| Approach bearing tolerance | ±45° | notebook 04 |
| Ideal approach distance | 30m | notebook 04 |
| Output image size | 1500×880px | notebook 07 |
| Field of view | 90° | notebook 07 |
| Vertical tilt | +5° | notebook 07 |
| Bottom crop (car hood removal) | 12% | notebook 07 |
| Coordinate system | RD New (EPSG:28992) | throughout |

# Data description

Quick overview of all files in `data/raw/` and `data/processed/`.

---

## data/raw/

| File / folder | Description |
|---|---|
| `Recording.csv` | Tab-delimited (`sep="\t"`) index of ~706k panoramic photos stored on external HDD (`D:\rotterdam_aiis_2025\...`). Columns include photo ID, filename, and coordinates in RD New (EPSG:28992). Source: AIIS 2025 dataset. |
| `Wegvakken.gpkg` | Full national NWB road segments (LineString). Each row is a wegvak with `JTE_ID_BEG` / `JTE_ID_END` linking it to junction nodes. Needs filtering to Rotterdam before use — very large. |
| `rotterdam_ring.geojson` | Custom polygon defining the Rotterdam ring area of interest. Used in notebook 00 to spatially filter NWB junctions. |
| `vri_locaties.gpkg` | VRI (verkeerslicht / traffic light) point locations for Rotterdam. 308 records; 292 are type `VRI` (full traffic light installations). Used in notebook 03. |
| `BRON/<year>/Ongevallengegevens/ongevallen.txt` | BRON crash records per year (2020–2024). CSV format with `encoding="latin-1"`, semicolon-delimited. Contains `JTE_ID` column for junction-located crashes. Used in notebook 03. |
| `snelheden_WKD/Snelheden.shp` | National speed limits per road segment (~1.6M rows). Links to NWB via `WVK_ID`. Used in notebook 03 as fallback when the Rotterdam cache is absent. |

---

## data/processed/

Files are listed in pipeline order.

### Main pipeline outputs

| File | Created by | Description |
|---|---|---|
| `intersections.gpkg` | notebook 00 | Raw NWB junction points for Rotterdam ring area, street_count ≥ 3. 5,846 rows. Before deduplication. |
| `intersections_merged.gpkg` | notebook 01 | **Main intersections file.** Deduplicated junctions after merging dual carriageway splits (25m threshold) and bayonet artefacts (7m threshold). 4,858 rows. Used as input by notebooks 03 and 04. |
| `wegvakken_rotterdam_bst_merged.gpkg` | notebook 01 | BST-filtered Rotterdam road segments (`BST_CODE` in {RB, ERF, HR}, `WEGBEHSRT=G`) with merge metadata. Used by notebooks 03 (speed join) and 04 (leg bearing). |
| `rotterdam_boundary.gpkg` | notebook 02 | Bounding polygon of the Rotterdam study area. Side effect of the photo filtering step. |
| `selected_photos_near_intersections.csv` | notebook 02 | ~176k panoramic photos within 5–55m of an intersection centroid. Columns: photo ID, coordinates, distance, intersection ID. |
| `snelheden_rotterdam.csv` | notebook 03 (first run) | Rotterdam-only rows from `Snelheden.shp`, no geometry. Cache to avoid re-loading the national shapefile on every run. |
| `intersections_stratified.gpkg` | notebook 03 | `intersections_merged.gpkg` enriched with stratum columns: `dim_type`, `dim_speed`, `dim_priority`, `dominant_speed`, `stratum`. (Also `dim_risk`, `crash_count` when `USE_RISK_LEVEL=True`.) |
| `osm_edges_rotterdam.gpkg` | eda/eda_OSM_voorrangswegen.ipynb | OSM road edges for Rotterdam in RD New. Downloaded once via osmnx and cached. Used by notebook 03 to classify intersections as voorrangsweg. |
| `leg_photo_selection.csv` | notebook 04 | Best approach photo per intersection leg, selected by bearing alignment. One row per leg with columns: intersection ID, bearing, photo path, `u_deg` offset. |
| `sampled_legs.csv` | notebook 05 | Stratified sample of intersection legs for expert elicitation. Subset of `leg_photo_selection.csv` joined to strata from `intersections_stratified.gpkg`. |

### Intermediate / superseded files

These files are kept for reference but are not consumed by the main pipeline.

| File | Status | Notes |
|---|---|---|
| `wegvakken_rotterdam.gpkg` | Intermediate | Rotterdam road segments before BST filter and before junction merging. |
| `wegvakken_rotterdam_bst.gpkg` | Intermediate | Rotterdam road segments after BST filter, before junction merging. |
| `wegvakken_rotterdam.csv` | Superseded | Early tabular cache of Rotterdam wegvakken attributes. Replaced by `wegvakken_rotterdam_bst_merged.gpkg`. No longer used. |
| `exported_photos.csv` | Utility output | List of photos exported/reprojected by `util_export_photos.ipynb`. Not part of the main pipeline. |

# Project Instructions — Intersections Fork

## Code style
- Always add comments to code, explaining what each step does and why.

## Approach
- For visualisation code: keep it simple and direct. Skip edge cases unless explicitly asked.
- Don't deliberate over completeness of visual categories — if a colour/group won't appear in practice, just define it and move on.
- "Good enough" is enough for display code. Don't over-engineer it.

## Project context
- This fork processes NWB road network data and panoramic street photos of Rotterdam intersections.
- Pipeline: 00_prepare_data_nwb → 01_merge_junctions → 02_image_extraction → 04_leg_photo_selection → 05_reprojection (03_stratified_sampling is a branch off 01).
- Main intersection file: `data/processed/intersections_merged.gpkg` (4,858 deduplicated junctions).
- All raw/processed data files are documented in `data_description.md`.
- Coordinate system throughout: RD New (EPSG:28992).
- External HDD with 706k panoramas is at `D:\rotterdam_aiis_2025\vault-production\vault_v1\`.

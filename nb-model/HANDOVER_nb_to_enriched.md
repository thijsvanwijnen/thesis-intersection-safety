# HANDOVER: NB Model Pipeline — Phases 3 & 4

Documents what this pipeline phase produces and what re-estimation needs.

## Notebook pipeline

| Notebook | Job | Key output |
|----------|-----|------------|
| NB01_data_prep.ipynb | Load, join, validate, encode | `outputs/nb_model_ready.csv` |
| NB02_eda.ipynb | Explore distributions, check overdispersion | EDA plots |
| NB03_baseline_model.ipynb | Poisson -> NB, variable selection | `outputs/model_baseline.pkl` |
| NB04_enriched_model.ipynb | Add CV score, LR test, comparison | `outputs/model_enriched.pkl` |

Run with: `python nb_model.py` (uses nbconvert) or open notebooks manually.
Update data first: `python update_data.py`

## Outputs produced

| File | Produced by | Description |
|------|-------------|-------------|
| `outputs/nb_model_ready.csv` | NB01 | Joined, validated, encoded dataset |
| `outputs/model_baseline.pkl` | NB03 | Fitted baseline NB model object |
| `outputs/baseline_results.json` | NB03 | Baseline coefficients, IRRs, CIs, AIC |
| `outputs/model_enriched.pkl` | NB04 | Fitted enriched NB model object |
| `outputs/nb_model_results.json` | NB04 | Full results: both models, LR test, AIC |
| `outputs/nb_comparison_table.csv` | NB04 | Side-by-side coefficient table (thesis-ready) |
| `outputs/diagnostic_plots/` | NB02–NB04 | EDA plots + residual diagnostics |

## Test-set boundary

Intersections with `cv_split == "train"` or `cv_split == "val"` are excluded from both
Phase 3 and Phase 4 modelling datasets. This prevents circularity in Phase 4 (the CV model
trained on these intersections, so their crash outcomes may have indirectly shaped the scores).

Current split counts (preliminary CV model, N=50 total):
- train: 23, val: 1 → excluded from modelling
- unlabelled: 22, excluded: 4 → modelling dataset

## When to re-estimate (Phase 4 update)

1. Full survey BT scores are complete (~145 intersections)
2. Rerun CV pipeline NB01–NB05 to retrain on full BT scores
3. Run `python update_data.py` to pull updated `cv_scores_full_network.csv`
4. Rerun `python nb_model.py` (or NB03_nb_model.ipynb)
5. Check that `nb_model_results.json > phase4_enriched > caveat` no longer says "PRELIMINARY"

Expected changes after full survey:
- Larger modelling dataset (more unlabelled intersections)
- Possibly different selected_vars from variable selection step
- More reliable beta_z estimate (less attenuation from measurement error)

## Exposure units — UNRESOLVED

The `exposure` column in `crash_counts.csv` is a single number per intersection.
Units are TBD; likely total vehicle passages over the study period 2019–2024.
The unit must be documented when BRON aggregation is implemented.
The offset is `log(exposure)` so the model predicts crash *rates* not raw counts.

## CV score caveats (Phase 4)

From `cv/outputs/model_selection.json`:
- Backbone: ResNet-50
- N_train: 63 (pilot survey only)
- Spearman rho: 0.391
- MAE: 0.189 (score range 0–1, so this is substantial measurement error)

Measurement error in z_i attenuates beta_z toward zero (errors-in-variables bias).
A sensitivity analysis using simulation-based error propagation is planned but not yet
implemented — see Section 8 of NB03_nb_model.ipynb for the placeholder.

## Intersection features — source

`intersection_features.csv` must be extracted from the intersections pipeline:
- Source: `intersections/data/processed/intersections_stratified.gpkg`
- Columns available: JTE_ID (= intersection_id), dim_type, dim_priority, street_count (= n_legs)
- Speed limit: join via Snelheden (WVK_ID -> JTE_ID_BEG/JTE_ID_END from Wegvakken)
- Traffic intensity: not yet in pipeline — requires additional data source (NDW/RWS)

## Crash counts — source

`crash_counts.csv` must be aggregated from BRON files:
- Source: `intersections/data/raw/BRON/{year}/Ongevallenbestand_*.csv` (encoding=latin-1)
- Spatial join to `intersections_bst_merged.gpkg` (match crashes to nearest intersection)
- Filter: injury crashes (AOL_OMS contains "letsel" or OMSCH_TA != "uitsluitend materiele schade")
- Period: 2019–2024 (6 years)
- Exposure: TBD — likely AADT * n_years or total vehicle passages; define before modelling

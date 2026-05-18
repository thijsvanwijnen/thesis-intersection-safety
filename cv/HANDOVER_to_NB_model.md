# Handover: CV Pipeline → Negative Binomial Crash Model

This document describes what the CV pipeline produces, how to read those outputs,
and what caveats apply when using them in the NB model (Phase 3).

> **Current status**: The pipeline is structurally complete but running on pilot/test
> survey data. All numbers and scores are preliminary. Once real survey responses are
> collected and BT scores are recomputed, the pipeline is re-run in order
> (NB01 → NB02 → NB03 → NB04 → NB05) and this handover remains valid — only the
> numbers change.

---

## Primary output: one score per intersection

**File:** `cv/outputs/cv_scores_full_network.csv`

| Column | Type | Description |
|--------|------|-------------|
| `intersection_id` | int | NWB junction identifier (join key for all other phases) |
| `cv_score_predicted` | float [0, 1] | Model-predicted visual safety score |
| `cv_split` | str | `train`, `val`, `unlabelled`, or `excluded` — see below |

**Use `cv_score_predicted` as the single scalar predictor in the NB model.**
Higher values = model predicts intersection looks safer.

### cv_split values and what they mean for the NB model

| Value | Meaning | NB model treatment |
|-------|---------|-------------------|
| `train` | Used to train the CV regression head | Exclude from NB test set |
| `val` | Used to validate the CV model | Exclude from NB test set |
| `unlabelled` | Had a photo but no BT label; scored by inference only | Can be used freely in NB model |
| `excluded` | Augmented copies used during CV training only | Drop these rows entirely |

The `train` and `val` intersections have a double role: their photos trained the CV
model, and their true BT scores exist. Using them in the NB test set would be
optimistic (the CV score is not truly out-of-sample for them). Drop or flag them.

---

## Coverage: intersections without a score

Not all Rotterdam intersections have a `cv_score_predicted`. Two reasons:

1. **No reprojected photo available** — logged in `cv/outputs/missing_photos.csv`.
   These intersections are present in the network but their source panoramas were
   missing at photo extraction time. They have no CV score and cannot be scored
   without new photos.

2. **Not in the selected intersection set** — the CV pipeline only covers the
   ~4,615 intersections selected in the intersections phase. Others are out of scope.

In the NB model, treat missing CV scores as missing data (not zero). Options:
- Drop intersections without a CV score from the NB analysis (simplest).
- Impute with the training-set mean score (note this in limitations).
- Include a binary `has_cv_score` indicator alongside the imputed value.

---

## Model quality — what to expect

The CV model predicts a safety score from a single street-level photo. Its precision
is limited by the number of labelled intersections (currently pilot data only).

Key numbers to carry forward from `cv/outputs/model_selection.json`:

- **Selected backbone**: noted in `model_selection.json` → `selected_backbone`
- **Validation MAE**: the expected average absolute error on held-out intersections
- **Spearman ρ**: rank correlation between predicted and true scores — more relevant
  than R² because BT scores have ordinal structure

**Important for the NB model**: the CV score carries measurement error equal to
the validation MAE. This attenuates the estimated β coefficient for `cv_score`
in the NB regression. A sensitivity analysis varying the assumed prediction error
is recommended (standard errors-in-variables correction, or simulation).

The model selection rationale is documented in full in `cv/outputs/model_selection.json`
and in the written decision cell of `cv/pipeline/NB04_comparison.ipynb`.

---

## Secondary output: split assignment for labelled intersections

**File:** `cv/outputs/split_assignment.csv`

| Column | Description |
|--------|-------------|
| `sample_id` | `{intersection_id}_orig` or `{intersection_id}_aug{n}` |
| `intersection_id` | NWB junction identifier |
| `is_augmented` | Whether this row is a data-augmented copy |
| `aug_seed` | Augmentation seed (0 for originals) |
| `cv_split` | `train`, `val`, or `excluded` |

Use this to reconstruct which labelled intersections were used for CV training vs
validation, for the audit trail required by the NB model test-set boundary.

---

## Joining to other data sources

The `intersection_id` in all CV outputs is the NWB junction identifier, which is
the join key used throughout the project:

- Join to crash data on `intersection_id`
- Join to network features (from `intersections/` phase) on `intersection_id`
- Join to Bradley-Terry scores on `intersection_id` (for labelled subset only)

---

## What to do when real survey data arrives

1. Replace `cv/data/bt_scores.csv` with the updated file.
2. Re-run `NB01 → NB02 → NB03 → NB04 → NB05` in order.
3. The new `cv_scores_full_network.csv` is a drop-in replacement — same columns,
   same join key, updated scores.
4. Feature caches (`cv/features/`) remain valid and do not need to be regenerated.
5. Check that the `cv_split` boundary is still respected in the NB model test set.

---

## Files at a glance

```
cv/outputs/
├── cv_scores_full_network.csv   ← PRIMARY: use this in NB model
├── missing_photos.csv           ← intersections with no score (log)
├── split_assignment.csv         ← CV train/val boundary for NB test-set audit
├── model_selection.json         ← selected backbone, checkpoint path, metrics
├── resnet50_metrics.json        ← full metrics for ResNet-50 baseline
├── dinov2_vits14_metrics.json   ← full metrics for DINOv2-Small
└── nb05_spatial_map.png         ← thesis-ready map of predicted scores
```

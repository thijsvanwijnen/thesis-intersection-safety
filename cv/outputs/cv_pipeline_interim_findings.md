# CV Pipeline — Interim Findings (NB02 + NB03)

> **Caveat**: All results below are based on the test survey dataset (~80 labelled
> intersections, 63 train / 16 val). The Bradley-Terry scores used as regression
> targets were derived from a small pilot survey, not the full data collection.
> Performance numbers are preliminary and are expected to improve substantially
> once real survey responses are collected and BT scores are recomputed on the
> full labelled set (~145 intersections). **Do not interpret the metrics below as
> indicative of final model quality.**

---

## Results at a glance

| Metric | ResNet-50 (frozen) | DINOv2-Small (frozen) | Null model |
|--------|-------------------|-----------------------|------------|
| MAE | 0.1889 | 0.1924 | **0.1752** |
| RMSE | 0.2350 | 0.2423 | **0.2347** |
| R² | -0.008 | -0.071 | — |
| Spearman ρ | 0.391 | -0.015 | — |

Neither model beats the null model (predicting the training-set mean for every
intersection). Both models effectively converge to near-constant predictions around
the training mean (~0.66), regardless of the actual BT score. This is the classic
symptom of a model that has not found learnable structure in the data.

---

## Diagnosis

### Primary cause: insufficient training data

With only 63 training samples, neither backbone has enough signal to learn the subtle
visual correlates of human-derived pairwise safety preferences. The Bradley-Terry
safety score is a continuous value derived from comparison judgements; mapping raw
street-level image features to this score reliably requires far more labelled examples
than are currently available.

### DINOv2 performs worse than ResNet-50 here

This is counterintuitive but explained by the small N:

- ResNet-50 achieves Spearman ρ = 0.391 — a weak but real rank signal.
- DINOv2-Small achieves Spearman ρ = -0.015 — effectively random rank ordering.

DINOv2's CLS token (384-dim) encodes high-level semantic scene representations from a
self-supervised ViT. These abstract features require a richer training set to fit
meaningfully with a linear regression head. ResNet-50's 2048-dim spatially pooled
features apparently retain enough low-level texture/structure cues for a marginal
rank-ordering signal even at this small N.

### DINOv2 never triggered early stopping

The DINOv2 training ran all 200 epochs. Val MSE decreased monotonically from 0.0895
to 0.0587, never plateauing. This confirms the model is not learning generalizable
structure — it is slowly squeezing imperceptible gains from noise rather than
converging to a stable representation.

### Label noise compounds the small-data problem

At N=80, individual comparison judgements from the pilot survey carry a high
uncertainty. The BT scores themselves have elevated standard error, which reduces
the effective signal-to-noise ratio available to the regression head.

---

## What will change with real survey data

When full survey responses are collected and the BT model is re-run:

1. N will roughly double (~145 intersections), which disproportionately helps at
   the small-data end of the learning curve.
2. BT score uncertainty (SE) will decrease as more pairwise comparisons accumulate
   per intersection — cleaner labels.
3. Fine-tuning the last 2 DINOv2 transformer blocks (`FINETUNE_BACKBONE=True` in
   NB03) becomes a realistic option; currently the risk of overfitting is too high.
4. Enabling augmented training data (`USE_ORIGINALS_ONLY=False` in NB02/NB03) will
   further expand the effective training set.

The pipeline is correctly implemented. Re-running it with updated labels requires
only replacing `data/processed/bt_scores_augmented.csv` and re-executing
NB01 → NB02 → NB03 → NB04 → NB05 in order (feature caches remain valid).

---

## Decision: proceed to NB04 without retraining

NB04 will load the existing metrics JSONs from both notebooks and produce the
architecture comparison table and model selection. The selection decision will be
revisited when real survey data is available.

Current status of output artefacts:

| Artefact | Status |
|----------|--------|
| `outputs/resnet50_metrics.json` | Done |
| `outputs/dinov2_vits14_metrics.json` | Done |
| `outputs/resnet50_best.pt` | Done |
| `outputs/dinov2_vits14_best.pt` | Done |
| `outputs/split_assignment.csv` | Done |
| `outputs/nb02_training_curve.png` | Done |
| `outputs/nb03_training_curve.png` | Done |
| `outputs/nb03_attention_maps.png` | Done |
| NB04 comparison + model selection | **Pending** |
| NB05 full-network inference | **Pending** |

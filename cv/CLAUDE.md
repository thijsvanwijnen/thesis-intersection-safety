# CV Pipeline — Instructions for Claude Code

This file is the authoritative briefing for the computer vision phase of the intersection
safety study. Read it fully before writing any code.

---

## Context: what came before

Phase 1 of this research (Bradley-Terry model) is complete on test data and will be
re-run on full survey data when responses are collected. It produced:

- **`sampled_legs_directional_clean.csv`** — 308 rows, one per sampled intersection leg.
  Key columns: `intersection_id`, `leg_bearing`, `photo_filepath`, `dim_type`,
  `dim_priority`, `dim_risk`, `dim_speed`, `is_centrum`.
- **Bradley-Terry safety scores** — one continuous score per intersection [0, 1].
  Currently based on test data; the full pipeline will be re-run when real survey data
  arrives. The CV pipeline must be written so that re-running it with updated scores
  requires nothing more than pointing to a new labels file and re-executing all cells.
- **Reprojected photos (labelled set)** — JPEG, 1500×880 px, FOV=90°, taken ~20 m from intersection.
  Path convention: `{REPRO_ROOT}/{intersection_id}/leg_{bearing:.0f}.jpeg`
  where `REPRO_ROOT = D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_new`
- **Reprojected photos (full city)** — same format and path convention, different root.
  `FULL_CITY_REPRO_ROOT = D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_full_city`
  Coverage: 4,615 intersections selected; **926 have photos** (3,689 missing source panoramas).
  Leg selection log: `intersections/data/processed/full_city_leg_selection.csv`

---

## Goal of this phase (RQ2)

Train a computer vision model that generalises the expert-derived Bradley-Terry safety
scores from the ~145 labelled intersections to the full Rotterdam network (4,615
intersections selected; 926 with photos available). The model maps street-level
intersection photos → predicted safety score.

The CV-derived score is then added as a predictor in the Negative Binomial crash
prediction model (Phase 3). The NB model requires a single scalar per intersection,
not a feature vector, so the primary output is one number per intersection.

---

## Folder structure

```
cv/
├── CLAUDE.md                     ← this file
├── examples/                     ← old educational notebooks (do not edit)
│   ├── cv_example.ipynb
│   └── vit_dinov2_explained.ipynb
├── NB01_data_audit.ipynb         ← step 1: verify data before training
├── NB02_baseline_resnet.ipynb    ← step 2: ResNet-50 frozen backbone
├── NB03_dinov2.ipynb             ← step 3: DINOv2-Small backbone
├── NB04_comparison.ipynb         ← step 4: compare architectures, select model
├── NB05_predict_network.ipynb    ← step 5: score all 926 intersections with photos
├── (NB06_explainability.ipynb)   ← step 6: attention maps — optional/stretch goal
├── features/                     ← cached .pt feature tensors (git-ignored)
├── outputs/                      ← model checkpoints, score CSVs, figures
└── data/
    └── bt_scores.csv             ← Bradley-Terry labels (one row per intersection)
```

Move existing notebooks to `examples/` before starting. Do not modify them.

---

## Approach: iterative and exploratory

This phase is deliberately iterative. Unlike the Bradley-Terry phase, there is no single
correct architecture. The workflow is:

1. Audit the data and understand its structure before writing any model code.
2. Establish a working pipeline end-to-end with the simplest possible backbone (ResNet-50).
3. Swap in a stronger backbone (DINOv2-Small) and compare metrics.
4. Decide on the final architecture based on evidence, not assumptions.
5. Run inference on the full network only after the model is validated.

Resist the urge to build everything at once. Each notebook should be independently
executable and produce a concrete artefact (a cached feature file, a trained checkpoint,
a metrics table, a score CSV).

---

## Pipeline architecture

```
One reprojected photo per intersection (JPEG 1500×880)
        ↓
Backbone (frozen pretrained CNN or ViT)
        ↓
Feature vector per intersection
        ↓
Regression head (small MLP, trained on BT scores)
        ↓
Predicted safety score ∈ [0, 1]
```

### Backbone options

| Backbone      | Feature dim | Params | Notes                                      |
|---------------|-------------|--------|--------------------------------------------|
| ResNet-50     | 2048        | 25M    | Baseline; replace `fc` with `nn.Identity()`|
| DINOv2-Small  | 384         | 21M    | Primary candidate; `torch.hub` load        |
| ViT-B/16      | 768         | 86M    | Frozen only; risky on small N              |

Start with ResNet-50 to validate the pipeline. Then swap to DINOv2-Small.
DINOv2 is self-supervised on 142M diverse images (LVD-142M); it generalises better to
street-level scenes than supervised ImageNet backbones.

### Regression head

```python
nn.Sequential(
    nn.Linear(feature_dim, 128),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(128, 1),
    nn.Sigmoid()   # output in [0, 1]
)
```

Only the regression head is trained. Backbone weights are frozen unless NB03 explicitly
adds a fine-tuning stage (last 2 DINOv2 blocks, lr=1e-5, with early stopping).

### Preprocessing

```python
# Training transform
transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Validation/inference transform (deterministic)
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

Do NOT use vertical flips or large rotations — intersection photos have a fixed
perspective and sky/road orientation is semantically meaningful.

For DINOv2-Small with patch size 14, resize to 518×518 (= 37×37 patches) or
336×336 (= 24×24 patches) rather than 224×224. Document the choice.

---

## Data rules — non-negotiable

### Split at intersection level

One photo corresponds to one intersection (1:1 mapping), so splitting on
`intersection_id` and splitting on photo path are equivalent. Still, always split on
`intersection_id` explicitly to make the intention clear and to keep the code robust
if the input data ever changes.

```python
# Correct
intersection_ids = df["intersection_id"].unique()
train_ids, val_ids = train_test_split(intersection_ids, test_size=0.2,
                                      random_state=42)

# Avoid — works now but obscures intent
images = df["photo_filepath"].tolist()
train_imgs, val_imgs = train_test_split(images, ...)
```

### Spatial stratification for cross-validation

When running k-fold cross-validation, intersections within the same geographic cluster
must be assigned to the same fold. Use the stratum columns (`dim_type`, `dim_priority`,
`is_centrum`) as a proxy for spatial clustering if a dedicated spatial fold assignment
is not available. This prevents spatial autocorrelation from inflating validation metrics.

### Separation from NB model test set

Intersections used for CV model training and validation must be excluded from the NB
model test set (Phase 3). The CV outputs CSV must include a column `cv_split` with
values `train`, `val`, or `unlabelled` to make this boundary explicit and auditable.

### Cache features, do not re-extract every epoch

Feature extraction through the frozen backbone is expensive and deterministic. Run it
once, save to disk as `.pt` files, and load from cache in subsequent runs.

```python
cache_path = Path("features") / f"{backbone_name}_{intersection_id}.pt"
if cache_path.exists():
    features = torch.load(cache_path)
else:
    features = extract_features(images)
    torch.save(features, cache_path)
```

---

## Metrics

Primary: **MAE** and **RMSE** on the validation set.
Secondary: **R²** and **Spearman ρ** (rank correlation — important because the BT scores
are derived from pairwise comparisons and have ordinal structure).

Report all four metrics for every model variant in NB04. Do not select a model based
on a single metric.

Also report the **null model baseline**: predicting the training-set mean for all
intersections. A model that does not beat this baseline is not useful.

---

## Notebook specifications

### NB01 — Data audit

Purpose: understand the data before writing model code. This notebook has no ML.

- Load `bt_scores.csv` and `sampled_legs_directional_clean.csv`. Report shapes,
  missing values, and column types.
- Plot the distribution of BT scores. Note skewness, floor/ceiling effects.
- Verify that each intersection_id in `bt_scores.csv` maps to exactly one photo on disk.
  Print a summary: N found, N missing, N total.
- Plot the geographic distribution of labelled intersections overlaid on the Rotterdam
  stratum map (use `intersections_stratified.gpkg` if available).
- Propose the train/val split and document it. Save the split assignment to
  `outputs/split_assignment.csv` (columns: `intersection_id`, `cv_split`).

No model code in this notebook.

### NB02 — Baseline: ResNet-50

Purpose: establish an end-to-end working pipeline and produce a first performance number.

Sections (in order):
1. Configuration block at the top — all paths and hyperparameters as named constants.
2. Dataset class (`IntersectionDataset`) reading real images from disk.
3. Feature extraction with frozen ResNet-50; cache to `features/resnet50/`.
4. Regression head training loop (MSE loss, Adam optimiser).
5. Validation metrics: MAE, RMSE, R², Spearman ρ. Compare to null model.
6. Residual plot: predicted vs actual BT score. Flag high-error intersections.
7. Save best checkpoint to `outputs/resnet50_best.pt`.
8. Save training curve (loss vs epoch) as a figure.

Hyperparameters to document and justify: learning rate, batch size, dropout rate,
number of epochs, early stopping patience.

### NB03 — DINOv2-Small

Purpose: test whether a self-supervised ViT backbone improves over ResNet-50.

Structure mirrors NB02 exactly (same sections, same metrics, same split). Differences:

- Backbone: `torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")`
- Feature dim: 384
- Resize images to 518×518 before feature extraction (or 336×336 — document choice)
- Feature cache to `features/dinov2_vits14/`
- Optional fine-tuning section (clearly labelled, default OFF):
  unfreeze last 2 transformer blocks, train with lr=1e-5, early stopping patience=5.
  Compare frozen vs fine-tuned metrics in a small table.
- Attention map visualisation: extract `[CLS]-to-patch` attention from the last block
  for 3–5 example intersections. Display overlaid on the original photo. Note what
  spatial regions the model attends to.

Save best checkpoint to `outputs/dinov2_vits14_best.pt`.

### NB04 — Architecture comparison and model selection

Purpose: synthesise results from NB02 and NB03 and select the production model.

- Load validation metrics from both notebooks (save them as JSON in `outputs/` so
  NB04 can load them without re-running training).
- Comparison table: backbone × metric (MAE, RMSE, R², Spearman ρ) + null model row.
- Bar chart: MAE by backbone.
- Scatter plot: predicted vs actual for both backbones, side by side.
- Error analysis: which intersections have the highest residuals? Are they
  systematically from one stratum, one district, or one dim_type?
- Written decision: state which model is selected and why. This text goes into the
  thesis Methods section as-is.
- Save selection to `outputs/model_selection.json`:
  `{"selected_backbone": "dinov2_vits14", "checkpoint": "dinov2_vits14_best.pt", ...}`

### NB05 — Predict full network

Purpose: apply the selected model to all 926 Rotterdam intersections that have a
reprojected photo available (out of 4,615 selected; 3,689 lack source panoramas).

- Load `model_selection.json` and the corresponding checkpoint.
- Load the full-city leg selection from `FULL_CITY_LEG_CSV`
  (`intersections/data/processed/full_city_leg_selection.csv`). This file already
  records which legs have photos — use it as the intersection list rather than the
  `.gpkg`, to avoid re-checking photo existence for every row.
- For intersections without a reprojected photo (rows present in the `.gpkg` but
  absent from `full_city_leg_selection.csv`), log them to
  `outputs/missing_photos.csv` and skip gracefully.
- Extract features (reuse cached files where available; extract new ones for
  unlabelled intersections).
- Run inference. Output: one predicted safety score per intersection.
- Save to `outputs/cv_scores_full_network.csv`:
  columns `intersection_id`, `cv_score_predicted`, `cv_split`.
- Plot the spatial distribution of predicted scores on a Rotterdam map.
  Colour by quartile. This figure is thesis-ready.
- Report summary statistics of predicted scores by stratum.

### NB06 — Explainability (stretch goal)

Only attempt this if the core pipeline is complete and validated. Do not start NB06
if NB05 has not produced a full-network score file.

- Attention maps for a stratified sample of intersections (high-score, mid-score,
  low-score, and high-residual).
- Check whether the model attends to interpretable features: road markings, signage,
  vegetation, lane widths, conflict zones.
- Write a brief qualitative summary: does the model's attention align with what traffic
  engineers said in the preparatory interviews?
- This section feeds directly into RQ5.

---

## Re-running with new BT scores

When real survey data becomes available and new BT scores are computed:

1. Replace `data/bt_scores.csv` with the updated file.
2. Delete `features/` only if the photos themselves have changed (they have not).
3. Re-run NB01 → NB02 → NB03 → NB04 → NB05 in order.
4. NB01 will produce a new `outputs/split_assignment.csv` — check that the split
   proportions are still reasonable before proceeding.
5. Feature caches from the previous run are valid and can be reused; only the
   regression head needs to be re-trained.

The pipeline is designed so that steps 2–5 can be completed in a single session.

---

## Key paths

| Variable          | Value                                                                                  |
|-------------------|----------------------------------------------------------------------------------------|
| `REPRO_ROOT`           | `D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_new` |
| `FULL_CITY_REPRO_ROOT` | `D:\rotterdam_aiis_2025\vault-production\vault_v1\reprojected_directional_fov90_dist20_full_city` |
| `SERVER_ROOT`          | `\\tudelft.net\staff-umbrella\SLIRotterdam\images`                                   |
| `LEGS_CSV`             | `intersections/data/processed/sampled_legs_directional_clean.csv`                      |
| `FULL_CITY_LEG_CSV`    | `intersections/data/processed/full_city_leg_selection.csv`                             |
| `BT_SCORES_CSV`        | `cv/data/bt_scores.csv`                                                                |
| `INTERSECTIONS_GPKG`   | `intersections/data/processed/intersections_stratified.gpkg`                          |
| `FEATURES_DIR`         | `cv/features/`                                                                         |
| `OUTPUTS_DIR`          | `cv/outputs/`                                                                          |

Always define these as constants at the top of each notebook. Never hardcode paths
inside functions.

---

## Dependencies

```python
torch >= 2.0          # CPU or CUDA; DINOv2 loads via torch.hub
torchvision
numpy
pandas
matplotlib
Pillow
scipy                 # for Spearman ρ
geopandas             # for spatial plots in NB01 and NB05
scikit-learn          # for train_test_split and metrics
```

DINOv2 first load requires internet access (downloads to `~/.cache/torch/hub/`).
Subsequent runs use the local cache.

---

## What to do right now

1. Move `cv_example.ipynb` and `vit_dinov2_explained.ipynb` to `cv/examples/`.
2. Create `cv/data/bt_scores.csv` from the existing Bradley-Terry output.
   Required columns: `intersection_id`, `bt_score`. Add any metadata columns
   (stratum, n_comparisons, score_se) that are available — they will be useful in NB01.
3. Start NB01. Do not write model code until NB01 confirms that all labelled
   intersections have at least one photo on disk and the score distribution looks
   reasonable.
4. Work through NB02 → NB03 → NB04 in order. Resist skipping ahead.

---

## Constraints and known limitations to document in the thesis

- The model is trained on ~145 labelled intersections (test data) and will be retrained
  on the full labelled set once survey responses are collected. Reported metrics on test
  data are preliminary.
- Spatial stratification in cross-validation is approximate. The same geographic cluster
  may appear in both train and val if the cluster is large and the sample is small.
- Error propagation: the CV-derived score carries prediction error (MAE from NB04) that
  attenuates the estimated β coefficient in the NB model. A sensitivity analysis
  varying the assumed prediction error is included in Phase 3.
- The model is trained on Rotterdam intersections. Transferability to other cities is
  not claimed.

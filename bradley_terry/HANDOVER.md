# Handover — Bradley-Terry Scoring Pipeline

This document records the interface between the `bradley_terry/` scoring step and the downstream `cv/` computer vision model.

---

## Input

- **Source database:** `data/raw/database.db`
- **Respondent completeness criterion:** `act1_t36 IS NOT NULL` (proxy for finishing all 36 tasks)
  - Parameterised as `MIN_TASKS_COMPLETED` in NB01 (default: 36)

---

## Processing summary

*(Fill in after running all notebooks)*

| Metric | Value |
|---|---|
| Total respondents in database | — |
| Respondents included (complete) | — |
| Total comparisons used | — |
| Unique intersections with a score | — |
| Intersections without a score (0 comparisons) | — |

---

## Output

**File:** `data/output/bt_scores.csv`

| Column | Type | Description |
|---|---|---|
| `intersection_id` | string | Intersection ID — matches the filename stem of the streetview photo (e.g. `182270019`) |
| `bt_param_raw` | float | Raw log-strength from the ILSR Bradley-Terry estimator |
| `bt_score_normalized` | float | Min-max normalised to [0, 1] |
| `n_comparisons` | int | Number of comparisons in which this intersection appeared |
| `n_wins` | int | Number of times this intersection was chosen as more dangerous |
| `image_path` | string | Full photo path as used in the survey app (e.g. `/assets/images/182270019.jpeg`) |

---

## Score semantics

**High score (→ 1) = intersection perceived as MORE dangerous.**  
**Low score (→ 0) = intersection perceived as LESS dangerous.**

The raw BT log-strength parameter is positive when an intersection wins more often than expected under a uniform model. After min-max normalisation, the most-dangerous intersection scores 1 and the least-dangerous scores 0.

The `cv/` model should therefore treat `bt_score_normalized` as a **risk label**, where 1 = high risk and 0 = low risk.

---

## Notes on data quality

*(Fill in after NB04)*

- Kendall's W: —
- Deviance per comparison: —
- Response time analysis: informational only — per-respondent median/min/max in `respondent_quality.csv`, no respondents excluded
- Circular triads: median — per respondent

---

## Known issues / quirks

1. `Response` table has columns `act1_t1..act1_t300`; only `t1..t36` are used.
2. No `finished` column in `Task_set` — completeness is inferred from `act1_t36 IS NOT NULL`.
3. Intersection IDs are extracted from photo file paths (stem of filename), not a dedicated column.

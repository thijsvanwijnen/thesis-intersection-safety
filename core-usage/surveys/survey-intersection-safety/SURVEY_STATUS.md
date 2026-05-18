# Survey Status — Intersection Safety Study

**Status:** Live as of 2026-05-13  
**URL:** https://similarity-survey.tudelft.nl  
**Researcher:** Thijs van Wijnen — gvanwijnen@student.tudelft.nl  
**Institution:** TU Delft, Faculteit Technologie, Beleid en Management

---

## What this survey does

Experts (traffic safety professionals) compare pairs of Rotterdam intersection street-level photos and judge which intersection has a higher risk of a serious road accident. The survey uses a **pairwise stated choice** design with 36 comparison tasks per respondent. Results feed a **Bradley-Terry model** to produce a continuous safety score per intersection, which is then used to improve crash prediction models.

---

## Survey flow

```
/home → /consent → /screening → /instructions → /act1/1 → ... → /act1/36 → /act2 → /end
                                                                              ↓
                                                                         (if quota full)
                                                                         /fullquota
```

| Page | File | Purpose |
|------|------|---------|
| `/home` | `pages/home.py` | Landing page |
| `/consent` | `pages/consent.py` | Informed consent + creates respondent in DB |
| `/screening` | `pages/screening.py` | 3 screening questions; checks quota |
| `/instructions` | `pages/instructions.py` | Task instructions |
| `/act1/<n>` | `pages/act1.py` | 36 pairwise comparison tasks (dynamic route) |
| `/act2` | `pages/act2.py` | 2 required + 1 optional background questions |
| `/end` | `pages/end.py` | Thank-you page |
| `/fullquota` | `pages/fullquota.py` | Shown when quota is full |

Navigation links are pre-computed on consent and stored in browser session (`hrefs-store`). The app uses Dash with `use_pages=True` and `refresh=False` (single-page app routing via `dcc.Location`).

---

## Tech stack

- **Framework:** Python Dash + Dash Bootstrap Components
- **Database:** SQLite (`database.db` in this folder)
- **Deployment:** Docker + Gunicorn + HTTPS (Let's Encrypt) on TU Delft server
- **Server:** `similarity-survey.tudelft.nl`, user `gvanwijnen`, survey at `/home/gvanwijnen/survey-intersection-safety/`

---

## Database schema

### Table: `Response`
One row per respondent. Key columns:

| Column | Content |
|--------|---------|
| `respondent_id` | Integer; milliseconds since 2026-05-01 (unique per respondent) |
| `set_id` | Which task set was assigned |
| `external_id` | Optional external panel ID |
| `sq1_professional_role` | Screening Q1: professional role (values 1–6) |
| `sq2_years_experience` | **Actually stores organization** (values 1–7) — column name is misleading |
| `sq3_intersection_assessment_experience` | **Actually stores years of experience** (values 1–4) — column name is misleading |
| `act1_t1` … `act1_t36` | Pairwise choice answers (1 or 2) |
| `act2_q1` | How often they conduct intersection inspections (1–4) |
| `act2_q2` | Familiarity with Duurzaam Veilig principles (1–4) |
| `act2_q3` | Optional open text remarks |

### Table: `Timestamp`
One row per respondent. Tracks Unix timestamps of every button click (consent, screening, each act1 task, act2).

### Table: `Task_set`
One row per task set (14 sets total). Columns: `set_id`, `act1_task_1`…`act1_task_36` (task IDs), `used` (0/1), `finished` (0/1).

### Table: `Quotas`
Screening quota table. All quotas set to 9999 (effectively unlimited). Columns: `sq1_professional_role`, `sq2_years_experience`, `sq3_intersection_assessment_experience`, `quota`, `actual`.

---

## Task set recycling logic

When a new respondent starts, `database.py._get_next_task_set_id()` picks a task set using 3-priority fallback:

1. **Priority 1 — never started:** pick the lowest `set_id` where `used = 0`
2. **Priority 2 — abandoned:** pick a set where `used = 1` but `finished = 0` (someone dropped out)
3. **Priority 3 — all finished:** pick randomly to keep collecting data

`used` is set to 1 on consent. `finished` is set to 1 when the respondent clicks Continue on act2 (the last step).

---

## Screening questions (pages/screening.py)

1. Professional role (6 options: traffic engineer, safety specialist, urban planner, policy advisor, safety consultant, other)
2. Organization (7 options: Rotterdam municipality, other municipality, province, Rijkswaterstaat, engineering firm, research institute, prefer not to say)
3. Years of professional experience (4 options: <2, 2–5, 6–10, >10)

Quota check runs on the Quotas table. With all quotas at 9999, every respondent passes.

---

## Background questions (pages/act2.py)

1. How often do you conduct site inspections or safety audits at intersections? (required, dropdown, 4 options)
2. How familiar are you with Duurzaam Veilig design principles? (required, dropdown, 4 options)
3. Any remarks about the assessment task or photos? (optional, free text)

**Important:** only questions 1 and 2 are required to enable the Continue button. Question 3 is optional and must NOT block submission.

---

## Key implementation decisions

- **Respondent ID** is generated as milliseconds since a reference date (`time.mktime((2026, 5, 1, ...))`) to make IDs unique and time-ordered. Query newest respondents with `ORDER BY consent_button DESC` (not by respondent_id).
- **Session storage** (`dcc.Store`) holds respondent ID and all task data in the browser. No server-side session state.
- **`hrefs-store`** is a pre-computed dict of `{path: next_path}` for the full navigation chain, stored in browser session on consent.
- **Pages are manually maintained.** The Dash pages were originally generated from `survey.yaml` via `pixelsurvey_core` but have been heavily customised. Do NOT re-run `survey_gen` — it would overwrite all fixes.

---

## Bugs fixed during development (do not reintroduce)

1. **act2 optional question blocking submit** — `toggle_continue_button` must only check `question_values[:2]`, not all 3 values. Question-3 is a Textarea that starts as `None` and will block submission if included in the required check.
2. **mark_survey_finished never called** — must be called in `handle_questionnaire_click` in act2.py alongside `update_quota`, when `hrefs['next']['/act2'] == '/end'`.
3. **Dead code in act1.py** — `update_quota` call inside act1's button handler (`if hrefs['next'][f'/act1/{task_nr}'] == '/end'`) is dead code because act1/36 always leads to /act2, never /end. Leave it; it's harmless.
4. **Task set crash at respondent 15** — original `_get_next_task_set_id()` returned `None` when all sets were used. Fixed by 3-priority fallback logic.

---

## Deployment commands

### Upload single changed file (Windows → server)

**Step 1 — Windows PowerShell → bastion:**
```powershell
scp "<local_file_path>" gvanwijnen@student-linux.tudelft.nl:/home/nfs/gvanwijnen/<filename>
```

**Step 2 — Bastion → server:**
```bash
scp ~/<filename> gvanwijnen@similarity-survey.tudelft.nl:/home/gvanwijnen/survey-intersection-safety/<relative_path>
rm ~/<filename>
```

**Step 3 — Server: rebuild Docker:**
```bash
cd ~/survey-intersection-safety
sudo docker compose down
sudo docker compose build
sudo docker compose up -d
sudo docker logs intersection-safety_container --tail=20
```

### Check / fix `finished` column (run after each rebuild)
```bash
sudo docker exec -it intersection-safety_container sqlite3 database.db "PRAGMA table_info(Task_set);"
# If 'finished' column is missing:
sudo docker exec -it intersection-safety_container sqlite3 database.db "ALTER TABLE Task_set ADD COLUMN finished INTEGER DEFAULT 0;"
```

### Query recent respondents
```bash
sudo docker exec -it intersection-safety_container sqlite3 database.db \
  "SELECT r.respondent_id, r.act2_q3 FROM Response r JOIN Timestamp t ON r.respondent_id = t.respondent_id ORDER BY t.consent_button DESC LIMIT 5;"
```

### Reset database (test data only — do not run in production)
```sql
DELETE FROM Response;
DELETE FROM Timestamp;
UPDATE Task_set SET used = 0, finished = 0;
UPDATE Quotas SET actual = 0;
```

---

## Input files

| File | Description |
|------|-------------|
| `assets/images/*.jpeg` | Street-level panoramic photos of Rotterdam intersections |
| `../../recipes/recipe-intersection-safety/experiments/pairwise_design.csv` | Which intersection pairs are compared per task set |
| `../../recipes/recipe-intersection-safety/survey.yaml` | Survey config (do not regenerate from this) |

---

## Next steps (as of 2026-05-13)

- Survey is live and being sent to participants
- Collect responses until sufficient coverage across task sets
- Export responses from SQLite for Bradley-Terry model fitting
- Join survey scores with crash data for intersection-level analysis

# Competition Instructions

**Competition:** [Playground Series S6E9 — Predicting Electric Vehicle Purchases](https://www.kaggle.com/competitions/playground-series-s6e9)

## Verified facts

First read from the Kaggle API on **2026-09-01** (scaffold session); data-level
facts verified against the downloaded files on **2026-09-01** after joining.
Anything that can move is timestamped; re-check before relying on it.

| Item | Value | Source |
|---|---|---|
| Competition ref | `playground-series-s6e9` | `kaggle competitions list` |
| Title | Predicting Electric Vehicle Purchases | competition page |
| Category | Playground | `kaggle competitions list` |
| Reward | Swag | `kaggle competitions list` |
| **Deadline** | **2026-09-30 23:59 UTC** | Kaggle API, re-confirmed 2026-09-01 |
| Entry / merger deadline | same as final deadline | Kaggle API, 2026-09-01 |
| Teams entered | 92 | as of 2026-09-01 (was 57 at scaffold time) — early, will move |
| Joined | **Yes** (`userHasEntered: True`) | Kaggle API, 2026-09-01 |
| **Evaluation metric** | **ROC AUC** (`evaluation_metric = "Roc Auc Score"`) | Kaggle API competition object, 2026-09-01 |
| Max daily submissions | 10 | Kaggle API, 2026-09-01 |
| Max team size | 3 | Kaggle API, 2026-09-01 |
| Kernels-only submissions | `False` — file upload permitted | Kaggle API, 2026-09-01 |
| Data published | 2026-08-12 | file creation dates |

Note on sources: the competition page itself is client-rendered and not
fetchable by URL, so the Evaluation/Data tab *prose* has not been read
verbatim. The metric above comes from the Kaggle API's competition object,
which is authoritative. If the Overview/Data prose is ever pasted in, quote
it here (S6E8 did exactly that).

## Task

**Binary classification.** Predict the probability that `Will_Buy_EV = "Yes"`
for each test row; submissions are scored with ROC AUC against the observed
target. Confirmed against the data (target values are `Yes`/`No` strings;
`sample_submission.csv` carries a constant *probability*, not a label — and
that constant, `0.174645`, is exactly the train positive rate
116,779 / 668,665).

## Data (verified against downloaded files, 2026-09-01)

| File | Shape | Notes |
|---|---|---|
| `train.csv` | 668,665 × 15 | `id` + 13 features + `Will_Buy_EV` |
| `test.csv` | 286,571 × 14 | `id` + 13 features |
| `sample_submission.csv` | 286,571 × 2 | `id`, `Will_Buy_EV` (float) |

- **Target:** `Will_Buy_EV` — `No` 551,886 (82.54%) / `Yes` 116,779 (17.46%).
- **IDs:** train `0..668664`, test `668665..955235`, both contiguous.
- **No missing values** in train or test, in any column (unlike S6E8, where
  missingness handling was a whole workstream).
- **No duplicate feature rows** in train (0 duplicates excluding `id`).

**Numeric features (7):**

| Feature | dtype | Train range | Notes |
|---|---|---|---|
| `Age` | int | 25–69 | |
| `Annual_Income_USD` | float | 30,000–188,549 | test max 186,936 |
| `Daily_Commute_km` | float | 5.0–98.7 | **test max 103.9 — exceeds train range** |
| `Number_of_Cars_Owned` | int | 1–4 | |
| `Charging_Stations_Near_Home` | int | 0–14 | |
| `Charging_Stations_Near_Work` | int | 0–19 | |
| `Environmental_Concern_Level` | float | 1–5 | discrete 1.0–5.0 — ordinal stored as float |

**Categorical features (6)** — train and test vocabularies match exactly:

| Feature | Levels (train counts) |
|---|---|
| `Gender` | Male 367,954 / Female 295,427 / Other 5,284 |
| `City_Type` | Urban 289,305 / Suburban 255,377 / Rural 123,983 |
| `Current_Car_Type` | Sedan 303,459 / SUV 246,545 / Hatchback 79,438 / Truck 39,223 |
| `Home_Charging_Possible` | Yes 462,677 / No 205,988 |
| `Subsidy_Available` | Yes 419,909 / No 248,756 |
| `Range_Anxiety_Level` | Low 603,972 / Medium 62,499 / High 2,194 — **High is rare (0.33%)** |

## Submission format

From `sample_submission.csv`: header `id,Will_Buy_EV`, 286,571 rows, `id`
ascending from 668,665, one probability per row.

```
id,Will_Buy_EV
668665,0.174645
668666,0.174645
668667,0.174645
```

Run `scripts/verify_submission.py` against every artifact before submitting
(`docs/0_coding_standards.md`).

## Submission mechanism

Not a Code Competition (`is_kernels_submissions_only = False`), so file upload
works — but master standard §11 still applies: submit via a completed Kaggle
kernel version (`kaggle competitions submit -k <user>/<kernel> -v <version>
-f submission.csv`) so every score is tied to code Kaggle actually has.
Playground Series accepts this; verified in practice on earlier episodes.

## Still open

- [x] **Original source dataset** — **identified 2026-09-02** as
      `itzzomkar/ev-adoption-behavior-and-range-anxiety` (CC0). Provenance,
      licence and usage recorded in
      [`docs/7_source_dataset_provenance.md`](7_source_dataset_provenance.md).
      Tested as extra training rows (E05: null) and later used as a
      *feature* by the champion (E06 onward).
- [ ] **Overview/Evaluation prose verbatim.** Nice-to-have for the record;
      the operative facts (metric, format) are already verified via API +
      files above.

## First steps — status

1. ~~Join the competition~~ — **done** (2026-09-01).
2. ~~Download data~~ — **done** (2026-09-01, `data/`, gitignored).
3. ~~Fill in metric / target / format / task type~~ — **done**, above.
4. ~~`notebooks/01_eda.ipynb`~~ — **done** (2026-09-01, published as EDA
   kernel v3).
5. ~~Modeling~~ — **done**: E01–E09, see
   [`docs/4_experiment_ledger.md`](4_experiment_ledger.md).

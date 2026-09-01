# Competition Instructions

**Competition:** [Playground Series S6E9 — Predicting Electric Vehicle Purchases](https://www.kaggle.com/competitions/playground-series-s6e9)

## Verified facts

Read from the Kaggle API on **2026-09-01**. Anything here that can move is
timestamped; re-check before relying on it.

| Item | Value | Source |
|---|---|---|
| Competition ref | `playground-series-s6e9` | `kaggle competitions list` |
| Title | Predicting Electric Vehicle Purchases | competition page |
| Category | Playground | `kaggle competitions list` |
| Reward | Swag | `kaggle competitions list` |
| **Deadline** | **2026-09-30 23:59 UTC** | `kaggle competitions list`, 2026-09-01 |
| Teams entered | 57 | as of 2026-09-01 — early, will move |
| Data published | 2026-08-12 | file creation dates |

**Data files** (`kaggle competitions files playground-series-s6e9`):

| File | Size |
|---|---|
| `train.csv` | 44,707,646 B (~44.7 MB) |
| `test.csv` | 18,298,347 B (~18.3 MB) |
| `sample_submission.csv` | 7,737,432 B (~7.7 MB) |

A 7.7 MB sample submission implies a large test set — order 10^6 rows, not the
10^4–10^5 typical of earlier Season 6 episodes. Worth confirming once the data
is downloadable, because it changes what is affordable per experiment.

## Not yet verified — fill these in first

**The competition has not been joined yet.** `userHasEntered` is `False`, and
`kaggle competitions download` returns `403 Forbidden`. Accept the rules on the
competition page before anything else; nothing below can be settled until then.

- [ ] **Evaluation metric.** Unknown. Not stated on the fetchable part of the
      page and not yet indexed by search — the competition is three weeks old.
      Do **not** assume ROC AUC because the title sounds binary. Read the
      Evaluation tab and record the exact metric name here.
- [ ] **Target column.** Unknown — needs `sample_submission.csv`.
- [ ] **Submission format.** Unknown — column names and dtypes from
      `sample_submission.csv`.
- [ ] **Task type.** The title implies binary classification (purchase / no
      purchase), but this is an inference from the title, not a read fact.
      Confirm against the Evaluation tab and the target's actual values.
- [ ] **Original source dataset.** Playground data is normally generated from a
      real dataset, and the original is usually permitted as extra training
      data. Find whether one is named, and record it in a provenance doc if so.
- [ ] **Submission mechanism.** Confirm whether this is a Code Competition
      (notebook re-executed by Kaggle) or file-upload. Master standard §11
      requires notebook-based submission where supported.

## First steps

1. Join the competition on Kaggle.
2. `kaggle competitions download -c playground-series-s6e9 -p data/`
   (`data/` is gitignored — see master standard §8).
3. Fill in every unchecked item above from the Evaluation and Data tabs.
4. Then start `notebooks/01_eda.ipynb`.

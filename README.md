# Predicting Electric Vehicle Purchases

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E9-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e9)
[![Status](https://img.shields.io/badge/Status-Baseline-blue)](docs/4_experiment_ledger.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E9:
https://www.kaggle.com/competitions/playground-series-s6e9

Public-notebook-first workflow. Notebooks are the executable source of truth;
`docs/` records rationale, validation, and submission evidence.

## Status

**Baselines + E01 tuning done; first submission scored (2026-09-01).**

| Champion | OOF AUC (F1: 5-fold strat., seed 42) | Promotion |
| --- | --- | --- |
| `e01_cat_2000x05` | **0.94176 ± 0.00074** | paired gate: 5/5 folds, 95% CI (+0.000145, +0.000239), P(Δ>0)=1.0 |

Public leaderboard: **0.94169** (submission 1, kernel v2, 2026-09-01) —
CV↔LB gap −0.00008, confirming the no-drift EDA verdict. Manifest:
[`docs/5_submission_manifest.md`](docs/5_submission_manifest.md).

All five baseline runs, decisions, and the predeclared promotion gates:
[`docs/4_experiment_ledger.md`](docs/4_experiment_ledger.md). EDA findings:
[`docs/2_eda_insights.md`](docs/2_eda_insights.md) — top-heavy signal, one
big interaction (the subsidy gate), no missingness, no drift.

- Task: binary classification — probability that `Will_Buy_EV = "Yes"`.
- Metric: **ROC AUC** (verified via the Kaggle API, 2026-09-01).
- Train 668,665 rows x 13 features; test 286,571 rows.

Deadline: **2026-09-30 23:59 UTC** (Kaggle API, re-confirmed 2026-09-01).

## Getting started

```bash
# 1. Join the competition on Kaggle first, or the download 403s.
kaggle competitions download -c playground-series-s6e9 -p data/
unzip -o 'data/*.zip' -d data/

# 2. Fill in the unchecked items in docs/1_instructions.md from the
#    Evaluation and Data tabs before writing any modelling code.
```

## Repository layout

- [`notebooks/`](notebooks/) — the executable workflow, plus
  `notebooks/kernels/<name>/` holding each notebook's Kaggle
  `kernel-metadata.json`.
- [`docs/`](docs/) — numbered notes: coding standards, competition
  instructions, and (as work starts) EDA, experiments, and submissions.
- [`scripts/`](scripts/) — `push_kaggle_kernel.sh` for pushing a notebook to
  its Kaggle kernel, and `verify_submission.py` for pre-submission checks.
- `data/`, `predictions/` — local and generated, gitignored.

## Conventions

Standards are layered: the shared master standard at
`~/Documents/GitHub/coding-standards/` is the baseline, and
[`docs/0_coding_standards.md`](docs/0_coding_standards.md) holds the
project-specific rules and deliberate overrides.

Agents working here should start from [`AGENTS.md`](AGENTS.md).

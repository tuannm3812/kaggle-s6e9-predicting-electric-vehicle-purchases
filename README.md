# Predicting Electric Vehicle Purchases

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E9-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e9)
[![Status](https://img.shields.io/badge/Public%20LB-0.94570-success)](docs/5_submission_manifest.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E9:
https://www.kaggle.com/competitions/playground-series-s6e9

Public-notebook-first workflow. Notebooks are the executable source of truth;
`docs/` records rationale, validation, and submission evidence.

## Status

**E09 complete (2026-09-04). Nine experiments, seven submissions.**

| | Model | OOF AUC | Public LB |
| --- | --- | --- | --- |
| **Champion** (paired-gate promoted, fold class F1) | `e08_avg3seeds` | 0.94550 | 0.94565 |
| **Best public score** (fold class F2 — not gateable against F1) | `e09_f2_avg3seeds` | 0.94564 (F2) | **0.94570** |

Progression: 0.94169 → 0.94198 → 0.94210 → 0.94562 → 0.94565 → 0.94570.

**The step that mattered was E06 (+0.00337 OOF), and it came from a
30-second diagnostic, not a sweep.** The "numeric" columns are *value
identities*: `Annual_Income_USD` takes 13,214 distinct values, 97.9% of
them drawn from the source dataset, and the exact value carries label
information its magnitude does not — signal that tree quantization (254
borders) cannot reach. Encoding those values as CatBoost categoricals
was worth five times every other accepted step combined. Full reasoning:
[`docs/4_experiment_ledger.md`](docs/4_experiment_ledger.md), E06.

Every run — kept or rejected — is in the ledger with its gate predeclared
*before* execution, and the failed predictions are recorded as plainly as
the successful ones. Two comparability classes are enforced in code
rather than by convention: CPU/GPU, and fold definition F1/F2.

- Task: binary classification — probability that `Will_Buy_EV = "Yes"`.
- Metric: **ROC AUC** (verified via the Kaggle API, 2026-09-01).
- Train 668,665 rows x 13 features; test 286,571 rows.
- Noise floor: **0.00005** on the current representation.

Deadline: **2026-09-30 23:59 UTC** (Kaggle API, re-confirmed 2026-09-01).

## Getting started

```bash
# 1. Join the competition on Kaggle first, or the download 403s.
kaggle competitions download -c playground-series-s6e9 -p data/
unzip -o 'data/*.zip' -d data/

# 2. Notebooks are authored locally but EXECUTED ON KAGGLE.
bash scripts/push_kaggle_kernel.sh baseline
kaggle kernels status tuannm3812/ev-purchases-baseline-modeling
kaggle kernels output tuannm3812/ev-purchases-baseline-modeling -p out/

# 3. Before pushing, run both local checks (they cover different things):
python3 scripts/check_frames.py        # every experiment's feature frames exist
python3 scripts/verify_submission.py <artifact.csv> \
    --test data/test.csv --sample data/sample_submission.csv
```

## Repository layout

- [`notebooks/`](notebooks/) — the executable workflow, plus
  `notebooks/kernels/<name>/` holding each notebook's Kaggle
  `kernel-metadata.json`.
- [`docs/`](docs/) — numbered notes: coding standards, competition
  instructions, EDA insights, the implementation plan, the experiment
  ledger, the submission manifest, the append-only agent log, and source
  dataset provenance.
- [`scripts/`](scripts/) — `push_kaggle_kernel.sh` (push a notebook to its
  Kaggle kernel), `verify_submission.py` (pre-submission schema checks),
  and `check_frames.py` (proves each experiment's feature frames are
  actually built — added after a missing frame killed a kernel run).
- `data/`, `predictions/` — local and generated, gitignored.

## Conventions

Standards are layered: the shared master standard at
`~/Documents/GitHub/coding-standards/` is the baseline, and
[`docs/0_coding_standards.md`](docs/0_coding_standards.md) holds the
project-specific rules and deliberate overrides.

Agents working here should start from [`AGENTS.md`](AGENTS.md).

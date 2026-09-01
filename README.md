# Predicting Electric Vehicle Purchases

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Playground%20Series%20S6E9-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/playground-series-s6e9)
[![Status](https://img.shields.io/badge/Status-Scaffold-lightgrey)](docs/1_instructions.md)
[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](requirements.txt)

Kaggle Playground Series S6E9:
https://www.kaggle.com/competitions/playground-series-s6e9

Public-notebook-first workflow. Notebooks are the executable source of truth;
`docs/` records rationale, validation, and submission evidence.

## Status

**Scaffold only — no data, no analysis, no results.** The competition has not
been joined yet, so the evaluation metric, target column, and submission format
are all still unknown. See [`docs/1_instructions.md`](docs/1_instructions.md)
for the checklist that has to be filled in first.

Deadline: **2026-09-30 23:59 UTC** (read from the Kaggle API, 2026-09-01).

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

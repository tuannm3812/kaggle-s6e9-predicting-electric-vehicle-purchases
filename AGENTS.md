# kaggle-s6e9-predicting-electric-vehicle-purchases

Kaggle Playground Series S6E9 — predicting electric vehicle purchases. Deadline
**2026-09-30 23:59 UTC**. Notebook-first: the notebooks in `notebooks/` are the
executable source of truth, `docs/` carries the reasoning.

This is a Playground competition, not a research project. Prefer a small number
of well-validated models over breadth.

## Standards

Follow the master standard at `~/Documents/GitHub/coding-standards/`.
Project-specific rules and deliberate overrides: @docs/0_coding_standards.md

## Read before changing anything

@docs/1_instructions.md — and note that most of it is still unfilled. The
competition has not been joined, so the **evaluation metric, target column and
submission format are all unknown**. Do not infer them. Do not write a metric
name into code or docs until it has been read off the Evaluation tab.

## Deltas from the master

- The test set is large (7.7 MB sample submission, likely ~10^6 rows). Measure
  runtime and memory on the first full-data fit before launching any sweep, and
  keep exploratory work on a stated subsample + seed.
- A subsample result and a full-data result never share a row in the ledger.

## Evidence locations

- `docs/1_instructions.md` — task, metric, deadline, submission mechanism
- `docs/N_experiment_ledger.md` — every run and its numbers *(not created yet)*
- `docs/N_submission_manifest.md` — every submission and its decision *(not created yet)*

Any claim about model behaviour should trace to a row in the ledger.

## Open risks

- **Nothing has been verified against the data yet.** No file in this repo has
  seen `train.csv`. Treat every quantitative statement as absent, not implied.
- The competition is new (57 teams as of 2026-09-01), so there is little public
  discussion to calibrate against. Mutable facts — leaderboard standing, public
  notebook approaches, quotas — must be re-checked live, never recalled.

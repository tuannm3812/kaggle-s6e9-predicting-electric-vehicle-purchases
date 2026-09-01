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

@docs/1_instructions.md — the competition was joined and the data verified on
2026-09-01: metric is **ROC AUC**, target is `Will_Buy_EV` (binary Yes/No,
17.46% positive), submission is one probability per test `id`. Quantitative
claims about the data trace to that doc or to `notebooks/01_eda.ipynb`.

## Deltas from the master

- The test set is large (7.7 MB sample submission, likely ~10^6 rows). Measure
  runtime and memory on the first full-data fit before launching any sweep, and
  keep exploratory work on a stated subsample + seed.
- A subsample result and a full-data result never share a row in the ledger.

## Evidence locations

- `docs/1_instructions.md` — task, metric, deadline, submission mechanism
- `docs/2_eda_insights.md` — executed EDA findings
- `docs/3_implementation_plan.md` — phased plan and gates
- `docs/4_experiment_ledger.md` — fold definition (F1), predeclared gates, every run
- `docs/5_submission_manifest.md` — every submission and its decision
- `docs/6_agent_log.md` — append-only session log; start here to catch up

Any claim about model behaviour should trace to a row in the ledger.

## Open risks

- **The original source dataset is unidentified.** The Data tab prose is not
  fetchable by URL and a column-name web search (2026-09-01) found nothing.
  If identified, it may be usable as extra training data — check before the
  final ensemble, not after.
- The competition is new (92 teams as of 2026-09-01), so there is little
  public discussion to calibrate against. Mutable facts — leaderboard
  standing, public notebook approaches, quotas — must be re-checked live,
  never recalled.
- Model-behaviour claims trace to `docs/4_experiment_ledger.md`. The OOF
  plateau is leaderboard-calibrated (public 0.94169 vs. OOF 0.94177,
  2026-09-01): margins near the plateau are ~0.0002 — the paired gate is
  the only defence against promoting noise.

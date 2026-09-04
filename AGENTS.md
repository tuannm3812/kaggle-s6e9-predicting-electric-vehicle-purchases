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

**Comparability classes — the rule that bites most often here.** Results
from different measurement conditions never share a ledger row, and two
of these are enforced in code rather than by convention:

- **Subsample vs. full data.** State the fraction and seed for any
  exploratory run; promote to full data before a candidate counts.
- **CPU vs. GPU.** CatBoost's GPU path is numerically different and not
  bit-reproducible here; GPU is screening-only (measured −0.00070).
- **Fold definition F1 (5-fold) vs. F2 (10-fold).** `paired_gate`
  *asserts* both runs share a definition, `register_average` refuses
  mixed members, and §9 filters promotions to the champion's class. F2
  is the go-forward default for new work (E09).

Measure runtime and memory on the first full-data fit before launching a
sweep: a 5-fold fit now costs ~4,100–5,000 s and a 10-fold fit ~6,100 s.
The test set is 286,571 rows — smaller than the 7.7 MB sample submission
first suggested.

## Evidence locations

- `docs/1_instructions.md` — task, metric, deadline, submission mechanism
- `docs/2_eda_insights.md` — executed EDA findings
- `docs/3_implementation_plan.md` — phased plan and gates
- `docs/4_experiment_ledger.md` — fold definitions (F1, F2), predeclared gates, every run
- `docs/5_submission_manifest.md` — every submission and its decision
- `docs/6_agent_log.md` — append-only session log; start here to catch up
- `docs/7_source_dataset_provenance.md` — the source dataset, its licence, and how it is used

Any claim about model behaviour should trace to a row in the ledger.

## State (2026-09-04)

- **Champion** (paired-OOF gated, class F1): `e08_avg3seeds`, OOF
  0.94550, public **0.94565**.
- **Best public score:** `e09_f2_avg3seeds`, **0.94570** — but it lives in
  class F2 and cannot be gated against an F1 champion, so "champion" and
  "best submission" deliberately name different artifacts.
- E01–E09 complete; 7 submissions; standing 186/699, leader 0.94656.
- **The one big win was E06 (+0.00337):** the "numeric" columns are value
  identities — `Annual_Income_USD` takes 13,214 distinct values, 97.9% of
  them drawn from the source dataset, and the exact value carries label
  information its magnitude does not. Everything before it was ~0.0002 a
  step; everything after it has been ~0.00005 a step.
- **Noise floor is 0.00005**, not the 0.00013 quoted in pre-E06 rows —
  value identities are deterministic, so seed variance collapsed.

## Open risks

- **The approach is at its ceiling.** Every enumerated axis is measured
  and five further free screens (2026-09-04) found nothing. The remaining
  0.0009 to the leader needs a representational idea like E06's; there is
  no candidate. Prefer cheap local diagnostics over speculative kernel
  runs — E06 came from a 30-second column-cardinality check.
- **The source dataset is identified** (`docs/7_source_dataset_provenance.md`)
  and, contrary to E05's null, **is used by the champion as a feature**,
  so its CC0 citation obligation is live.
- Mutable facts — leaderboard standing, public notebook approaches,
  quotas — must be re-checked live, never recalled.
- Model-behaviour claims trace to `docs/4_experiment_ledger.md`. CV↔LB
  tracking holds across six OOF-backed submissions, but the sign flipped
  positive at E06: test predictions are an average of every fold model
  while each OOF row comes from one, so LB > OOF is partly construction,
  not free accuracy.

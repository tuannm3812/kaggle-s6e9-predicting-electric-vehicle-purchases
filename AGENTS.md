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

## State — one line, then pointers (kept short on purpose)

**Search closed 2026-09-05 after E01–E10 plus a bit-identical
reproduction (R1).** Champion `e08_avg3seeds` (public 0.94565, fold class
F1); best submission `e09_f2_avg3seeds` (public **0.94570**, class F2 —
the two names differ deliberately). The one big step was E06's value
identities; the noise floor on that representation is 0.00005.

This block used to carry a full state summary and went stale twice in two
days — the same facts were hand-maintained in five files. It now names
only what is needed to orient: **numbers and model behaviour live in
`docs/4_experiment_ledger.md`; current state and what is open lives in
`docs/3_implementation_plan.md`.** Do not widen this section; update
those two and let this point.

## Open risks

- **The only outstanding action is the final two-submission selection in
  the Kaggle UI** before 2026-09-30 23:59 UTC — recommendation in
  `docs/5_submission_manifest.md`. Search is closed; prefer cheap local
  diagnostics over speculative kernel runs if it ever reopens.
- The source dataset is identified and **used by the champion as a
  feature** — its CC0 citation obligation is live
  (`docs/7_source_dataset_provenance.md`).
- Mutable facts — leaderboard standing, public notebooks, quotas — must
  be re-checked live, never recalled.
- LB has run slightly above OOF since E06 for a mostly mechanical reason
  measured in E08B — see the ledger; keep gating on OOF.

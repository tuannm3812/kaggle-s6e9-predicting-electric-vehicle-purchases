# Implementation Plan

Phased plan for Playground Series S6E9 (Predicting Electric Vehicle
Purchases), written **2026-09-01** against a **2026-09-30 23:59 UTC**
deadline (29 days). Takes methodology from S6E7/S6E8 (fixed folds, OOF-first
validation, hypothesis-gated submissions, predeclared promotion gates) and
S6E8's deliberate scope restraint: a small number of well-validated models,
not model proliferation.

Competition shape (all verified — `docs/1_instructions.md`,
`docs/2_eda_insights.md`): binary target `Will_Buy_EV` (17.46% positive),
ROC AUC, 668,665 train rows, 13 features, **no missing values, no
duplicates, no train/test drift** (adversarial AUC 0.4992). Signal is
top-heavy: `Environmental_Concern_Level`, `Subsidy_Available`,
`Annual_Income_USD` carry nearly all marginal signal, with one big
interaction (the subsidy gate, `docs/2_eda_insights.md` §5).

## Phase 0 — Setup (done 2026-09-01)

- [x] Competition joined; data downloaded and verified against
      `docs/1_instructions.md`.
- [x] Metric verified via Kaggle API: **ROC AUC**. Quotas: 10/day, team ≤ 3,
      file upload permitted (`is_kernels_submissions_only = False`).
- [x] `scripts/verify_submission.py` rewritten for `Will_Buy_EV`; passes on
      `sample_submission.csv`.
- [x] `requirements.txt`, `notebooks/kernels/eda/kernel-metadata.json`.
- [ ] Original source dataset identification (open — see
      `docs/1_instructions.md`).

## Phase 1 — EDA (done 2026-09-01)

`notebooks/01_eda.ipynb` executed end-to-end locally (~21 s). Full findings:
`docs/2_eda_insights.md`. Headlines feeding Phase 2: top-heavy signal,
strictly monotone ordinals, the subsidy gate, no missingness/drift/duplicate
workstreams needed, CV expected to track the leaderboard.

## Phase 2 — Baseline Modeling (`notebooks/02_baseline_modeling.ipynb`) — done 2026-09-01

Executed end-to-end locally (kernel `s6e8-py39`, ~10 min wall-clock, dominated by CatBoost). Results and decisions: `docs/4_experiment_ledger.md`. Working champion `v2b_catboost_default`, OOF AUC 0.94157 ± 0.00072 on F1. Original step list, followed as written:

1. **Validation:** `StratifiedKFold(n_splits=5, shuffle=True,
   random_state=42)` on `Will_Buy_EV` — defined once in
   `docs/4_experiment_ledger.md` (F1) and reused by every comparable model
   so OOF predictions align across candidates.
2. **Runtime measurement first** (scale override,
   `docs/0_coding_standards.md`): wall-clock + peak memory of the first
   full-data fold fit, recorded in the ledger before anything wider runs.
   EDA's 21 s full run suggests this is light, but measured ≠ assumed.
3. **v1 sanity:** constant (prevalence), logistic regression (one-hot +
   scaled; sanity floor, not a candidate), default
   `HistGradientBoostingClassifier`.
4. **v2 strong:** LightGBM and CatBoost with native categorical handling.
   `Range_Anxiety_Level` ordinal-encoded (Low<Medium<High) by default per
   the monotone evidence; treat-as-categorical as a cheap A/B, logged.
5. **Candidate sanity checks:** finite, in `[0,1]`, non-constant
   predictions; per-fold + overall OOF AUC; train/test prediction quantile
   comparison. No thresholded "predicted positive rate" check — AUC makes
   no threshold.
6. Every run — including rejected ones — gets a ledger row.

## Phase 3 — Optimization & Ensemble (evidence-gated, by ~2026-09-20)

Status 2026-09-01: step 1 done (E01 — `e01_cat_2000x05` promoted via
the paired gate, `docs/4_experiment_ledger.md`); step 4 resolved as
**skip Optuna** (predeclared no-headroom condition met). Steps 2/3/5/6
remain gated as written; E02 blend is eligible on diversity.

1. Hand-designed configuration search first (a handful of configs per
   family, comparable boosting budgets), no automated sweeps by default.
2. Explicit interaction features (`Subsidy × Environmental_Concern`,
   `Subsidy × Income`) as an OOF ablation only if v2 plateaus below
   expectation — GBDTs should find the gate natively.
3. XGBoost only if it is wrong on *different rows* (residual/rank
   diversity), not to "have three families".
4. Optuna only if the hand-designed search shows real headroom between
   configs; skip and say so otherwise.
5. Multi-seed averaging only if fold std is non-trivial vs. candidate gaps.
6. Ensemble only past the predeclared diversity bar
   (`docs/4_experiment_ledger.md`): champion-vs-candidate OOF Pearson
   correlation **≤ 0.995**, plus a paired-gate win for the blend. S6E8
   skipped ensembling at 0.9976 correlation — that is the standard.
7. **Promotion gate** (predeclared in the ledger before any comparison
   runs): candidate beats champion on ≥ 3 of 5 aligned folds, paired
   stratified-bootstrap 95% CI on ΔAUC entirely positive, P(Δ>0) ≥ 0.95.

## Phase 4 — Submissions (from first candidate onward)

- `scripts/verify_submission.py` before every artifact leaves the machine.
- Submit via a completed Kaggle kernel version (`kaggle competitions submit
  -k tuannm3812/<kernel> -v <version> -f submission.csv`), never a detached
  local CSV (master standard §11).
- One submission per accepted hypothesis; every submission logged in
  `docs/5_submission_manifest.md` (notebook version, OOF, public score,
  decision) the moment it is scored. Quota is 10/day; the binding
  constraint is discipline, not quota.
- Keep the current champion as a known-good fallback at every step.

## Phase 5 — Final Week (2026-09-24 → 2026-09-30)

1. Freeze features by 2026-09-26; stability and promotion checks only.
2. Re-run the champion notebook end-to-end on Kaggle to confirm
   reproducibility; pin the versions the trusted run actually used.
3. Final submission locked by **2026-09-29** — a day of buffer against a
   failed Kaggle run.
4. Closing README update: result table, what worked, stop-condition
   reasoning.

## Subsample rule (restated from `docs/0_coding_standards.md`)

Exploratory work runs on a stated subsample + seed; candidate runs use full
data; the two never share a ledger row. Given the measured lightness of
this dataset, full-data runs are likely affordable throughout — but that is
decided by the Phase 2 measurement, not assumed.

## Planned Docs

| Doc | Phase | Content |
| --- | --- | --- |
| `2_eda_insights.md` | 1 | done |
| `3_implementation_plan.md` | — | this file |
| `4_experiment_ledger.md` | 2–5 | fold definition, every run, promotion decisions |
| `5_submission_manifest.md` | 4 | every submission, score, decision |
| `6_agent_log.md` | — | append-only agent collaboration log (master §13) |
| `7_source_dataset_provenance.md` | open | only if the source dataset is identified |

## Current state and next moves (internal — 2026-09-02)

Kept here rather than in the notebooks: `notebooks/` is pushed to a
**public** Kaggle kernel, so forward strategy stays in `docs/`. See the
convention in `docs/0_coding_standards.md`.

**Champion:** `e03_cat_int_avg5seeds` — OOF 0.94223, public 0.94210
(submission 3). 3-seed variant (0.94220) is a sanctioned fallback if the
final week needs compute back.

**Closed axes** — each measured, each recorded in
`docs/4_experiment_ledger.md`; re-running any of them is waste:

| Axis | Closed by | Evidence |
| --- | --- | --- |
| Capacity (iterations, depth, leaves) | E01, E02 | every increase scored worse |
| Regularization (l2, random_strength, bagging) | E04 | +0.00001…+0.00002, or −0.00030 |
| Optuna / automated sweep | E01 | no headroom between hand-designed configs |
| Blending | E02, E03 | OOF correlations 0.9958–0.9999, all above the 0.995 bar |
| Seed averaging | E03 | plateaus past 3 seeds (+0.00003 for the 4th and 5th) |
| Subsidy-gate features | E04 | features v2 +0.00003, gate-rejected |
| GPU for champion fitting | E04 | −0.00070 vs CPU; screening only |

**Open with real upside:**

1. **The unidentified source dataset.** Extra training data is the only
   remaining lever that could plausibly move more than 0.0002. The Data
   tab is client-rendered and not fetchable by URL; needs the Dataset
   Description pasted in, or a manual read. If found and license-clear,
   test as extra training rows under the standing paired gate.
2. **Feature ideas grounded in new evidence** — not re-permutations of
   the existing 13 columns, which E02/E04 suggest are mined out.

**If nothing further lands,** the current champion is a defensible final
answer. Final-week work is then reproducibility, not search: re-run the
champion kernel end-to-end, confirm the artifact, pin versions, and lock
the final submission by 2026-09-29 (one day of buffer).

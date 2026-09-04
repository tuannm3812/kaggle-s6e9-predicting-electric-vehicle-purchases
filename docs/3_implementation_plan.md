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

## Phase 3 — Optimization & Ensemble (evidence-gated, by ~2026-09-20) *(complete)*

Status 2026-09-04: complete — E01–E09 all recorded in the ledger; the
ensemble path is closed (every blend measured ≤ +0.00002). Original
status line kept below for the record. Status 2026-09-01: step 1 done (E01 — `e01_cat_2000x05` promoted via
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
| `7_source_dataset_provenance.md` | written 2026-09-02 | the source dataset, its licence, and how it is used |

## Current state and next moves (internal — 2026-09-02)

Kept here rather than in the notebooks: `notebooks/` is pushed to a
**public** Kaggle kernel, so forward strategy stays in `docs/`. See the
convention in `docs/0_coding_standards.md`.

**Champion (2026-09-04):** `e08_avg3seeds` — OOF 0.94550 (class F1),
public **0.94565**. Best public score is `e09_f2_avg3seeds` at
**0.94570**, which sits in class F2 and cannot be gated against an F1
champion; both are candidates for the final two-submission selection.

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
| Source dataset as extra training rows | E05 | +0.00001, CI spans zero, P(Δ>0) 0.627 |
| Capacity, **re-tested post-E06** | E07 | +0.00001 — closed permanently; the representation change did not move its optimum |
| Encoding breadth (low-cardinality numerics as categoricals) | E07 | +0.00004, gate-rejected |
| CTR complexity (`max_ctr_complexity=1`) | E07 | −0.00023; combinations are signal, not noise |
| Seed averaging, **re-tested post-E06** | E08 | +0.00007, below its own predeclared +0.00010 threshold |
| Full-data refit for test predictions | E08B | +0.00004 on LB; below the noise floor, not promoted |
| Fold count 5 → 10 | E09 | +0.00005 on LB; adopted as the go-forward default, not a champion |
| Blending (any partner tried) | E02, E03, free screens | best case +0.00002; partners are ≥0.003 weaker |
| A decorrelated non-CatBoost partner | free screen 2026-09-04 | LightGBM stays 0.0033 behind even with leak-free nested TE |

**Noise floor: 0.00005** on the current representation (was 0.00013
pre-E06). Any pre-E06 row quoting 0.00013 as "the" floor is describing
the old representation.

**E06 reopened these axes, and E07–E09 closed them again.** The pre-E06
nulls were all measured on a representation that discarded the value
identities, so they were re-tested once, deliberately. They did not
flip: capacity is now closed *permanently* (E07), encoding breadth and
CTR complexity are closed (E07), and seed averaging returned +0.00007
rather than E03's +0.00019 — so E03's additivity result does **not**
generalise across representations (E08).

**Open with real upside: nothing.** Five free screens on 2026-09-04
(duplicates, id signal, joint identities, a strong LightGBM partner,
artifact blending) all returned null. See the ledger.

**Agreed sequence (2026-09-03, user directive "all three, sequenced").**
Ordered so that no run's work is invalidated by a later one — E03 proved
seed-averaging additive, so the config is settled *before* it is
averaged:

| Run | Experiment | Why this order |
| --- | --- | --- |
| kernel v10 | **E07** — capacity, full value-ids, CTR complexity (single seed) | Explore first: averaging a config that then changes is wasted compute |
| kernel v11 | **E08** — seed-average E07's winner | Additive gain (+0.00019 measured in E03), applied once the config is final |
| kernel v12/13 | **E09** — 10-fold under a new fold definition **F2** | Motivated by E06's +0.00020 LB>OOF gap: test statistics use all 668k rows, each F1 fold only ~535k. Needs F2 because it breaks comparability with every F1 row; gate F2-vs-F2 only |

**Sequence outcome (2026-09-04):** E07 null, E08 +0.00007 OOF plus a
correction to the LB>OOF explanation, E09 +0.00005 LB. Best submission
`e09_f2_avg3seeds` at public **0.94570**; gated champion `e08_avg3seeds`
at 0.94565. Roughly 20 h of compute for a twentieth of the gap to the
leader — the enumerated axes are exhausted, and the remaining 0.00086
needs a representational idea like E06's, not another tuning pass.
**Find evidence cheaply and locally before predeclaring anything
further.**

**Closed for good by the free screens (2026-09-03):** blending, source
tracing, and target-free derived features — see the ledger.

## Phase 4 — Closing out (2026-09-04 onward)

Search is finished: every enumerated axis is measured and five further
free screens found nothing. What remains is not modelling.

| Task | Status |
| --- | --- |
| Pin dependency versions | **done** — `requirements.txt` pinned to the kernel-v13 environment |
| Record catboost in the reproducibility snapshot | **done** — it produces the champion and was missing |
| Verify the champion's reproduction path still executes | **done** — `check_frames.py` passes for `RUN_E08`; CPU runs have reproduced bit-identically five times |
| Choose the final two submissions | **decided** — see `docs/5_submission_manifest.md`; the action itself is UI-only and still outstanding |
| Select them on Kaggle before 2026-09-30 23:59 UTC | **outstanding — the only hard deadline left** |

**A full re-run purely to re-confirm reproducibility is not planned.** The
CPU pipeline has produced bit-identical OOF vectors across kernel
versions five separate times (E05, E06, E07, E08, E09 baselines), which
is stronger evidence than one more run would add, and it would cost ~4 h
for no new information.

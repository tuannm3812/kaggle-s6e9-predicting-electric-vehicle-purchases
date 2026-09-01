# Experiment Ledger

Every experiment's hypothesis and promotion criteria are written here
**before** its results, per `docs/0_coding_standards.md`. Results are never
edited to fit outcomes; rejected runs stay recorded. A subsample result and
a full-data result never share a row.

## Fold definition

**F1** (defined 2026-09-01, before any model run):
`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` stratified on
`Will_Buy_EV`, applied to `train.csv` in file order (`id` 0..668664). Every
comparable model uses F1 so OOF predictions align row-for-row. Any change of
fold scheme gets a new tag (F2, …) and restarts comparability.

## Predeclared gates (2026-09-01)

- **Working-champion selection (v1/v2 baselines):** highest OOF AUC on F1
  among candidates passing sanity checks (finite, in [0,1], non-constant;
  no single fold driving the result). This selects a *working* champion for
  iteration; it is not a paired-gate promotion.
- **Promotion gate (any later challenger vs. champion):** on aligned F1 OOF
  predictions — (1) challenger wins ≥ 3 of 5 folds, (2) paired stratified
  bootstrap 95% CI of ΔAUC entirely > 0, (3) P(Δ>0) ≥ 0.95. All three must
  hold.
- **Ensemble diversity bar:** blending is considered only if
  champion-vs-candidate OOF Pearson correlation ≤ **0.995**; otherwise
  record the correlation and skip (S6E8 precedent at 0.9976).

## Run log

All rows: full data (no subsample), folds F1, executed locally 2026-09-01 on
kernel `s6e8-py39` (Python 3.9.6, sklearn 1.6.1, lightgbm 4.6.0,
catboost 1.2.10) by `notebooks/02_baseline_modeling.ipynb` (notebook v1).
Fold-level AUCs and the full config of every run are in that notebook's
Reproducibility Snapshot cell.

| Run | Date | Data scope | Model / config | Folds | OOF AUC (mean ± fold std) | Wall-clock | Notes / decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v1a_constant | 2026-09-01 | full | constant = train prevalence | — | 0.500 | <1 s | rankless floor; harness check |
| v1b_logistic | 2026-09-01 | full | one-hot + scaled, `LogisticRegression(max_iter=2000)` | F1 | 0.93809 ± 0.00081 | 5.6 s | sanity floor, excluded from candidacy by predeclaration; solver overflow RuntimeWarnings (as in S6E8) — predictions finite/in-range |
| v1c_hgb_default | 2026-09-01 | full | HGB defaults, native cat, ANX ordinal | F1 | 0.94102 ± 0.00087 | 18.2 s | **first-fit measurement** (scale override): 18.2 s, 0.99 GB peak RSS → full-data CV affordable, no subsample regime needed |
| v2a_lightgbm_default | 2026-09-01 | full | LightGBM defaults (100 trees), native cat, ANX ordinal | F1 | 0.94115 ± 0.00082 | 8.4 s | |
| v2b_catboost_default | 2026-09-01 | full | CatBoost defaults (1000 iter), 5 cat_features, ANX ordinal | F1 | **0.94157 ± 0.00072** | 550.9 s | **working champion** per predeclared highest-OOF rule; +0.00042 over v2a < fold std — not a paired-gate promotion; 65× LightGBM runtime |
| v2c_lightgbm_anx_categorical | 2026-09-01 | full | as v2a, ANX native categorical | F1 | 0.94123 ± 0.00088 | 8.7 s | A/B vs. v2a: Δ +0.00008 ≪ fold std → tie; **ordinal default retained** |

## Decisions (2026-09-01)

- **Working champion: `v2b_catboost_default`** (OOF AUC 0.94157, F1).
  Selection rule was predeclared above; note the margin over LightGBM is
  inside fold noise, and the v2 budgets are not comparable (100 vs. 1000
  trees) — resolving that is E01's job, not a reason to re-litigate v2.
- **Diversity readings** (OOF Pearson): CatBoost–LightGBM **0.9940**,
  CatBoost–HGB **0.9937** → below the 0.995 bar, blend-eligible later.
  LightGBM–HGB 0.9979 and LightGBM–LightGBM(anx cat) 0.9991 → ineligible.
- **Runtime measurement recorded** — the scale override's precondition for
  any future sweep is satisfied.
- **No leaderboard submission made yet.** `notebooks/submission.csv`
  (champion fold-mean, validated by `scripts/verify_submission.py`) is
  ready; submission waits for the kernel-push flow per
  `docs/3_implementation_plan.md` Phase 4.

## E01 — Budget-Matched GBDT Configurations (predeclared, not yet run)

**Hypothesis:** LightGBM given a boosting budget comparable to CatBoost's
defaults (more estimators, lower learning rate) closes or reverses the
+0.00042 gap at a fraction of the runtime; HGB and CatBoost get their own
comparable-budget configs so this is a three-family search, not
LightGBM chasing a frozen number.

**Search space:** a handful of hand-designed configurations per family,
listed in full in the notebook before running; no automated sweeps.

**Promotion criteria:** the predeclared paired gate above, against
`v2b_catboost_default` on aligned F1 OOF predictions. Rejected configs are
recorded here with their numbers.

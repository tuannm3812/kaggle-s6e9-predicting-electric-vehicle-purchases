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

## E01 — Budget-Matched GBDT Configurations (predeclared 2026-09-01, before execution)

**Hypothesis:** LightGBM given a boosting budget comparable to CatBoost's
defaults (more estimators, lower learning rate) closes or reverses the
+0.00042 gap at a fraction of the runtime; HGB and CatBoost get their own
comparable-budget configs so this is a three-family search, not LightGBM
chasing a frozen number.

**Configurations (frozen before any E01 run; nothing added or dropped
afterwards):**

| Config | Family | Parameters (beyond family defaults + seed 42) |
| --- | --- | --- |
| `e01_hgb_1000x05` | HGB | `max_iter=1000, learning_rate=0.05, early_stopping=False` |
| `e01_hgb_2000x03_63l` | HGB | `max_iter=2000, learning_rate=0.03, max_leaf_nodes=63, early_stopping=False` |
| `e01_lgbm_1000x05` | LightGBM | `n_estimators=1000, learning_rate=0.05` |
| `e01_lgbm_2000x03_63l` | LightGBM | `n_estimators=2000, learning_rate=0.03, num_leaves=63, min_child_samples=50` |
| `e01_lgbm_1000x05_127l` | LightGBM | `n_estimators=1000, learning_rate=0.05, num_leaves=127, min_child_samples=100, colsample_bytree=0.8` |
| `e01_cat_2000x05` | CatBoost | `iterations=2000, learning_rate=0.05` |
| `e01_cat_1000x10_d8` | CatBoost | `iterations=1000, learning_rate=0.1, depth=8` |

All on full data, folds F1, ANX ordinal, native categoricals — identical to
the v2 pipeline.

**Promotion criteria (the predeclared paired gate above, applied against
`v2b_catboost_default` on aligned F1 OOF predictions):** fold wins ≥ 3/5,
paired stratified bootstrap (B = 1000, resampling within class, seed 42)
95% CI of ΔAUC entirely > 0, and P(Δ>0) ≥ 0.95. The bootstrap is computed
for every config whose overall OOF AUC exceeds the champion's point
estimate; configs below it are recorded as not-promoted on the point
estimate alone (running a bootstrap that cannot promote is waste). Every
config's numbers are recorded here either way.

*(results pending — notebook v2 execution)*

### E01 results (executed locally 2026-09-01, pre-directive; notebook v2)

Full data, folds F1, kernel `s6e8-py39`. **Wall-clocks are
contention-inflated** (concurrent jobs shared the machine) — upper bounds,
not benchmarks. Total run ≈ 2 h 46 m.

| Run | OOF AUC (mean ± fold std) | Wall-clock | Note |
| --- | --- | --- | --- |
| `e01_cat_2000x05` | **0.94176 ± 0.00074** | 1152 s | **promoted — new champion** |
| `e01_lgbm_1000x05` | 0.94155 ± 0.00079 | 2825 s | best LightGBM; below champion point estimate |
| `e01_hgb_1000x05` | 0.94145 ± 0.00069 | 280 s | best HGB |
| `e01_cat_1000x10_d8` | 0.94113 ± 0.00071 | 3979 s | deeper+faster lr hurt |
| `e01_lgbm_2000x03_63l` | 0.94109 ± 0.00071 | 218 s | |
| `e01_hgb_2000x03_63l` | 0.94100 ± 0.00067 | 496 s | |
| `e01_lgbm_1000x05_127l` | 0.94071 ± 0.00071 | 220 s | most capacity, worst E01 score |

**Paired gate** (only config above the champion point estimate):
`e01_cat_2000x05` vs. `v2b_catboost_default` — fold wins **5/5**
(per-fold Δ +0.000133…+0.000243), paired bootstrap 95% CI
**(+0.000145, +0.000239)** entirely positive, P(Δ>0) **1.000** →
**promoted** under the predeclared gate.

### Decisions (2026-09-01, post-E01)

- **Champion: `e01_cat_2000x05`** (OOF AUC 0.94176). First promotion to
  clear the paired gate; provably predeclared (config freeze commit
  `3acae15` precedes this results commit).
- **Optuna: skipped** per the plan's predeclared condition — the seven
  hand-designed configs span 0.94071–0.94176 and every capacity increase
  scored worse than its smaller sibling; no evidenced headroom.
- **Diversity (aligned OOF Pearson vs. new champion):**
  `e01_lgbm_1000x05` **0.9964**, `e01_hgb_1000x05` **0.9963**,
  `v2a_lightgbm_default` **0.9961** — all above the 0.995 bar, so **no
  blend is attempted** (predeclared; S6E8 precedent). The earlier 0.9940
  reading was against the superseded default-CatBoost champion.
- Per the execution directive, E02 onward runs on Kaggle; these E01 rows
  are the last local ones.


## E02 — Champion Improvement Candidates (predeclared 2026-09-02, before execution)

Runs on Kaggle (execution rule, `docs/0_coding_standards.md`), notebook v3.
Baseline for every comparison: `e01_cat_2000x05` re-fit **in the same
kernel run** (cross-environment OOF deltas are 5th-decimal noise, so the
gate always compares within-run vectors). Folds stay F1 — the fold seed
(42) never varies; only model seeds do where stated.

**Candidates (frozen; nothing added or dropped afterwards):**

| Candidate | Config | Hypothesis |
| --- | --- | --- |
| `e02_cat_interactions` | champion config + 3 subsidy crosses | explicit gate features improve split allocation beyond what CatBoost finds natively (EDA §5) |
| `e02_cat_avg3seeds` | champion config averaged over model seeds {42, 7, 2026} (components `e02_cat_s7`, `e02_cat_s2026`; seed-42 member is the champion re-fit) | seed-variance reduction lifts OOF AUC; plan's multi-seed condition is met (fold std ~0.0007 >> candidate gaps ~0.0002) |
| `e02_cat_3000x035` | CatBoost `iterations=3000, learning_rate=0.035` | E01's winning direction (more budget, lower lr) has remaining headroom |
| `e02_lgbm_1000x05_interactions` | LightGBM 1000×0.05 + the same 3 crosses | cheap family check of the interaction hypothesis |

**Interaction features (frozen, target-free, identical on train/test):**
with `sub = 1[Subsidy_Available = Yes]`, `hc = 1[Home_Charging_Possible = Yes]`:
`Subsidy_x_EnvConcern = sub × Environmental_Concern_Level`,
`Subsidy_x_Income = sub × Annual_Income_USD`,
`Subsidy_x_HomeCharging = sub × hc`.

**Promotion criteria:** the standing paired gate vs. the in-run champion
re-fit (fold wins ≥ 3/5; paired stratified bootstrap B=1000, seed 42, 95%
CI of ΔAUC entirely > 0; P(Δ>0) ≥ 0.95). Bootstrap only for candidates
above the champion point estimate; seed components (`e02_cat_s*`) are not
candidates themselves. **Submission only if something promotes** — a
non-promotion is recorded here and produces no submission.

*(results pending — notebook v3 kernel run)*

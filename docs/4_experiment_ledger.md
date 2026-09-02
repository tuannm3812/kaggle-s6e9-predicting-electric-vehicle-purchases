# Experiment Ledger

Every experiment's hypothesis and promotion criteria are written here
**before** its results, per `docs/0_coding_standards.md`. Results are never
edited to fit outcomes; rejected runs stay recorded. A subsample result and
a full-data result never share a row.

## Device comparability

Every run row states its device. **CPU and GPU results never share a
comparability class** (CatBoost GPU differs numerically from CPU — see
`docs/0_coding_standards.md`). Gates stay valid across the boundary only
because the champion is re-fit in-run; a GPU candidate is never compared
to a CPU champion number. All rows through E03 are **CPU**.

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

### E02 results (Kaggle kernel v3, COMPLETE 2026-09-02 ~05:26 local)

First experiment fully under the Kaggle-only rule — wall-clocks are clean
worker numbers. Champion re-fit in-run: `e01_cat_2000x05` OOF 0.94177
± 0.00073 (3352 s), matching the v2 run to the 5th decimal.

| Run | OOF AUC (mean ± fold std) | Wall-clock | Note |
| --- | --- | --- | --- |
| `e02_cat_interactions` | **0.94204 ± 0.00074** | 3419 s | **promoted — new champion** |
| `e02_cat_avg3seeds` | 0.94193 ± 0.00075 | 10078 s (3 members) | promoted, superseded by higher-OOF promotion |
| `e02_lgbm_1000x05_interactions` | 0.94182 ± 0.00089 | 201 s | **rejected** by gate |
| `e02_cat_s2026` | 0.94181 ± 0.00072 | 3368 s | seed component, not a candidate |
| `e02_cat_s7` | 0.94180 ± 0.00076 | 3358 s | seed component, not a candidate |
| `e02_cat_3000x035` | 0.94177 ± 0.00074 | 5026 s | tied champion — budget direction exhausted |

**Paired gate** (three point-estimate challengers):

| Candidate | Fold wins | 95% CI (ΔAUC) | P(Δ>0) | Verdict |
| --- | --- | --- | --- | --- |
| `e02_cat_interactions` | 5/5 | (+0.000209, +0.000317) | 1.000 | **promoted** |
| `e02_cat_avg3seeds` | 5/5 | (+0.000122, +0.000182) | 1.000 | promoted |
| `e02_lgbm_1000x05_interactions` | 3/5 | (−0.000032, +0.000132) | 0.894 | rejected |

### Decisions (2026-09-02, post-E02)

- **Champion: `e02_cat_interactions`** (OOF AUC 0.94204) — highest-OOF
  promotion per the predeclared selection rule. The interaction effect
  **replicated on LightGBM** (0.94155 → 0.94182), evidence it is the
  features, not seed noise — even though the LightGBM variant itself did
  not clear the gate.
- **Budget direction closed:** 3000×0.035 tied the champion exactly.
- **Diversity vs. new champion** (aligned OOF Pearson, kernel-v3
  matrices): `e02_cat_avg3seeds` 0.9986, `e02_lgbm_1000x05_interactions`
  0.9963, `e01_cat_2000x05` 0.9985 — all above the 0.995 bar →
  **blending stays closed**.
- **E03 candidate flagged (not yet predeclared):** interactions + 3-seed
  averaging of the interaction config; hypothesis of approximately
  additive gains. Requires its own frozen predeclaration before any run.


## E03 — Combining the Two Promoted Effects (predeclared 2026-09-02, before execution)

Kaggle kernel v4, notebook v4. Baseline for the gate: the standing champion
`e02_cat_interactions` **re-fit in the same run** (its seed-42 fit doubles
as a seed-average member, so no fit is wasted).

**Hypothesis:** E02 promoted interactions (+0.00027) and 3-seed averaging
(+0.00016) *independently* against the same baseline. They act on different
error sources — features vs. seed variance — so their gains should be
approximately additive: predicted OOF ≈ 0.94220 (champion 0.94204 +
~0.00016), i.e. beating the champion by roughly the averaging effect alone.
A materially smaller gain means the two effects overlap; a null means
averaging does not transfer to the interaction config.

**Candidates (frozen; nothing added or dropped afterwards):**

| Candidate | Config | Members |
| --- | --- | --- |
| `e03_cat_int_avg3seeds` | interaction features, champion config, averaged over model seeds {42, 7, 2026} | `e02_cat_interactions` (re-fit, seed 42) + `e03_cat_int_s7` + `e03_cat_int_s2026` |
| `e03_cat_int_avg5seeds` | same, seeds {42, 7, 2026, 13, 99} | the three above + `e03_cat_int_s13` + `e03_cat_int_s99` |

The 5-seed variant tests whether averaging gains keep accruing past three
seeds or plateau; both are evaluated against the same re-fit champion.
Seed components (`e03_cat_int_s*`) are **not** candidates themselves.

**Promotion criteria:** the standing paired gate vs. the in-run champion
re-fit (fold wins ≥ 3/5; paired stratified bootstrap B=1000, seed 42, 95%
CI of ΔAUC entirely > 0; P(Δ>0) ≥ 0.95). Bootstrap only for candidates
above the champion point estimate. **Submission only on promotion**, and if
both promote, the predeclared highest-OOF rule selects between them.

**Cost note:** each CatBoost fit is ~3400 s on the Kaggle worker, so this
run is ~5 fits ≈ 4.7 h plus the re-fit. Predeclared as acceptable for a
run that decides whether seed-averaging enters the final champion.

### E03 results (Kaggle kernel v4, COMPLETE 2026-09-02 ~12:01 local, **CPU**)

In-run champion re-fit: `e02_cat_interactions` OOF 0.94204 ± 0.00074
(3018 s), matching kernel v3 exactly — the seed-42 fit doubles as an
average member, so five fits covered both candidates.

| Run | OOF AUC (mean ± fold std) | Wall-clock | Note |
| --- | --- | --- | --- |
| `e03_cat_int_avg5seeds` | **0.94223 ± 0.00075** | 14570 s (5 members) | **promoted — new champion** |
| `e03_cat_int_avg3seeds` | 0.94220 ± 0.00074 | 8807 s (3 members) | promoted; **matches the predeclared prediction exactly** |
| `e03_cat_int_s99` | 0.94209 ± 0.00073 | 2931 s | seed component |
| `e03_cat_int_s2026` | 0.94207 ± 0.00071 | 2858 s | seed component |
| `e03_cat_int_s7` | 0.94205 ± 0.00075 | 2931 s | seed component |
| `e02_cat_interactions` (re-fit) | 0.94204 ± 0.00074 | 3018 s | gate baseline, also seed-42 member |
| `e03_cat_int_s13` | 0.94196 ± 0.00081 | 2833 s | seed component |

**Paired gate:**

| Candidate | Fold wins | 95% CI (ΔAUC) | P(Δ>0) | Verdict |
| --- | --- | --- | --- | --- |
| `e03_cat_int_avg5seeds` | 5/5 | (+0.000155, +0.000227) | 1.000 | **promoted** |
| `e03_cat_int_avg3seeds` | 5/5 | (+0.000134, +0.000199) | 1.000 | promoted, lower OOF |

### Decisions (2026-09-02, post-E03)

- **Hypothesis confirmed exactly.** The predeclaration predicted OOF
  ≈ 0.94220 if interactions and seed-averaging are additive; the 3-seed
  average returned **0.94220**. The effects address different error
  sources and compose without overlap. This is the strongest form of
  evidence this project has produced: a number named before the run.
- **Champion: `e03_cat_int_avg5seeds`** (0.94223) by the predeclared
  highest-OOF rule — **but the 5th seed bought +0.00003 for +5763 s**.
  The 3-seed variant is the better compute trade and is a sanctioned
  fallback if the final week needs the budget; recorded here so that
  choice needs no re-litigation.
- **Averaging plateaus past three seeds** — the question the 5-seed
  variant existed to answer, now answered.
- **Single-seed spread of one config: 0.94196–0.94209 (0.00013).** This
  is the noise floor for single-seed comparisons; smaller "gains" mean
  nothing without the paired gate.
- **Diversity:** 0.9999 (avg3), 0.9992 (single-seed) — nested
  averages of one config, far above 0.995 → blending stays closed.
- **All cheap levers are now exhausted** (budget, Optuna, blending,
  averaging, the one EDA-supported feature idea). Further gains need a
  new feature hypothesis or more compute → E04 goes to GPU.


## E04 — GPU Calibration + Regularization & Feature-v2 Search (predeclared 2026-09-02, before execution)

Kaggle kernel v5, notebook v5, **GPU** (`task_type="GPU"`). First GPU run,
so it is its own comparability class (`docs/0_coding_standards.md`): every
comparison below is GPU-vs-GPU within this run.

**Why these axes.** E01/E02 searched *capacity* (iterations, learning rate,
depth, leaves) and every increase scored worse — recorded then as "the
plateau is regularization-side, not capacity-starved". Regularization
(`l2_leaf_reg`, `random_strength`, `bagging_temperature`) has never been
varied: it is the one model axis with a documented reason to expect
headroom. Separately, EDA §6 observed charging-station counts are flat
marginally but was never converted into *conditional* features; feature-v2
tests that directly.

**Feature set v2** (frozen; v1 = the three champion subsidy crosses):
v1 plus `Anxiety_x_Subsidy = (2 − anx_ordinal) × sub`,
`EnvConcern_x_Income = Environmental_Concern_Level × Annual_Income_USD`,
`Total_Stations = home + work stations`, and
`Stations_x_NoHomeCharging = Total_Stations × (1 − hc)` — the EDA §6
hypothesis that public charging matters when home charging is absent.

**Stage 1 — single-seed GPU candidates** (baseline
`e04_gpu_base` = champion config + features v1, seed 42, GPU):

| Candidate | Change from baseline |
| --- | --- |
| `e04_gpu_l2_10` | `l2_leaf_reg=10` (default 3) |
| `e04_gpu_l2_30` | `l2_leaf_reg=30` |
| `e04_gpu_rs2_bag2` | `random_strength=2, bagging_temperature=2` |
| `e04_gpu_featv2` | features v2, otherwise baseline |

**Stage 2 — averaging, selection rule predeclared:** the highest-OOF
stage-1 candidate **that beats `e04_gpu_base`** is averaged over seeds
{42, 7, 2026} as `e04_gpu_best_avg3`; the baseline is averaged over the
same seeds as `e04_gpu_base_avg3`. If no stage-1 candidate beats the
baseline, stage 2 is skipped and E04 records a null result.

**Promotion criteria:** the standing paired gate, `e04_gpu_best_avg3` vs.
`e04_gpu_base_avg3` (both GPU, both 3-seed). Clearing it makes the new
config the champion **configuration**; because the standing champion
(`e03_cat_int_avg5seeds`, 0.94223) is CPU and 5-seed, the submission
artifact comes from the GPU 3-seed winner only if it also **exceeds the
standing champion's OOF**, which is recorded as a cross-device
observation, not a paired-gate claim. Otherwise the CPU champion stands
and E04 reports configuration evidence only.

**Runtime guard (predeclared):** the calibration fit reports GPU
wall-clock. If it exceeds **900 s**, stage 2 is skipped automatically
(kernel time limit protection) and E04 returns stage-1 evidence only.

**Cross-device calibration:** `e04_gpu_base` is the same configuration as
CPU `e02_cat_interactions` (0.94204). Their difference measures the
GPU-vs-CPU numerical delta — the first such measurement in this project,
and the reason the calibration fit exists.

*(results pending — notebook v5 kernel run)*

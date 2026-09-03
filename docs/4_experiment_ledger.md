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

### E04 results (Kaggle kernel v5, COMPLETE 2026-09-02 ~14:53 local, **GPU**)

**Null result on both hypotheses, plus two facts worth more than the
hypotheses were.**

| Run | OOF AUC (mean ± fold std) | Wall-clock | Note |
| --- | --- | --- | --- |
| `e04_gpu_best_avg3` (= featv2 ×3 seeds) | 0.94150 ± 0.00074 | 945 s | **rejected by gate** |
| `e04_gpu_base_avg3` | 0.94149 ± 0.00076 | 969 s | gate baseline |
| `e04_gpu_featv2` | 0.94137 ± 0.00074 | 315 s | stage-1 winner, +0.00003 over base — below noise |
| `e04_gpu_l2_30` | 0.94136 ± 0.00078 | 313 s | +0.00002 — null |
| `e04_gpu_l2_10` | 0.94135 ± 0.00076 | 314 s | +0.00001 — null |
| `e04_gpu_base` | 0.94134 ± 0.00077 | **341 s** | calibration + gate baseline |
| `e04_gpu_rs2_bag2` | 0.94104 ± 0.00080 | 314 s | −0.00030 — actively worse |

**Gate:** `e04_gpu_best_avg3` vs. `e04_gpu_base_avg3` — 4/5 folds, 95% CI
**(−0.000034, +0.000051)** spanning zero, P(Δ>0) = 0.648 → **not
promoted**. No submission written; `e03_cat_int_avg5seeds` stands.

### Finding 1 — GPU is 8.9× faster and measurably *less accurate*

Same configuration, same folds: **GPU 0.94134 vs. CPU 0.94204 = −0.00070**,
at 341 s vs. 3018 s. The deficit is **5.4× the single-seed noise floor**
(0.00013) — not noise, a systematic device difference (GPU
`border_count` 128 vs. CPU 254, and differing split algorithms).

Operational consequence, now measured rather than assumed:

- **GPU is a screening tool, not a champion-fitting tool** in this
  project. Use it to explore many configurations cheaply; re-fit anything
  promising on CPU before it can become a champion or a submission.
- −0.00070 is larger than every gain this project has won *combined*
  (E01+E02+E03 ≈ +0.00046 OOF). A GPU champion would have thrown away
  more than the whole search had earned.
- The predeclared cross-device rule did its job: the run compared
  GPU-vs-GPU throughout and refused to submit.

### Finding 2 — the "regularization-side plateau" claim is falsified

E02's insight cell speculated that "the plateau is regularization-side,
not capacity-starved". E04 tested that directly: `l2_leaf_reg` 10 and 30
moved OOF by +0.00001/+0.00002 (below the 0.00013 noise floor), and
`random_strength`/`bagging_temperature` **hurt** by 0.00030. Neither
capacity (E01/E02) nor regularization (E04) has headroom — **the model
axis is exhausted**, and the earlier speculation was wrong. It was an
untested claim in an insight cell; it is now a tested and rejected one.

### Finding 3 — features v2 add nothing

The EDA §6 hypothesis (`Stations_x_NoHomeCharging` — public charging
should matter when home charging is absent), plus anxiety/income crosses,
moved OOF +0.00003 and failed the gate. The subsidy-gate feature space
appears exhausted: E02's three crosses captured what was there.

*Caveat, stated rather than hidden:* these feature results were measured
on GPU, whose coarser binning could in principle mask a small feature
effect. Given the effect size (+0.00003, ~4× below the noise floor) a CPU
re-test would cost ~5 h to chase a signal with no positive evidence
behind it — recorded as an option, not a recommendation.

### Finding 4 — GPU runs are not bit-reproducible (observed on the v7 re-run)

Kernel v7 re-ran E04's identical code, seeds and folds (the republish that
carried the notebook restructure). The **verdict was stable** — nothing
promoted, no submission — but the numbers moved in the 5th decimal:

| Quantity | Kernel v5 | Kernel v7 |
| --- | --- | --- |
| `e04_gpu_base` OOF | 0.94134 | 0.94133 |
| `e04_gpu_featv2` OOF | 0.94137 | 0.94138 |
| Gate 95% CI | (−0.000034, +0.000051) | (−0.000018, +0.000069) |
| Gate P(Δ>0) | 0.648 | **0.879** |

CatBoost GPU is not deterministic run-to-run even with fixed seeds. Two
consequences:

- **Reproducibility claims about GPU runs must be qualified.** A CPU run
  of this project reproduces exactly (kernel v4's champion re-fit matched
  v3 to the 5th decimal); a GPU run does not.
- **P(Δ>0) swung 0.648 → 0.879 on identical inputs** — most of the way to
  the 0.95 threshold. A single GPU run near a gate boundary is not
  trustworthy evidence on its own; had the point estimate been slightly
  larger, run-to-run noise alone could have flipped a promotion. This is
  a second, independent reason GPU stays screening-only, and it is why
  the gate's *conclusion* (not its intermediate statistics) is what gets
  recorded as evidence.

### Decisions (2026-09-02, post-E04)

- **Champion unchanged:** `e03_cat_int_avg5seeds` (OOF 0.94223, public
  0.94210). E04 produced no submission, as predeclared.
- **GPU reclassified** from "the lever that makes bigger searches
  affordable" to "screening only, CPU re-fit required" — see
  `docs/0_coding_standards.md`.
- **Closed axes now:** capacity, regularization, blending, averaging
  (past 3 seeds), subsidy-gate features, Optuna. A hyperparameter sweep
  would be searching an axis measured flat twice.
- **What remains genuinely open:** the unidentified source dataset (extra
  training data is the only lever left that could move more than
  0.0002), and any feature idea grounded in *new* evidence rather than
  re-permuting the existing columns.


## E05 — Does the Source Dataset Help? (predeclared 2026-09-02, before execution)

Kaggle kernel v8, notebook v6, **CPU** (GPU is screening-only and
unreliable near gate boundaries — E04 Findings 1 and 4).

**Context:** the source dataset is identified and CC0
(`docs/7_source_dataset_provenance.md`). It adds ~9.5k usable rows to
668,665 — **1.4%** — and is itself synthetic, so the usual "real data
beats generated data" argument does not apply. **The honest prior is that
this does nothing**; it is tested because it is the last untested lever
and costs two fits, not because it is expected to win.

**Design (leakage-safe):** source rows are appended to the **training
portion of each fold only**. Validation folds stay pure competition data,
so OOF remains measured on the competition distribution and stays
comparable to every prior row. Rows with missing values are dropped
(predeclared as 9,478 of 10,000; the run measured 9,466 — see Finding 2) to keep the no-missing regime the test set has.

| Run | Description |
| --- | --- |
| `e05_cpu_base` | champion config + features v1, seed 42, competition data only — in-run gate baseline (expected ≈ 0.94204, matching `e02_cat_interactions`) |
| `e05_cpu_plus_source` | identical, with the usable source rows added to each training fold |

**Promotion criteria:** the standing paired gate, `e05_cpu_plus_source`
vs. `e05_cpu_base`, both single-seed CPU. This is a **screen**, not a
championship bid: the standing champion is a 5-seed average, so clearing
this gate would justify an averaged follow-up (E06), not an immediate
submission. **No submission from E05 regardless of outcome.**

**Falsifiable prediction, stated before the run:** the delta will be
below the measured single-seed noise floor of 0.00013, i.e. this fails to
promote. If it promotes, the prior above was wrong and E06 follows.

### Results (Kaggle kernel v8, notebook v6, CPU, full data, F1 folds)

| Run | OOF AUC | fold std | Folds | Wall | Peak RSS |
| --- | --- | --- | --- | --- | --- |
| `e05_cpu_base` | 0.94204 | 0.00074 | 0.94087 / 0.94172 / 0.94304 / 0.94257 / 0.94201 | 3,475 s | 1.71 GB |
| `e05_cpu_plus_source` | 0.94205 | 0.00079 | 0.94077 / 0.94177 / 0.94313 / 0.94252 / 0.94207 | 3,538 s | 1.77 GB |

**Paired gate** (`e05_cpu_plus_source` vs `e05_cpu_base`): fold Δ =
−0.00010 / +0.00005 / +0.00009 / −0.00005 / +0.00006 → **3/5 fold wins**,
**95% CI (−0.000049, +0.000073)**, **P(Δ>0) = 0.627** → **not promoted**.
OOF Pearson between the two runs 0.9977, above the 0.995 diversity bar,
so there is no blend to consider either.

**Findings**

1. **The prediction held.** Δ = +0.00001, well inside the 0.00013 noise
   floor. Adding 1.4% synthetic rows from a synthetic source teaches the
   model nothing it had not already learned from 668k rows. The lever is
   closed.
2. **Row count correction.** The run reported **9,466** usable source
   rows (534 of 10,000 dropped), not the 9,478 predeclared. The
   predeclared figure came from a local count with a different
   missing-value rule; the kernel figure is authoritative. Twelve rows
   cannot change a 0.00001 result, but the discrepancy is recorded rather
   than silently overwritten.
3. **Free reproducibility check.** `e05_cpu_base` is the champion config
   on features v1, seed 42, CPU — the same fit as `e02_cat_interactions`
   from kernel v4. Their OOF vectors correlate at **1.0000** and the AUC
   matches to five decimals (0.94204). The CPU pipeline is
   bit-reproducible across kernel versions, which is the property E04
   showed the GPU pipeline lacks.
4. **No submission written**, as predeclared; the run's `SUBMIT_OK`
   path was exercised by the "champion not fit in this run" branch.

### Decisions (2026-09-02, post-E05)

- **Champion unchanged:** `e03_cat_int_avg5seeds` (OOF 0.94223, public
  0.94210).
- **Source dataset closed** as a training lever. It stays useful only as
  provenance (`docs/7_source_dataset_provenance.md`).
- **Every predeclared lever is now measured.** What remains is either a
  genuinely new model family (decorrelated enough to clear the 0.995
  blend bar — nothing tried so far has been) or a change to *how* the
  champion is fit rather than *what* it is fit on. Both must be
  predeclared as E06 with a falsifiable prediction before any run.



## E06 — Value Identity: Exact Numeric Values as Categoricals (predeclared 2026-09-03, before execution)

Kaggle kernel v9, notebook v7, **CPU**, full data, F1 folds.

**Evidence that motivated it** (local diagnostics, 2026-09-03, no model
fitting — recorded in `docs/2_eda_insights.md` §10):

1. The "numeric" columns are discrete. `Annual_Income_USD` has 13,214
   distinct values in 668,665 rows; **492 values each occur ≥200 times
   and together cover 32% of rows**, and `30000` alone covers 9.2%.
   `Daily_Commute_km` has 805 values, with `5.0` on 21.6% of rows.
2. **97.9% of train income values are values in the 8,915-income source
   dataset**, and every frequent train income is a source income that
   appears 2–3 times there. The generator sampled income from the
   source's values, so the exact value identifies a source row.
3. The identity carries label information the magnitude does not. An
   out-of-fold (F1) target encoding of the *exact* income value scores
   **AUC 0.7072** univariate vs **0.6812** for 100 quantile bins; e.g.
   income 72,441 has a 3.6% purchase rate inside a bin averaging 12.4%.
   For the 506k rows whose income maps to a unique source row, the
   purchase rate is **26.1% when that source row is `Yes` vs 17.6% when
   `No`**.
4. The champion cannot see this: CatBoost quantizes numerics to 254
   borders, so one value among 13k is never isolated.
5. Incremental estimate over the champion, by a 5-fold CV'd logistic
   stack on the champion's OOF logit: **+0.00089** for the income
   encoding, +0.00096 with commute added, +0.00011 for a source-label
   lookup alone, **+0.00134** for all three. Caveat: a stack that reuses
   the same folds as its inputs carries a mild second-level leak, so
   these are upper-ish estimates, not predictions.

**Design.** Features v3 = v1 (interactions) plus string copies of
`Annual_Income_USD` and `Daily_Commute_km` (`Annual_Income_USD_id`,
`Daily_Commute_km_id`) passed to CatBoost as categoricals. CatBoost's
ordered target statistics are computed inside each training fold, so
this is leakage-safe by construction; validation folds see only the
prior for values absent from their training fold, exactly as test rows
will (0.58% of test incomes are unseen in train). The numeric columns
are kept. One arm adds a source-dataset lookup: for each row, the mean
label and count of source rows sharing its income (−1 / 0 when none) —
this uses the source's labels only, never the competition target, so it
needs no fold handling.

| Run | Description |
| --- | --- |
| `e06_cpu_base` | champion config, features v1, seed 42 — in-run gate baseline (expected 0.94204 exactly; CPU is bit-reproducible, E05 Finding 3) |
| `e06_cat_value_ids` | identical, features v3 |
| `e06_cat_value_ids_src` | features v3 + source income lookup (`Src_Income_Rate`, `Src_Income_N`) |

**Promotion criteria:** the standing paired gate, each candidate vs.
`e06_cpu_base`, single-seed CPU. Because the standing champion is a
5-seed average at 0.94223, a promoted candidate takes the submission
slot **only if its OOF also exceeds 0.94223** — otherwise the run is
evidence-only and a seed-averaged follow-up decides. This rule is now
enforced in code (`STANDING_CHAMPION_OOF`, §9), not by a printed note.
Between the two candidates, the higher OOF is submitted; their
difference is recorded as an observation, not gated.

**Falsifiable predictions, stated before the run:**

- `e06_cat_value_ids` beats `e06_cpu_base` by **at least +0.0005**
  (≈4× the noise floor) and clears the gate with 5/5 folds. If the delta
  is below +0.00026 (2× noise floor), the value-identity hypothesis is
  wrong *as a CatBoost feature* and the stack estimate was leak-inflated.
- `e06_cat_value_ids_src` is within ±0.0002 of `e06_cat_value_ids`: the
  source lookup is mostly redundant with the in-fold target statistics on
  the same key.
- Wall-clock rises to roughly 1.3× the baseline fit (high-cardinality
  CTRs), i.e. ~75 min per candidate; the whole run stays under 4 h.

### Results (Kaggle kernel v9, notebook v7, CPU, full data, F1 folds)

| Run | OOF AUC | fold std | Folds | Wall | Peak RSS |
| --- | --- | --- | --- | --- | --- |
| `e06_cpu_base` | 0.94204 | 0.00074 | 0.94087 / 0.94172 / 0.94304 / 0.94257 / 0.94201 | 2,656 s | 1.99 GB |
| `e06_cat_value_ids` | **0.94541** | 0.00066 | 0.94443 / 0.94512 / 0.94646 / 0.94560 / 0.94545 | 3,927 s | 2.56 GB |
| `e06_cat_value_ids_src` | **0.94542** | 0.00062 | 0.94453 / 0.94514 / 0.94643 / 0.94561 / 0.94545 | 3,958 s | 2.59 GB |

**Paired gate vs. `e06_cpu_base`:** both candidates **5/5 fold wins**,
P(Δ>0) = 1.000 — `e06_cat_value_ids` CI (+0.003236, +0.003510),
`e06_cat_value_ids_src` CI (+0.003248, +0.003530). **Both promoted.**

**Independently re-run against the standing champion**
`e03_cat_int_avg5seeds` (0.94223), outside the notebook, from the saved
matrices: `e06_cat_value_ids` **+0.00318**, 5/5 folds, 95% CI
(+0.003047, +0.003315), P(Δ>0) = 1.000. The promotion does not rest on
the in-run single-seed baseline alone.

**Findings**

1. **The hypothesis held, by a margin larger than the entire search
   before it.** +0.00337 over the in-run baseline, **~26× the 0.00013
   noise floor**, against a predeclared threshold of ≥+0.0005. Every
   accepted step from v1 to E03 totalled +0.00066; this single feature is
   five times that.
2. **The source lookup is redundant, as predicted.** `_src` beats
   `value_ids` by **+0.000018** — 3/5 folds, CI (−0.000012, +0.000050),
   P(Δ>0) = 0.871. The predeclared band was ±0.0002; the observed
   difference is an order of magnitude inside it. CatBoost's in-fold
   target statistics on the same key already extract what the source
   labels carry, so **the external dataset adds nothing** beyond what
   the competition data itself encodes.
3. **The gain is broad, not memorization.** By the train frequency of a
   row's income value: 6–20 **+0.01816** (2.1% of rows), 21–100
   **+0.00422** (29.1%), 101–1000 **+0.00224** (57.5%), >1000 +0.00032
   (9.7%). Only singleton values (freq = 1, 0.6% of rows) are *worse*,
   −0.00199 — the expected noisy-statistic case. Test's frequency
   profile matches train's almost exactly (29.4% / 57.1% / 9.7%), with
   0.58% unseen and 0.39% singleton, so ~1% of test rows sit in the
   unfavourable zone.
4. **Distributions agree**, guarding against a train/test feature
   mismatch: OOF vs test prediction quantiles match to 3–4 decimals at
   q01/q25/q50/q75/q99, means 0.17450 vs 0.17452 against a 0.17465 base
   rate.
5. **Wall-clock prediction missed slightly:** candidates ran 1.48× the
   baseline, not the predicted 1.3× (high-cardinality CTRs cost more than
   estimated). Total run 2.93 h, inside the predicted 4 h.
6. **The diversity bar is cleared for the first time in this project.**
   `e06_cat_value_ids` correlates **0.9868** with `e06_cpu_base` and
   0.9873 with the standing champion — below the 0.995 blend bar, where
   every earlier pair sat at 0.9958–0.9999. The two value-id arms
   correlate 0.9994 with each other, so *they* must not be blended.

### Decisions (2026-09-03, post-E06)

- **New champion: `e06_cat_value_ids_src`** (OOF 0.94542), by the
  predeclared rule "between the two candidates, the higher OOF is
  submitted". Recorded caveat: its margin over `e06_cat_value_ids` is
  statistical noise (Finding 2), and the simpler arm carries no external
  dataset dependency. The rule was fixed before the run and is followed
  as written rather than re-chosen after seeing the numbers; if the
  dependency ever becomes inconvenient, `e06_cat_value_ids` is a
  sanctioned drop-in at −0.00002.
- **The plateau was never a ceiling — it was a blind spot.** E01–E05
  searched capacity, regularization, blending, averaging, features and
  extra rows, and all of them were flat because they all operated on a
  representation that discarded the signal. The lesson for the remaining
  weeks: when many independent axes all return null, suspect the
  representation before concluding the problem is exhausted.
- **Opened by this result:** seed-averaging the new champion (E03 proved
  averaging additive, +0.00019, and it has never been tested on this
  feature set), and — for the first time — a genuine blend, since the
  0.995 diversity bar is cleared. Both must be predeclared as E07.

**Submitted** 2026-09-03 (submission 4, id 55980494, kernel v9):
**public LB 0.94562**, up from 0.94210. CV↔LB gap **+0.00020** — the
first *positive* gap in this project, after −0.00008 / −0.00006 /
−0.00013. Mechanical explanation in `docs/5_submission_manifest.md`:
test-time value statistics are estimated from all 668,665 training rows
while each OOF fold used ~535k, so OOF slightly under-states this
feature family. Standing 130/531 (24.4th percentile) from 106/280
(~37th).


## Free post-E06 screens (2026-09-03, local, no fitting)

Three ideas tested against the saved OOF matrices at zero compute cost.
All three are **closed**; recorded so they are not re-attempted.

**1. Blending E06 with the pre-E06 models — closed, and the diversity
bar was the wrong test.** E06 Finding 6 noted correlation 0.9868, the
first pair ever under the 0.995 bar. But every rank-blend weight *hurts*,
monotonically: with `e03_cat_int_avg5seeds` at w=0.95 → −0.00003, w=0.90
→ −0.00007, w=0.75 → −0.00028. Same shape for `e06_cpu_base` and
`e02_lgbm_1000x05_interactions` (corr 0.9852). The partners are 0.0034
weaker, and decorrelation cannot pay for that much deficit.
**Lesson: the 0.995 diversity bar is necessary, not sufficient — a
partner also needs comparable strength. The bar as written would have
green-lit all three of these.** Blending the two E06 arms with each
other gives +0.00003 (corr 0.9994, fails the bar anyway).

**2. Tracing rows back to their source row — closed.** If a row could be
matched to the source row that generated it, its label would be readable
directly. It cannot: the generator resampled columns independently, so
multi-column keys match almost nothing. Income alone matches 97.9% of
train rows (75.8% uniquely), but adding one more column collapses it —
income+commute matches **8.2%**, income+commute+age **1.7%**,
income+age+cars+city 7.7%. And on the rows that *do* match uniquely, the
source label adds **±0.00001** over E06. This independently re-confirms
E06 Finding 2 by a second route: the source dataset holds nothing the
in-fold target statistics have not already extracted.

**3. Six target-free derived features — all exactly null.** Frequency of
the income value (train-only and train+test), frequency of the commute
value, the `income == 30000` floor flag (9.2% of rows), the commute
floor flag, and income mod 1000. Every one scores **±0.00000** over the
champion in the CV stack, individually and all six together. The
value-identity categoricals already carry whatever these encode.


## E07 — Re-testing Capacity and Encoding on the New Representation (predeclared 2026-09-03, before execution)

Kaggle kernel v10, notebook v8, **CPU**, full data, F1 folds, seed 42
throughout. First of a three-run sequence agreed with the user:
**E07 explores single-seed**, E08 averages the winner (E03 proved
averaging additive, so averaging before the config is settled would be
wasted compute), E09 evaluates 10-fold under its own fold definition.

**Why re-open axes the ledger calls closed.** E01 closed capacity and
E04 closed regularization — both measured on a representation that
discarded the value-identity signal E06 later found worth +0.00337. An
optimum located when 0.0034 less signal was extractable is not evidence
about the optimum now. This is a *scoped* re-opening with a stated
reason, not a licence to re-run history: each arm below is gated
normally, and a null result closes it again for good.

| Run | Description |
| --- | --- |
| `e07_base` | the champion config (2000 × 0.05, features v3 + source lookup), seed 42 — in-run gate baseline; expected to reproduce 0.94542 exactly (CPU is bit-reproducible, confirmed three times) |
| `e07_all_value_ids` | + the remaining five numerics as string categoricals (`Age`, both station counts, `Number_of_Cars_Owned`, `Environmental_Concern_Level`) — target-encoding them rather than splitting on them |
| `e07_cap_4000x025` | 4000 iterations at lr 0.025 — same budget product, finer steps |
| `e07_ctr1` | `max_ctr_complexity=1` (default 4): no categorical *combinations*. Tests whether combinations built on a 13,214-level categorical are noise rather than signal |

**Promotion criteria:** the standing paired gate, each arm vs.
`e07_base`, all single-seed CPU on identical folds. A promoted arm takes
the submission slot only if its OOF also exceeds
`STANDING_CHAMPION_OOF = 0.94542`; enforced in code via `SUBMIT_OK`.

**Falsifiable predictions, stated before the run:**

1. `e07_cap_4000x025` is the **most likely winner**: ≥ +0.0002. More
   extractable signal usually rewards more capacity, and this is the
   arm the re-opening argument is really about. If it lands below
   +0.00013 (the noise floor), capacity is closed permanently — the
   representation change did not move it, and the E01 finding was about
   the problem rather than the features.
2. `e07_all_value_ids` is **within ±0.0003** and fails to promote. Age
   (45 values), the station counts (15/20), cars (4) and concern level
   (5) are low-cardinality; trees isolate those with a few splits
   already, so target statistics should add nothing. The E06 gain came
   from cardinality trees *cannot* split through (13,214 and 805), which
   these are not.
3. `e07_ctr1` is **negative** (combinations help): between −0.0015 and
   0. Included because it is cheap, decisive either way, and would
   roughly halve run time if it were somehow neutral.
4. Total run under 6.5 h; `e07_cap_4000x025` is the long pole at ~2.2 h.

### Results (Kaggle kernel v10, notebook v8, CPU, full data, F1 folds)

| Run | OOF AUC | Δ vs base | fold std | Wall | Peak RSS |
| --- | --- | --- | --- | --- | --- |
| `e07_base` | 0.94542 | — | 0.00062 | 5,015 s | 2.97 GB |
| `e07_all_value_ids` | 0.94546 | +0.00004 | 0.00064 | 8,167 s | 3.30 GB |
| `e07_cap_4000x025` | 0.94544 | +0.00001 | 0.00064 | 9,905 s | 3.30 GB |
| `e07_ctr1` | 0.94520 | −0.00023 | 0.00063 | 2,445 s | 3.30 GB |

**Paired gate vs. `e07_base`** — **nothing promoted**:

| Candidate | Fold wins | 95% CI | P(Δ>0) | Promoted |
| --- | --- | --- | --- | --- |
| `e07_all_value_ids` | 4/5 | (−0.000009, +0.000076) | 0.954 | **No** |
| `e07_cap_4000x025` | 3/5 | (−0.000009, +0.000036) | 0.888 | **No** |

No submission written. Champion unchanged: `e06_cat_value_ids_src`.

### Scoring the predeclared predictions — 2 of 4 right

1. **Prediction 1 was WRONG, and it was the headline.** `e07_cap_4000x025`
   was predicted "most likely winner, ≥ +0.0002". It delivered
   **+0.00001** — 3/5 folds, P(Δ>0) 0.888, an order of magnitude below
   the claim and below the 0.00013 noise floor. Per the predeclared
   rule, **capacity is now closed permanently**: the representation
   change did not move its optimum, so E01's finding was about the
   problem, not the feature set. The reasoning that justified re-opening
   it — "more extractable signal usually rewards more capacity" — is
   falsified here and should not be reused as a motive.
2. **Prediction 2 correct.** `e07_all_value_ids` +0.00004, inside the
   predicted ±0.0003, failed to promote. It failed on the CI criterion
   alone (P(Δ>0) 0.954 does clear 0.95, but the interval includes zero),
   which is the gate behaving as designed — and a useful reminder that
   with two gates at 95% in one run, a lone P just over the threshold is
   exactly what multiple comparisons produce.
3. **Prediction 3 correct.** `e07_ctr1` −0.00023, inside the predicted
   −0.0015…0 band. Categorical **combinations are signal, not noise**,
   even when built on a 13,214-level feature — but they cost 2× the
   runtime for +0.00023, which is itself below the noise floor.
4. **Prediction 4 wrong on runtime.** Predicted under 6.5 h; actual
   **7 h 31 m** (7.09 h of fitting). The two feature-heavy arms ran
   2.3 h and 2.8 h against my ~1.2 h estimate — high-cardinality CTRs
   scale worse with iterations than assumed. Future budgeting for this
   representation should use ~1.4 s per 1000 rows per 1000 iterations,
   not the pre-E06 figure.

**Reproducibility:** `e07_base` is **bit-identical** to
`e06_cat_value_ids_src` from kernel v9 (`np.array_equal` True). Fourth
consecutive confirmation that CPU runs reproduce exactly across kernel
versions.

### Decisions (2026-09-04, post-E07)

- **Champion unchanged:** `e06_cat_value_ids_src` (OOF 0.94542, public
  0.94562).
- **Closed permanently:** capacity (second measurement, now on the new
  representation), encoding breadth (low-cardinality numerics as
  categoricals), CTR complexity. All correlations among E07 arms are
  0.9985–0.9997, far above the diversity bar, so no blend either.
- **What E07 really established:** the model is **saturated on this
  representation**. Three independent knobs — capacity, feature breadth,
  categorical interaction depth — all move it less than the noise floor.
  The remaining gap to the leaderboard top (~0.0008) is therefore not a
  tuning problem, and should not be attacked with more configurations.

*(E08 next, per the agreed sequence: seed-average the champion.)*

## E08 — Seed Averaging, and a Test-Time Fitting Change (predeclared 2026-09-04, before execution)

Kaggle kernel v11, notebook v9, **CPU**, F1 folds. Second of the agreed
three-run sequence. E07 established the model is saturated on
*configuration*, so E08 changes **how the champion is fit**, not what.

### Part A — seed averaging (gated normally)

| Run | Description |
| --- | --- |
| `e08_s42` | champion config (features v3 + source lookup), seed 42 — gate baseline and average member; expected to reproduce 0.94542 exactly |
| `e08_s7`, `e08_s2026` | same, seeds 7 and 2026 |
| `e08_avg3seeds` | element-wise mean of the three — the candidate |

**Promotion criterion:** the standing paired gate vs. `e08_s42`. Takes
the submission slot only if OOF also exceeds
`STANDING_CHAMPION_OOF = 0.94542`.

**Falsifiable prediction:** **+0.00019**, matching E03's measurement of
the identical operation on the previous representation (0.94204 →
0.94223), so OOF ≈ **0.94561**, promoting 5/5. If averaging now returns
less than +0.00010, seed variance is not additive with the value-identity
features and the E03 result does not generalise across representations.

### Part B — full-data refit for test predictions (NOT gated — read this)

**The motivation is a measured asymmetry, not a hunch.** E06's public LB
*beat* its OOF by +0.00020, reversing the sign of the three previous
gaps. The likely mechanism: a row's value-identity encoding is a target
statistic over rows sharing that value, and **test rows get statistics
estimated from all 668,665 training rows, while each OOF fold's came
from only ~535,000**. If that is the cause, then the current test
prediction — the mean of five fold-models, each still holding only 80%
of the statistics — is leaving that advantage on the table.

`e08_fulldata_avg3`: the champion config fit on **all 668,665 rows**
(seeds 42, 7, 2026, averaged), predicting test directly.

**This arm has no OOF and therefore cannot be gated.** It is kept in a
separate store, can never enter the gate or champion selection, and
writes a *separate* artifact (`submission_fulldata.csv`). Saying so
plainly because the project's own rule is that a decision which must
stop something has to be a mechanism, not a note — the mechanism here is
the separate store, not this paragraph.

**How it gets decided, since OOF cannot:** by a paired leaderboard
comparison — submit both artifacts and compare. That is sound here
specifically because the two models are near-identical and scored on the
same rows, so the *difference* is far better determined than either
absolute score. It costs 2 of 10 daily submissions.

**Falsifiable prediction:** `submission_fulldata.csv` scores **+0.0001
to +0.0003** above the 5-fold-average artifact on the public LB. If it
scores *lower*, the LB>OOF gap has some other cause and the fold-model
average stays — in which case the +0.00020 explanation in
`docs/5_submission_manifest.md` is wrong and must be corrected.

**Predicted cost:** Part A ~4.2 h (3 × 1.4 h), Part B ~1.0 h (3 fits on
668k rows, no folds). Total ~5.2 h — budgeted with E07's corrected
figure, having under-estimated that run by an hour.

*(results pending — notebook v9 kernel run)*

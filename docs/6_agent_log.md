# Agent Collaboration Log

Append-only, per master standard §13. Correct a past entry by adding a new
one, never by rewriting it. Record what was **checked**, not just what was
claimed; findings that did not hold up stay visible.

**For an independent reviewer:** every quantitative claim should trace to a
row in `docs/4_experiment_ledger.md` or an executed notebook cell. Gate
criteria are meant to be committed **before** results — for E01 this is
provable from git history (predeclaration commit `3acae15` precedes any
results commit), which is stronger than S6E8's same-commit caveat.

---

## 2026-09-01 — Session 1 (scaffold, retroactive note)

Repo scaffolded per master §13 (`d6e4b57`): AGENTS/CLAUDE, docs 0–1,
`.gitignore`, scripts. Competition **not yet joined**; metric/target/format
recorded as unknown rather than inferred. Recorded retroactively by
session 2 from git history.

## 2026-09-01 — Session 2 (join → EDA → baselines), commit `b488c43`

- Competition found already joined (`userHasEntered: True`); data
  downloaded; every unknown in `docs/1_instructions.md` filled from the
  Kaggle API + files. **Checked:** metric read from the API competition
  object (`Roc Auc Score`), not inferred from the title; sample-submission
  constant equals train prevalence to 6 dp.
- `notebooks/01_eda.ipynb` executed end-to-end locally (~21 s);
  `docs/2_eda_insights.md`. **Checked:** zero missing/duplicates asserted,
  adversarial AUC 0.4992 (3-fold OOF), monotone ordinals from full-train
  rates.
- `docs/3_implementation_plan.md` + `docs/4_experiment_ledger.md` written
  with fold definition F1 and promotion/diversity gates **before** any
  model run.
- `notebooks/02_baseline_modeling.ipynb` v1 executed locally (kernel
  `s6e8-py39`): five runs, working champion `v2b_catboost_default`
  OOF AUC 0.94157 ± 0.00072. **Checked:** `scripts/verify_submission.py`
  passes on the champion artifact; sanity checks + OOF correlations in the
  notebook.
- User approved commit + submission flow + E01.

## 2026-09-01 — Kaggle kernel v1 failures and fix, commits `c40ba9b`, `3acae15`

- **Finding that did not hold up:** "both failed" (user report) — partially
  wrong on investigation. The Kaggle kernels (eda v1, baseline v1) did
  fail; the local E01 run was still healthy (evidence: live kernel process
  at ~390% CPU; empty log was buffering, not failure). The status poller's
  `case` match was lowercase-only, so `KernelWorkerStatus.ERROR` never
  broke the loop — poller bug, separate from the kernel failure.
- **Root cause (kernel):** `StopIteration` in the data-dir resolver — the
  worker mounts competition data at `/kaggle/input/competitions/<slug>`,
  not the assumed `/kaggle/input/<slug>`. Reference: S6E8's working
  notebooks check the `competitions/` layout. Master §12 (walk the mount)
  was violated; fix adds both layouts + `rglob` walk.
- **Checked:** EDA re-executed locally clean, then kernel v2 reached
  `KernelWorkerStatus.COMPLETE` on Kaggle (~20:01 local). The baseline
  notebook carries the same fix via its generator; its v2 push waits for
  the in-flight local E01 run to finish.
- E01 configs frozen in the ledger (`3acae15`) before execution.

## 2026-09-01 — User directive: execute on Kaggle only

From this point, notebooks are authored/edited locally but **executed on
Kaggle** (push kernel → poll status → pull outputs), not locally. The
in-flight local E01 run predates the directive and is allowed to finish;
its ledger rows will say "local". Recorded in
`docs/0_coding_standards.md`.

**Open items at time of writing:**
- Local E01 run in progress; on completion: patch baseline notebook with
  the §12 path fix, fill insights/ledger, push kernel v2.
- Under the Kaggle-only rule the notebook should also write OOF `.npy`
  artifacts to the kernel output dir so `kaggle kernels output` can
  retrieve them (currently local-only via `../predictions`).
- First leaderboard submission pending kernel v2 COMPLETE
  (`-v 2` flow); `docs/5_submission_manifest.md` created then.
- Original source dataset still unidentified (`docs/1_instructions.md`).

## 2026-09-01 — E01 results, first paired-gate promotion

- Local E01 run finished (2 h 46 m wall, contention-inflated; last
  pre-directive local run). **Checked:** all 12 runs pass sanity; no error
  outputs; totals match the notebook snapshot cell.
- **`e01_cat_2000x05` promoted** — 5/5 folds, 95% CI (+0.000145,
  +0.000239), P(Δ>0)=1.000. Gate criteria were committed before results
  (`3acae15`), so the ordering is auditable.
- Optuna skipped per predeclared condition (capacity increases all hurt).
- Diversity vs. new champion: LightGBM 0.9964, HGB 0.9963 — above the
  ≤ 0.995 bar → **blend skipped by predeclaration** (the earlier 0.9940
  reading was against the superseded champion). Recorded in the ledger.
- Notebook patched post-run: §12 data-dir resolver (same fix as EDA,
  validated by EDA kernel v2 COMPLETE) and artifact writes to the kernel
  working dir. These two cells changed without a local rerun — the
  validating run is baseline kernel v2 on Kaggle, per the execution rule.
- Next: push baseline kernel v2 → COMPLETE → submit `-v 2` → create
  `docs/5_submission_manifest.md`.

## 2026-09-01 — Kernel v2 COMPLETE on Kaggle; first submission scored

- Kernel v2 ran end-to-end on Kaggle (~3 h): resolver landed on
  `/kaggle/input/competitions/playground-series-s6e9` — the root-cause
  fix confirmed in production. **Checked:** Kaggle's own gate re-run gave
  the same verdict (champion `e01_cat_2000x05`, OOF 0.94177 there) and
  additionally gate-tested `e01_lgbm_1000x05` (3/5 folds, CI spanning 0)
  → correctly rejected. Cross-environment numbers differ only in the 5th
  decimal (library versions), as expected.
- Submitted via `-k ... -v 2` (§11 flow). **Public LB 0.94169** vs. OOF
  0.94177 — gap −0.00008, the CV↔LB hypothesis confirmed. Recorded in
  `docs/5_submission_manifest.md`. Quota 1/10; standing 79 of
  157 at submission time.
- Open: E-next experiment TBD (blend closed by diversity bar; Optuna
  closed by no-headroom); source dataset still unidentified.

## 2026-09-02 — E02 on Kaggle: interactions promoted, LB 0.94198

- Kernel v3 (first Kaggle-only experiment run, ~5.5 h) COMPLETE.
  **Checked:** in-run champion re-fit matched v2 to the 5th decimal
  (0.94177), validating within-run gate comparisons.
- **`e02_cat_interactions` promoted** (OOF 0.94204; 5/5 folds, CI
  (+0.000209, +0.000317)). Interaction effect replicated on LightGBM
  (0.94155 → 0.94182) though that variant was itself rejected by the gate
  (CI spanning zero) — the gate separating a real feature effect from an
  unpromotable candidate in the same run. Seed-averaging also promoted
  (0.94193) but superseded. Budget direction closed (3000×0.035 tied).
- Submitted `-v 3`: **public 0.94198** vs. OOF 0.94204 — LB gain
  (+0.00029) matched OOF gain (+0.00027). Manifest row 2.
- Notebook v3 refactor in effect: historical sections behind flags;
  committed output-free; the executed record is the kernel version page.
- Open: E03 (interactions + seed-average combo) flagged in the ledger,
  **not yet predeclared**; source dataset still unidentified.

## 2026-09-02 — E03: additivity confirmed exactly; LB 0.94210

- Kernel v4 COMPLETE (~5 h, CPU). **Checked:** in-run champion re-fit
  reproduced 0.94204 exactly; the dry-run design held (5 fits, champion
  fit once as the seed-42 member).
- **Predeclared prediction met exactly:** ledger said OOF ≈ 0.94220 if
  interactions and seed-averaging are additive; `e03_cat_int_avg3seeds`
  returned **0.94220**. Both averages promoted (5/5 folds);
  `e03_cat_int_avg5seeds` (0.94223) took the champion slot by the
  highest-OOF rule — recorded with the caveat that the 5th seed bought
  +0.00003 for +5763 s, and 3 seeds is a sanctioned fallback.
- Measured noise floor: single-seed spread of one config is 0.00013.
- Submitted `-v 4`: **public 0.94210**. Manifest row 3. Standing 106/280
  — rank number rose while score improved because the field grew; noted
  in the manifest so nobody reads rank as a model signal.
- **All cheap levers now closed** (budget, Optuna, blending, averaging,
  the one EDA-backed feature idea). Recorded so a later session doesn't
  retry them.
- Next: E04 on GPU (sanctioned 2026-09-02) — must re-fit the champion,
  since GPU/CPU are separate comparability classes. Source dataset still
  unidentified.

## 2026-09-02 — E04 (first GPU run): null result, and a claim of mine falsified

- Kernel v5 COMPLETE on GPU. **No submission** — the predeclared
  fallback fired exactly as the dry run predicted.
- **Finding that did not hold up — mine.** An E02 insight cell asserted
  "the plateau is regularization-side, not capacity-starved". That was
  speculation written next to real numbers, which is how unverified
  claims harden into fact. E04 tested it: `l2_leaf_reg` 10/30 moved OOF
  +0.00001/+0.00002 (noise floor 0.00013) and random_strength/bagging
  *hurt* by 0.00030. **Falsified.** The notebook cell now says so
  in place, rather than being quietly deleted.
- **GPU measured, not assumed:** 8.9× faster (341 s vs 3018 s), and
  **0.00070 AUC worse** on an identical config — 5.4× the noise floor,
  and more than every gain this project has won combined. GPU is
  reclassified in the standards as screening-only, CPU re-fit required
  before any promotion or submission. Had the cross-device rule not been
  predeclared before this run, a GPU champion would have looked like
  progress while losing more than the entire search had gained.
- Features v2 (EDA §6 conditional charging + anxiety/income crosses):
  +0.00003, gate-rejected. Caveat recorded in the ledger that GPU's
  coarser binning could mask a small effect; not chased, because there is
  no positive signal to chase.
- **Closed axes:** capacity, regularization, blending, averaging,
  subsidy-gate features, Optuna. Recorded so no later session re-runs
  them. Genuinely open: the unidentified source dataset.

## 2026-09-02 — Notebooks republished; GPU non-determinism observed

- **EDA kernel v3 COMPLETE** (findings-only version) and **baseline
  kernel v7 COMPLETE** (restructured sections, roadmap removed). Both
  verified on the Kaggle worker, not just locally.
- **Checked, and worth recording:** v7 re-ran E04's identical code, seeds
  and folds. The verdict held (nothing promoted, no submission) but OOF
  moved in the 5th decimal and the gate's P(Δ>0) swung **0.648 → 0.879**.
  CatBoost GPU is not deterministic run-to-run; CPU runs in this project
  have reproduced exactly. Recorded as ledger Finding 4 and in the
  standards. This is a second independent reason GPU stays
  screening-only: near a gate boundary, run-to-run noise alone could
  flip a promotion.
- No change to the champion or the leaderboard: `e03_cat_int_avg5seeds`,
  public 0.94210, 3 submissions.

## 2026-09-02 — Multi-agent audit: two real defects fixed

Ran a 152-agent audit workflow (six bug lenses, each finding refuted by
three independent verifiers). The ideation half and ~97 verifier agents
died on a session limit, so **the idea results are absent, not empty** —
no score ideas were produced and none should be inferred. The audit half
returned findings, which I re-verified myself against the code rather
than trusting partially-voted verdicts.

**Confirmed and fixed:**

1. **CRITICAL — submission written against its own warning.** The E04
   below-standing branch printed "do not submit this run's artifact" and
   then wrote `submission.csv`, because `CHAMPION_NAME = best` was set in
   both arms and the submission cell only checked membership in
   `test_store`. Real regime: E04 measured GPU at 0.00070 worse, so a GPU
   winner below the CPU champion is the *expected* case, not an edge
   case. Fixed with a `SUBMIT_OK` flag the submission cell honours;
   regression-tested on the exact path (candidate beats in-run baseline,
   sits below the standing champion) — now writes nothing.
2. **HIGH — `BASELINE_CHAMPION` collisions in frozen sections.** After
   E03's promotion the pointer named E03's own average, so §4.5 wrote
   that name twice (single-seed + average) and §4.4 referenced a run it
   never fits (KeyError). Fixed with literal names
   (`e03_cat_int_s42`, `e01_cat_2000x05`) plus an assert in `_register`
   making duplicate names fail loudly.

**Verified:** all 256 RUN_* flag combinations now execute cleanly — no
duplicate names, no KeyError, no NameError. An earlier sweep reporting
128 failures was a gap in my own stub harness (`roc_auc_score` unstubbed),
not a notebook defect; recorded here because the distinction matters.

**Not yet acted on** — audit findings I have not verified myself and must
not treat as established: paired-bootstrap construction, family-wise
error across E01–E05's many 95% gates, `fold_std` using ddof=0,
unpinned `requirements.txt`, and several docs-consistency claims.

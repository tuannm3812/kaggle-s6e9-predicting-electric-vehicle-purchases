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

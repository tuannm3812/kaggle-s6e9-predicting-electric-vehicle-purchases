# Coding Standards

## Baseline

This project follows the shared
`coding-standards/coding_standards.md` at the GitHub root
(`/Users/tuannm3812/Documents/GitHub/coding-standards`) as its baseline. That
file is the fallback for anything not overridden below — commit message
convention, pre-commit/pre-push workflow, notebook style, feature-engineering
and leakage-prevention rules, and documentation style all live there.

Everything in this file is either a project-specific addition or an explicit
override. **Do not copy the shared standard into this file.** If a rule here
duplicates it, delete the copy and keep the reference.

## Repository Scope

Notebook-first Kaggle workflow, matching
`kaggle-s6e7-predicting-student-health-risk` and
`kaggle-s6e8-predicting-smartphone-addiction`:

- `notebooks/` — EDA, baseline modeling, tuning, ensembling. Plus
  `notebooks/kernels/<name>/` holding each notebook's Kaggle
  `kernel-metadata.json`.
- `docs/` — durable findings and decisions, numbered per master standard §2.
- `scripts/` — small CLI helpers only (`push_kaggle_kernel.sh`,
  `verify_submission.py`, `check_frames.py`), never core logic.
- `data/` — local Kaggle files. **Gitignored.**
- `predictions/` — OOF and test prediction matrices. **Gitignored.**

`data/` and `predictions/` are intentional additions on top of the shared
baseline's minimal root, because this project uses the Kaggle CLI locally.
Both stay out of git.

## Scale override

The test set is large enough (7.7 MB sample submission) that the usual
"just rerun it" habits from earlier Season 6 episodes may not hold. Two
consequences:

- **Measure before scaling an experiment.** Record wall-clock and memory for
  the first full-data fit, and put the numbers in the experiment ledger before
  launching a sweep.
- **Prefer a fixed subsample for exploratory work**, with a stated fraction and
  seed, and promote to full data only for candidate runs. Say which was used in
  every recorded result — a subsample score and a full-data score are not
  comparable and must not share a row.

## Validation

- Fixed folds, defined once and reused by every comparable model, so OOF
  predictions align across candidates.
- Any transform that touches the target — target encoding, calibration —
  fits **inside** the fold, never globally (master standard §5).
- Record the fold definition (n_splits, seed, stratification key) in the
  experiment ledger the first time it is used.

**Fold definitions are a comparability class (added 2026-09-03).** F1 is
`StratifiedKFold(5, shuffle=True, random_state=42)`; F2 is the same with
10 splits. An F1 OOF and an F2 OOF are different measurements and must
never be gated against each other — more training data per fold flatters
OOF, which is the treatment under test rather than a confound. This sits
at the same level of consequence as the CPU/GPU rule, and like it is
enforced in code: `paired_gate` asserts both runs share a definition,
`register_average` refuses members spanning classes, and §9 filters
promotions to the champion's class. A cross-class claim is settled by
leaderboard instead, with its prediction fixed in advance.

## Promotion gate

Carried forward from S6E7 and S6E8, which both used it to stop wasted work:

- A new champion needs a **paired comparison on aligned OOF predictions**, not
  a better single-split number.
- State the promotion criterion **before** running the comparison.
- Record non-promotions too, with their numbers. A model that failed to promote
  is evidence about the problem, and re-running it later is pure waste.
- Before spending budget on an ensemble, check candidate correlation against a
  predeclared diversity bar. S6E8 correctly skipped ensembling on a `0.9976`
  correlation — that decision is the standard, not the exception.

## Submissions

- Notebook-based submission where the competition supports it (master
  standard §11). Confirm which applies — see `docs/1_instructions.md`.
- Run `scripts/verify_submission.py` against `sample_submission.csv` before
  every submission: column names, row count, **id order**, finiteness, and
  value range. (It does not check dtypes; an earlier version of this line
  said it did.)
- Record every submission in the submission manifest with its notebook version
  and the decision it supported. Never let a scored submission go unrecorded.

## Execution environment (user directive, 2026-09-01)

Notebooks are authored and edited locally, but **executed on Kaggle, not
locally**: `scripts/push_kaggle_kernel.sh <target>` → poll `kaggle kernels
status` (match `COMPLETE`/`ERROR` case-insensitively) → retrieve artifacts
with `kaggle kernels output`. The trusted run behind any committed output
or ledger row is the Kaggle kernel run; ledger rows cite the kernel
version, and rows from the pre-directive local runs are marked "local".
Local execution is reserved for cheap syntax/smoke checks, not full runs.

Consequence: notebooks must write every artifact needed downstream (OOF
matrices included) to the kernel working directory so `kaggle kernels
output` can fetch them — the local-only `../predictions` path is a
fallback, not the primary channel.

## GPU execution (user directive, 2026-09-02)

GPU is available for Kaggle runs when it pays. CatBoost dominates this
project's runtime (~3400 s per full-data 5-fold fit on the CPU worker), so
GPU is the lever that makes wider experiments affordable.

**The comparability rule — this is the part that bites.** CatBoost's GPU
implementation is not numerically identical to its CPU one (notably
`border_count` defaults to 128 on GPU vs. 254 on CPU, and some split
algorithms differ). A GPU OOF score therefore **does not share a
comparability class with a CPU OOF score**, exactly like the subsample /
full-data rule above:

- A GPU result and a CPU result **never share a ledger row**, and a GPU
  candidate is never gated against a CPU champion number.
- Every ledger row states its device.
- This project's gate design already absorbs this: the champion is
  **re-fit in-run** before every comparison, so a GPU run gates
  GPU-vs-GPU and stays valid without re-running history.
- The first GPU run must include a champion re-fit, giving both the
  timing gain and the numerical GPU-vs-CPU delta as *measured* facts
  rather than assumptions.

**Measured 2026-09-02 (E04), replacing the assumption above:** GPU is
**8.9× faster** (341 s vs. 3018 s per 5-fold fit) and **0.00070 AUC
worse** on the identical configuration — 5.4× this dataset's single-seed
noise floor, and more than every gain the whole search has won combined.
So GPU is a **screening tool only**: explore configurations on GPU,
re-fit anything promising on CPU before it can become a champion or a
submission artifact. Never submit a GPU-fit model here.

**GPU runs are also not bit-reproducible** (measured on the E04 re-run,
2026-09-02): identical code, seeds and folds moved OOF in the 5th decimal
and swung the gate's P(Δ>0) from 0.648 to 0.879. CPU runs here reproduce
exactly. So a GPU result near a gate boundary is not trustworthy on its
own, and any reproducibility claim about a GPU run must be qualified.

**Mechanics:** set `enable_gpu: true` in the kernel metadata and pass
`task_type="GPU"` in the CatBoost config — metadata alone does nothing,
the model must select GPU computation. GPU quota is limited and mutable;
check it live rather than recalling a number. LightGBM/HGB configurations
here stay CPU: they already fit in 200–300 s, so GPU would add
comparability risk for no meaningful gain.

## Public notebooks carry findings, not forward strategy (2026-09-02)

`notebooks/` is pushed to **public** Kaggle kernels
(`is_private: false`), so a notebook is a published artifact, not a
private worklog. Consequence:

- **No "Next Moves" / roadmap / planning sections in any notebook** —
  EDA included (applied 2026-09-02 to both notebooks). Forward
  strategy — what is closed, what is worth trying next, what the
  remaining levers are — lives in `docs/3_implementation_plan.md` and
  `docs/4_experiment_ledger.md`.
- Notebooks keep **insight cells about results already produced**: what a
  number means, what a gate decided, what a hypothesis showed. That is
  the interpretation the master standard requires (§4), and it is
  finished work rather than intent.
- A closing summary of *what this notebook established* is fine; a list
  of what to do next is not.

**Section numbering.** Headings are a reader's map, so they must stay a
clean hierarchy: top-level `##` for real stages of the workflow, `###`
for parts of one stage. Completed experiments belong grouped under a
single top-level section (one `###` each), not promoted to peers of
Config and Submission — a notebook that accretes `8b`, `8c`, … as
experiments land has lost the map. Renumber when a section is added or
retired rather than suffixing.

## Derive run-guards, never enumerate them (2026-09-02)

A notebook that accumulates experiment flags (`RUN_E01`, `RUN_E02`, …)
must not gate shared sections on an enumerated list like
`if RUN_CHAMPION and not (RUN_E03 or RUN_E04)`. That list was forgotten
twice in one day — when E04 was added, and again for E05 — and each time
the failure was silent and consequential: the generic champion re-fit
would fit a *single* model under a seed-*average* champion's name, then
the submission cell would happily write an artifact from it.

Derive the condition instead (`EXPERIMENT_ACTIVE = RUN_E02 or …`), define
it next to the flags, and say in a comment that new flags are added there
rather than at each use site. More generally: when a bug class recurs,
change the structure that permits it, not just the instance.

**A validity check is not a variation check (2026-09-05).** E10's
pre-run smoke test confirmed each CatBoost config was *accepted* and
caught an invalid one before it could kill a run — good as far as it
went. Two accepted configs then produced **bit-identical** predictions to
the baseline, so ~2.8 h of kernel compute re-measured the baseline twice.
Before spending platform compute on a configuration sweep, fit two tiny
models and **assert the predictions differ**; an accepted parameter is
not necessarily an effective one. (Here the cause was real: for a binary
target at `TargetBorderCount=1`, `BinarizedTargetMeanValue` and `Borders`
are algebraically the same, and `combinations_ctr=["Borders","Counter"]`
is already the default.)

**A precondition in a comment is not a precondition (2026-09-04, third
instance of this pattern).** §5's champion re-fit carried the comment
*"Only valid when BASELINE_CHAMPION names a single-model config"*. By
notebook v10 the champion was a **3-seed average on features v3**, so a
run with `RUN_CHAMPION=True` and no experiment active would fit **one**
model on the **pre-E06 frame**, register it under the average's name, and
write `submission.csv` from it — an artifact roughly **0.0034 worse**,
labelled as the champion. The 16,384-combination sweep passed it, because
the sweep asserts that nothing *crashes*, not that the right model was
fit.

The fix makes the champion's composition **data** (`CHAMPION_SEEDS`,
`CHAMPION_IS_AVERAGE`, `CHAMPION_FOLDS`) and has §5 reproduce it or
refuse. Two general rules follow, both learned the hard way here:

- **When a section's correctness depends on a fact about a moving
  pointer, encode the fact next to the pointer.** Every time this project
  wrote the dependency as prose instead, it broke on the next promotion.
- **A sweep that only checks for exceptions is not a correctness test.**
  Add assertions about *what was fit and what was written*, not just that
  the cell ran. The champion-re-fit scenarios are now permanent cases in
  the dry-run.

**A stub that supplies what §2 should build cannot test §2 (2026-09-04).**
The enumerated-flag bug above recurred a *third* time — the guard
`if (RUN_E06 or RUN_E07 or RUN_E08)` around the value-identity feature
frames was not updated for E09 — and kernel v12 died on
`NameError: X_v3s` after reaching the first fit. The 16,384-combination
dry-run passed it, because the harness pre-defines `X_v3s` and every
other frame in order to sweep cheaply. **A harness that injects the
artefact under test is blind to that artefact's absence.**

Two fixes, both structural:

- The guard is derived once (`NEEDS_VALUE_ID_FRAMES`, beside
  `NEEDS_SOURCE` and `EXPERIMENT_ACTIVE`) rather than repeated.
- `scripts/check_frames.py` executes the **real** Config and Data cells
  for each experiment flag and statically resolves every frame name that
  experiment references, so a missing frame fails locally in seconds.
  Run it before every push; the fast dry-run covers control flow, this
  covers frame availability, and neither substitutes for the other.

**Dry-run every branch before spending platform compute.** Stub the
harness, execute the notebook's control flow with fake numbers, and assert
on fit counts, which runs receive extra data, which candidate is selected,
and whether an artifact is written. This practice caught the mislabeled
re-fit twice, a `StopIteration` on a carried-over champion, and a
submission that would have been written from predictions the run never
produced.

## A run name is a primary key; a printed warning is not a control (2026-09-02)

Two defects found by a multi-agent audit, both from the same habit of
letting *prose* or a *moving pointer* stand in for a mechanism:

1. **A printed warning is not a guard.** The E04 champion-selection branch
   printed "do not submit this run's artifact" and then set
   `CHAMPION_NAME` anyway, so the submission cell wrote the file. On
   Kaggle that file *is* the competition submission — a model measured
   0.00070 AUC worse would have been submitted against an explicit
   instruction not to. A decision that must stop something has to be a
   variable the code reads (`SUBMIT_OK`), never a message a human reads.
2. **Historical sections must use literal run names, never a moving
   pointer.** `BASELINE_CHAMPION` is repointed on every promotion, but
   frozen sections referenced it, so after E03 was promoted the E03
   section wrote one name twice (single-seed row *and* the average that
   contained it) and the E02 section referenced a run it never fits.
   Lookups are `next(r for r in results if r["run"] == name)` — first
   match wins — so a duplicated name silently splits one identity across
   two different vectors, and the gate could screen against one baseline
   while bootstrapping against another.

Enforcement: `_register` now asserts the name is unused, so any future
collision fails loudly instead of silently. Prefer a mechanism that makes
the bad state unrepresentable over a comment asking the reader not to
enter it.

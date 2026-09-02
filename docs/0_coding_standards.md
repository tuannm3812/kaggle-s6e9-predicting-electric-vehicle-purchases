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
  `verify_submission.py`), never core logic.
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
  every submission: column names, row count, dtypes, and value range.
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

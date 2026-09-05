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
  `kernel-metadata.json`. **Deliberate deviations from master §2:** the
  notebooks are zero-padded (`01_eda.ipynb`, `02_modeling.ipynb`) rather
  than `1_eda.ipynb` — declared rather than fixed, since the master says
  not to renumber an existing repo and the names are load-bearing. The
  modeling notebook was renamed from `02_baseline_modeling.ipynb` on
  2026-09-05 because "baseline" no longer described a workflow holding
  E01–E10. The kernel slug followed: pushing the new title made Kaggle
  **re-slug the kernel to `ev-purchases-modeling` while preserving the
  full version lineage** (the push landed as v16 of the same kernel) —
  contradicting the assumption, written here hours earlier, that the
  slug was immutable and a title change would abandon versions 2–15.
  Verified empirically: the old slug 404s on the API, the new one
  carries all versions. Manifest rows citing
  `-k tuannm3812/ev-purchases-baseline-modeling -v N` are the commands
  as actually run and stay as written; every future command uses the
  new slug.
- `docs/` — durable findings and decisions, numbered per master standard §2.
- `scripts/` — small CLI helpers only (`push_kaggle_kernel.sh`,
  `verify_submission.py`, `check_frames.py`, `render_pdf.py`), never
  core logic.
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

GPU is allowed for Kaggle runs, but E04 measured it and demoted it:
**8.9× faster, 0.00070 AUC worse, and not bit-reproducible** (identical
inputs moved the gate's P(Δ>0) from 0.648 to 0.879). So GPU is a
**screening tool only** — explore on GPU if a sweep ever needs it, re-fit
on CPU before anything can be promoted or submitted, and never trust a
GPU result near a gate boundary. A GPU row never shares a comparability
class with a CPU row; every ledger row states its device, and the in-run
champion re-fit keeps gates valid across the boundary. Measurements and
the two findings behind this rule: `docs/4_experiment_ledger.md`, E04.

**Mechanics:** `enable_gpu: true` in kernel metadata does nothing by
itself — CatBoost must also get `task_type="GPU"` (the notebook's
`USE_GPU` flag does both). LightGBM/HGB stay CPU: they fit in 200–300 s,
so GPU adds comparability risk for no gain. GPU quota is mutable; check
it live.

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

## Hard-won harness rules (each learned from a real failure)

Each rule below is stated in the 2–4 lines an implementer needs; the full
incident — kernel versions, hours lost, exact tracebacks — lives in the
`docs/6_agent_log.md` entry of the date given. Do not re-inline the
stories here.

- **Derive run-guards, never enumerate them** (2026-09-02, recurred
  2026-09-04 ×2). Any condition of the form `if RUN_A or RUN_B` at a use
  site is forgotten when `RUN_C` arrives. Define it once, named, next to
  the flags (`EXPERIMENT_ACTIVE`, `NEEDS_SOURCE`,
  `NEEDS_VALUE_ID_FRAMES`, `CHAMPION_REFIT`), and add new flags there.
- **Dry-run every branch before spending platform compute** — stub the
  harness, execute the real control flow, and assert on *what is fit and
  what is written*, not merely that nothing raises. A sweep that only
  checks for exceptions passed a notebook that silently fit the wrong
  model (2026-09-05).
- **A stub that supplies what §2 should build cannot test §2**
  (2026-09-04). The dry-run pre-defines feature frames to sweep cheaply,
  so it is structurally blind to a frame §2 fails to build; that is what
  `scripts/check_frames.py` exists for. Run both before every push —
  neither substitutes for the other.
- **A precondition in a comment is not a precondition** (2026-09-04,
  third instance of the pattern). When a section's correctness depends on
  a fact about a moving pointer, encode the fact as data beside the
  pointer (`CHAMPION_SEEDS`, `CHAMPION_IS_AVERAGE`) and make the code
  reproduce-or-refuse.
- **A validity check is not a variation check** (2026-09-05). Before a
  configuration sweep, fit two tiny models and assert the predictions
  *differ*; an accepted parameter is not necessarily an effective one.
  Two E10 arms re-measured the baseline bit-for-bit.

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

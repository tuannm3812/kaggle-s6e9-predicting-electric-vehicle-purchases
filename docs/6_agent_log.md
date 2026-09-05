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
- Features v2 (EDA notebook §6 conditional charging + anxiety/income crosses):
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

## 2026-09-02 — E05 read: source dataset is a null

Kernel v8 output fetched (the earlier fetch attempt was declined by the
user; retried on their "retry"). `e05_cpu_plus_source` vs `e05_cpu_base`:
+0.00001 OOF, 3/5 fold wins, 95% CI (−0.000049, +0.000073), P(Δ>0)
0.627 → not promoted, exactly as the predeclared prediction said. No
submission written (predeclared; the `SUBMIT_OK` path fired).

Two things worth an independent reviewer's attention:

- **Predeclaration discrepancy, recorded not hidden:** the ledger
  predeclared 9,478 usable source rows; the kernel measured 9,466. My
  local count used a different missing-value rule. Immaterial to a
  0.00001 result, but the predeclared number was wrong and the ledger
  now says so (E05 Finding 2).
- **Bit-reproducibility confirmed for CPU:** `e05_cpu_base` (kernel v8)
  and `e02_cat_interactions` (kernel v4) are the same config and
  correlate at 1.0000 with identical AUC. That is the property the GPU
  path failed in E04.

Docs updated: ledger (results + post-E05 decisions), implementation plan
(closed-axes table now includes the source dataset; "open" list is
empty by design), provenance (outcome section). E05 matrices copied to
`predictions/`. The three older "source dataset still unidentified"
lines above are dated entries and stay as written.

**State:** champion `e03_cat_int_avg5seeds`, public 0.94210, 3
submissions. Every predeclared lever measured. Nothing predeclared for
E06 yet — ideation from the audit workflow is still absent (session
limit), so the next step is generating candidates by another route and
predeclaring before any run.

## 2026-09-03 — E06 found, predeclared, implemented (not yet run)

Both re-launched ideation agents died on the session limit again, so
the candidate came from a cheap local diagnostic instead: the numeric
columns are discrete, `Annual_Income_USD` is a *value identity* (97.9%
of train values are source-dataset incomes), and an out-of-fold
encoding of the exact value scores AUC 0.7072 vs 0.6812 binned. A CV'd
logistic stack over the champion's OOF estimated +0.0009 (income alone)
to +0.0013 (all three features) — 7–10× the noise floor and more than
every accepted step combined. Details: EDA insights §10, ledger E06.

Order of operations, for a reviewer checking predeclaration: ledger E06
committed at `b0beece` **before** the notebook change; the notebook v7
commit follows it.

Notebook v7 changes: `make_features(value_ids=True)` (features v3),
`load_source_frame` / `build_source_lookup` / `add_source_lookup`
(source labels only, no fold handling needed), E05 frozen as §4.7 with
its insight filled, E06 as §6, gate/selection wired for E06, and a new
same-device rule in §9 — a promoted candidate takes the submission slot
only if its OOF exceeds `STANDING_CHAMPION_OOF` (0.94223), enforced by
`SUBMIT_OK`, not by prose. Also moved the stranded E02/E03 insight cells
back under §4.4/§4.5 and guarded the summary cell against an empty
`results` (it raised on the all-flags-off path).

Dry-run: 2048/2048 flag combinations execute cleanly; 7 scripted E06
scenarios assert fit lists, champion choice, `SUBMIT_OK`, and whether
`submission.csv` exists. Real smoke check of §1–2 on local data: the
value-id columns and source lookup build correctly (0.58% of test
incomes unseen; 97.9% train / 97.9% test rows match a source income).

Awaiting the user's go-ahead to push kernel v9 (CPU, est. ~3.5 h).

## 2026-09-03 — Independent review of E06 predeclaration + notebook v7 (Cursor)

Reviewed commits `b0beece` (ledger/EDA predeclare) and `7073d98`
(notebook v7). Checked predeclaration order, feature construction, §9
submission guards, kernel metadata, and key quantitative claims against
local `data/` (source file not present locally).

**Verified:**

- Predeclaration order is correct: ledger E06 at `b0beece` precedes
  notebook v7 at `7073d98`.
- Local data reproduces the headline diagnostics in ledger E06 / EDA insights §10:
  13,214 distinct incomes; `30000` on 9.21% of rows; 0.58% of test
  incomes unseen in train; `astype(str)` keys are stable (match rate 1.0).
- `make_features(value_ids=True)` builds the intended v3 frame (18 cols;
  `_id` columns as object dtype); kernel copy matches
  `notebooks/02_baseline_modeling.ipynb`.
- `kernel-metadata.json` already attaches the source dataset
  (`itzzomkar/ev-adoption-behavior-and-range-anxiety`), so the
  `e06_cat_value_ids_src` arm will run on Kaggle.
- The new same-device submission floor (`STANDING_CHAMPION_OOF` +
  `SUBMIT_OK` in §9) matches the ledger text and closes the E04-class
  defect pattern (prose warning without a control). Stubbed control-flow
  checks: promoted-above-standing writes; promoted-below-standing does
  not; E05 screen never writes.
- `e06_cpu_base` is the right in-run comparator (single-seed
  `champion_factory` on interactions, expected 0.94204 per E05 Finding 3).

**Assessment — sound to run:**

- The hypothesis is well-motivated and honestly scoped: value identity is
  a *representation* change CatBoost's 254-border quantization cannot
  express, not a rehash of a closed axis.
- Falsifiable predictions (+0.0005 vs base, ±0.0002 between arms) and
  the stack-leak caveat in the ledger are proportionate.
- Source-income lookup uses source labels only (no competition-target
  fold handling needed); the generative identity argument is explicit.

**Nits / watch items (none blocking):**

1. **Dry-run is not reproducible from the repo.** The 2048/2048 and
   seven-scenario claims are plausible (11 flags → 2048; I stubbed
   control flow with zero exceptions), but there is no checked-in harness
   script — same gap as the E04 audit sweep. Consider committing a small
   stub test if this pattern recurs.
2. **`docs/3_implementation_plan.md` is stale** — §"Current state" still
   says "nothing predeclared" and omits E06; update after the run, not
   before.
3. **Two-bar outcome needs a predeclared follow-up.** If
   `e06_cat_value_ids` clears the paired gate vs `e06_cpu_base` but sits
   below 0.94223, §9 correctly writes no submission — but no E07
   seed-average of the v3 config is predeclared yet. Decide that *before*
   reading results, not after a promising evidence-only run.
4. **Runtime risk:** 13k-cardinality income categoricals may cost more
   than the ledger's 1.3× estimate; the 4 h budget still looks safe on
   CPU with only 2–3 fits.
5. **Carry forward unverified audit items** from 2026-09-02 (paired
   bootstrap construction, family-wise error across gates, `fold_std`
   ddof=0, unpinned `requirements.txt`) — unrelated to E06 but still open.

**Recommendation:** approve kernel v9 push. On return: fill ledger results,
E06 insight cell, manifest row only if `SUBMIT_OK` is True, and predeclare
any seed-average follow-up before interpreting an evidence-only promotion.

## 2026-09-03 — E06 lands: +0.00337, the largest gain of the project

Kernel v9 COMPLETE (2.93 h, three CPU fits). `e06_cat_value_ids`
**0.94541** vs baseline 0.94204: +0.00337, 5/5 folds, P(Δ>0) 1.000 —
against a predeclared threshold of ≥+0.0005. Champion is now
`e06_cat_value_ids_src` (0.94542) per the predeclared higher-OOF rule.

**Verification done before believing it**, because the jump is 26× the
noise floor and every prior step was ~0.0002:

- Re-ran the paired gate *outside* the notebook, from saved matrices,
  against the standing champion rather than the in-run baseline:
  +0.00318, 5/5, CI (+0.00305, +0.00332), P 1.000.
- Checked the gain is not memorization — it is positive across every
  frequency stratum holding 99% of rows, and negative only on singleton
  values (0.6% of rows).
- Confirmed test's value-frequency profile matches train's, and that OOF
  and test prediction distributions agree to 3–4 decimals.
- `e06_cpu_base` came back **bit-identical** to `e05_cpu_base` (third
  confirmation that CPU runs reproduce exactly across kernel versions).

**Two process notes worth a reviewer's attention.** First, the ideation
that produced this did *not* come from the multi-agent workflow — those
agents died on session limits twice — but from a 30-second local
diagnostic on column cardinality. Second, the notebook's new
`STANDING_CHAMPION_OOF` guard was exercised in the pass direction here
(0.94542 > 0.94223 → artifact written); the dry-run had already
confirmed the fail direction writes nothing.

**Status:** artifact validated (286,571 rows, 286,571 unique values,
range [0.0000036, 0.99983]). Not submitted — awaiting the user's
go-ahead. Plan reopened: seed-averaging and, for the first time, a
blend (correlation 0.9868 clears the 0.995 bar).

## 2026-09-03 — Post-E06 screens, then E07 predeclared and launched

Three ideas killed for free against saved OOF matrices, before spending
any compute (ledger "Free post-E06 screens"): blending with pre-E06
models (hurts at every weight — the 0.995 diversity bar is necessary but
not sufficient, since the partners are 0.0034 weaker), tracing rows back
to their source row (the generator resampled columns independently, so
multi-column keys match 1.7–8% of rows and add ±0.00001), and six
target-free derived features (all exactly ±0.00000).

User chose the sequenced plan: **E07** explore single-seed → **E08**
average the winner → **E09** 10-fold under a new fold definition F2.
Ordered so nothing is invalidated later: E03 proved averaging additive,
so averaging before the config is settled would be wasted compute.

E07 predeclared at `9765971` **before** the notebook change, as usual.
It re-opens capacity and encoding — axes E01/E04 closed against a
representation that lacked the value-identity signal, which is a stated,
scoped reason rather than a licence to re-run history; a null closes them
permanently.

**A bug the smoke check caught before it cost a run:** `SOURCE_FRAME`
was still guarded by `RUN_E05 or RUN_E06`, so with only E07 active the
source dataset never loaded and `X_v3s`/`X_v4` were never built — E07
would have printed "skipped" and fitted nothing for ~4 h of queue time.
This is precisely the enumerated-flag-list failure the standards already
warn about, recurring at a *second* site, so the fix derives it once
(`NEEDS_SOURCE`) next to `EXPERIMENT_ACTIVE` rather than patching the
instance.

Dry-run: **4096/4096** flag combinations clean, 12 scenarios pass
(5 new for E07: promotion above/below the standing floor, no promotion,
source missing, two-arm tie-break). Two older E06 scenarios failed at
first and were *stale tests, not bugs* — they encoded the old standing
champion (0.94223) and its name; behaviour was correct.

Kernel v10 launched (CPU, 4 fits, ~6.5 h predicted).

## 2026-09-04 — E07 null; E08 launched (averaging + an ungated test-time arm)

**E07: all three arms null, and my headline prediction was wrong.**
Capacity at 4000×0.025 returned **+0.00001** against a predeclared
"≥ +0.0002, most likely winner". By the rule I wrote before the run,
capacity is now closed permanently — E01's finding was about the problem,
not the feature set, and the "more signal rewards more capacity"
reasoning that justified re-opening it is falsified. All-value-ids
+0.00004 (correct call), `max_ctr_complexity=1` −0.00023 (correct call,
and it shows categorical combinations are real signal). Runtime
prediction also wrong: 7 h 31 m against "under 6.5 h". 2 of 4 right.

`e07_base` came back bit-identical to `e06_cat_value_ids_src` — fourth
consecutive CPU reproducibility confirmation.

**What E07 actually established:** the model is saturated on
*configuration*. Three independent knobs all move it less than the noise
floor, so the ~0.0008 gap to the leaderboard top is not a tuning problem
and should not be attacked with more configs.

**E08 therefore changes how the champion is fit, not what it is.**
Part A seed-averages it (E03 measured +0.00019 for this operation).
Part B is a test-time change with a real motive: E06's LB beat its OOF
by +0.00020, and the likely mechanism is that value-identity encodings
are target statistics — test rows get one from all 668,665 rows while
each fold model holds ~535,000. So Part B fits on all rows and predicts
test directly.

**Part B has no OOF and cannot be gated.** Rather than write a warning,
it lives in a separate `fulldata_test_store` that the gate, champion
selection and the submission cell structurally cannot read, and it emits
`submission_fulldata.csv` on its own path. The dry-run asserts exactly
that property (E08 scenario B: absent from `test_store`, absent from
`gate_results`, own artifact present). It will be decided by a paired
leaderboard comparison — valid here because the two models are
near-identical and scored on the same rows — at a cost of 2 of 10 daily
submissions, and the prediction (+0.0001…+0.0003) is on record so the
manifest's explanation of the +0.00020 gap is falsifiable.

Dry-run: **8192/8192** flag combinations clean, 17 scenarios pass. One
initial failure was a wrong assertion of mine (the average is registered
by `register_average`, not `run_cv`), not a notebook defect.

Kernel v11 launched (CPU, 4 CV fits + 3 full-data fits, ~5.2 h predicted
— budgeted with E07's corrected cost figure).

## 2026-09-04 — E08 results, two failed magnitude predictions, E09 launched

**E08 Part A promoted** (`e08_avg3seeds` 0.94550, public **0.94565**) —
new champion, submission 5. **Part B won the paired LB comparison**
(0.94569, submission 6) and was **not promoted**: +0.00004 is below the
noise floor, and a single LB comparison at that margin is exactly what
the gate exists to refuse.

**Both magnitude predictions failed.** Part A: +0.00007 against a
predicted +0.00019, which was *below the falsification threshold I wrote
into the predeclaration*, so E03's additivity result is recorded as NOT
generalising across representations. Part B: +0.00004 against a predicted
+0.0001…+0.0003. Directions right both times, magnitudes ~3× too large.
E09's predictions are deliberately scaled down as a result.

**Two findings worth more than the gains.**

1. **The noise floor collapsed from 0.00013 to 0.00005.** Three seeds
   span 0.00005 where they spanned 0.00013 pre-E06. Value identities are
   deterministic, so they replace seed-sensitive tree structure with
   seed-stable encoding — which explains both the smaller averaging gain
   and why that gain is still real. Re-checked every prior "below the
   noise floor" dismissal against the lower bar; none flip.
2. **I had the LB>OOF explanation wrong and Part B corrected it.** I
   attributed the +0.00020 gap to test-time value statistics using 668k
   rows vs ~535k per fold. Isolating that mechanism measures it at
   **+0.00004** — a fifth of the gap. The larger share is that each OOF
   row is predicted by *one* model while each test row is predicted by
   the average of every fold model (15 here). `docs/5_submission_manifest.md`
   is corrected.

**E09 launched** (kernel v12): 10-fold under a new fold definition F2.
Better motivated than when planned, since it improves both effects E08B
separated. The comparability rule is enforced as a **mechanism**:
`paired_gate` asserts both runs share a fold definition,
`register_average` refuses members spanning classes, and §9 filters
promoted candidates to the champion's class — so an F2 run can be
promoted within F2 yet structurally cannot take the gated submission
slot. It writes its own `submission_f2.csv`, decided by leaderboard.

**A bug the dry-run caught:** `BASELINE_CHAMPION` had not been repointed
after E08's promotion — it still named `e06_cat_value_ids_src` with the
old 0.94542 floor, so v10 would have gated against a superseded champion
and used a stale submission floor.

Dry-run: **16384/16384** flag combinations clean, 21 scenarios pass, plus
a direct negative test proving the cross-class gate and average both
raise (and that a same-class gate still works). Two initial failures were
stale expectations of mine, not defects.

## 2026-09-04 — Kernel v12 ERRORED: the enumerated-flag bug, third occurrence

`NameError: X_v3s` ~10 minutes in, at E09's first fit. The guard building
the value-identity frames read `if (RUN_E06 or RUN_E07 or RUN_E08)` and
was never updated for E09 — the same failure mode as the `SOURCE_FRAME`
guard I fixed two runs ago, at a *different* site I did not check.

**Why the dry-run missed it, which is the part worth keeping.** The
harness pre-defines `X_v3s` and every other frame so it can sweep 16,384
flag combinations cheaply. That injection is exactly what §2 was failing
to do, so the harness was structurally blind to the bug: **a stub that
supplies the artefact under test cannot test whether it exists.** All
16,384 combinations passed a notebook that could not run.

The E07 version of this bug was caught by a *smoke check* that executes
the real §2 against local data. I ran that for E07 and skipped it for
E09 — so the safeguard existed and I failed to apply it.

**Structural fixes rather than another patch:**

- Guard derived once as `NEEDS_VALUE_ID_FRAMES`, beside `NEEDS_SOURCE`
  and `EXPERIMENT_ACTIVE`.
- New `scripts/check_frames.py` executes the real Config and Data cells
  per experiment flag and statically resolves every frame name that
  experiment references. It reproduces the failure on the old notebook
  and passes on the fixed one, and it now covers **all twelve**
  experiment configurations — not just the one being pushed. Its first
  run also surfaced two false-positive classes (names assigned inside
  the cell), now handled.
- Recorded in `docs/0_coding_standards.md` as a rule about harness
  design, not just about this guard.

Cost: ~10 minutes of Kaggle compute, no submission wasted, no data lost.
Cheap for the lesson, but it is the third instance of one bug class.

## 2026-09-04 — E09 complete: 10-fold is worth +0.00014 on OOF

Kernel v13 (v12's re-run after the `NameError` fix) finished in 5.2 h.
`e09_f2_avg3seeds` F2 OOF **0.94564**, promoted within F2 (9/10 folds,
P 1.000). Cross-class observation, same config and seed with only the
fold count differing: **+0.00014** (CI +0.000093…+0.000196), recorded as
an observation because it is biased toward F2 by construction.

**The comparability mechanism was exercised for real and held.** The run
printed that the F2 candidate was promoted in-class but ineligible to
displace the F1 champion, wrote no `submission.csv`, and emitted only
`submission_f2.csv`. Champion unchanged at `e08_avg3seeds`.

Predictions: 1 correct and inside its band (+0.00014 vs +0.00008…+0.00020
— the first magnitude prediction to land, after deliberately scaling down
from E08's 3× misses), 1 indistinguishable (averaging gain under F2 vs
F1: +0.000073 vs +0.000074, so the reasoning that 10-fold leaves less
seed variance to remove is *not* supported), 1 wrong (runtime 5.2 h
against 7.7 h predicted — over-corrected after under-estimating E07),
1 pending on the leaderboard.

Also fixed a cosmetic defect the F2 run exposed: the gate printed
"fold wins 9/5" because the denominator was hardcoded. It now reads the
run's fold definition. Re-verified afterwards: `check_frames.py` ok on
all 12 configurations, 16384/16384 dry-run combinations, 21 scenarios.

## 2026-09-04 — Submission 7 scored; then a full repo audit and cleanup

**Submission 7** (`e09_f2_avg3seeds`, kernel v13): public **0.94570**,
+0.00005 over the champion and **inside** the predicted +0.00003…+0.00012
band. Standing 186/699. "Champion" and "best submission" now deliberately
name different artifacts — `e08_avg3seeds` holds the gated title in class
F1, while the better public score lives in class F2 and cannot be gated
against it.

**Five free screens, all null** (~10 min of local compute, vs ~5 h for a
speculative kernel run): no train/test duplicate rows, no `id` signal,
joint value identities too sparse, artifact blending +0.000008, and — the
most promising idea — a decorrelated LightGBM partner that stays 0.0033
behind even with leak-free nested target encoding. That last screen
produced a genuinely useful fact: **naive target encoding hurts
(−0.00264) because a training row's encoding contains its own label;
nested encoding recovers +0.00433.** That is exactly what CatBoost's
ordered target statistics do automatically, and it explains CatBoost's
dominance here better than "it is a better booster" does.

**Repo audit (subagent) — findings verified by hand before acting.**
Two were materially wrong, not merely stale:

1. **`docs/7` claimed the source dataset "is not used by the champion and
   will not be used in any submission."** False since E06: the champion is
   fit on features v3 **plus** the source income lookup, and four of seven
   submissions depend on it — so the CC0 citation obligation was live
   while the doc said it wasn't. Corrected, with the superseded sentence
   quoted so the error stays visible.
2. **The gate's fold-win threshold was the literal `3`.** Correct under
   F1, but under F2 it meant 3 of 10 — a far weaker bar than the gate was
   ever meant to impose. Now derived as `n_splits // 2 + 1` (3 under F1,
   6 under F2) and predeclared in the ledger. E09's 9/10 clears either
   way, so no recorded result changes.

Also fixed: a blank line that split the submission manifest into two
tables and left rows 4–7 without headers; three different champions named
in one section of the plan; `AGENTS.md` still leading with "the source
dataset is unidentified"; a **public** notebook cell naming
`e01_cat_2000x05` as champion and an empty E09 insight placeholder;
`README` frozen at E03; `requirements.txt` unpinned (now pinned to the
kernel-v13 versions, an audit item open since 2026-09-02); `.gitignore`
missing the two new submission artifacts; a `push_kaggle_kernel.sh`
target pointing at a directory that never existed; the reproducibility
snapshot omitting **catboost**, the one library that produces the
champion; and ambiguous `EDA §N` citations that resolved against two
different numbering schemes.

Deleted `notebooks/submission.csv` — a 7.9 MB pre-E01 artifact, three
representations and seven submissions out of date.

Verified after: `check_frames.py` ok on all 12 configurations,
16384/16384 dry-run combinations, 21 scenarios, and a targeted test that
the new threshold is 3 under F1 and 6 under F2.

## 2026-09-04 — A user question surfaced a champion-re-fit defect

Asked what would happen if the notebook were run to produce a submission.
Checking rather than answering from memory found a real defect, and the
answer would have been wrong if I had guessed.

**The defect.** §5's champion re-fit ran
`run_cv(BASELINE_CHAMPION, champion_factory, X_int, X_test_int,
cat_features=BASE_CATEGORICALS)` under the comment *"Only valid when
BASELINE_CHAMPION names a single-model config"*. Since E08 the champion
is `e08_avg3seeds` — a **3-seed average on features v3 + source lookup**.
So `RUN_CHAMPION=True` with no experiment active would have:

1. fit a **single** model, not the 3-seed average;
2. on `X_int` — the **pre-E06 frame, missing the value identities worth
   +0.00337**;
3. registered it under the average's name; and
4. written `submission.csv` from it, with `SUBMIT_OK` True.

Confirmed by running that exact configuration through the dry-run: one
fit, champion `e08_avg3seeds`, `submission.csv` written. A submission
about **0.0034 worse than the champion, labelled as the champion**.

**Why the existing tests missed it.** The 16,384-combination sweep checks
that no combination raises. This one raised nothing — it quietly did the
wrong thing. A sweep for exceptions is not a correctness test.

**The fix.** The champion's composition is now data next to the pointer
(`CHAMPION_SEEDS`, `CHAMPION_IS_AVERAGE`, reusing `CHAMPION_FOLDS`), and
§5 reproduces it faithfully — three seeds, features v3 + source lookup,
fold class F1 — or refuses when the source dataset is absent, instead of
silently substituting a different model. `CHAMPION_REFIT` is derived once
and feeds `NEEDS_SOURCE` / `NEEDS_VALUE_ID_FRAMES` so §2 builds the
frames it needs.

Three champion-re-fit scenarios are now permanent dry-run cases asserting
*what is fit and what is written*: reproduces all three seeds and writes
a submission; refuses with no artifact when the source is missing; stands
down when an experiment is active. Full suite after the fix: 16384/16384
combinations, 24 scenarios, `check_frames.py` ok on all 12 configurations.

Recorded in `docs/0_coding_standards.md` as the third instance of
"a precondition in prose is not a precondition".

## 2026-09-05 — R1: champion reproduces bit-identically from the current notebook

Kernel v14, 3 h 30 m. All three predeclared predictions confirmed:

1. **Bit-identical.** Eight vectors (4 runs × OOF/test) all
   `np.array_equal` True against kernel v11; OOF AUC matches to 16
   decimal places (0.9454983185241117).
2. **Artifact byte-identical.** `sha256(submission.csv)` is
   `aba17f9fe8e08631…` in both runs, so re-submitting would score exactly
   0.94565. No submission made — the hash is better evidence than a
   quota slot.
3. **Runtime** 3.42 h of fitting against a predicted ~3.5 h.

The point of this run was not a sixth reproducibility data point. It
proves the champion is reproducible **from the notebook as it stands
today**, not merely from the historical version that produced it — and it
is the first exercise on real compute of the repaired §5 path, which
under notebook v10 would have written an artifact ~0.0034 worse under the
champion's name. The pinned `requirements.txt` also matches the Kaggle
worker exactly, and `catboost 1.2.10` now appears in the snapshot.

**Project state: search closed, reproduction verified, one action left** —
selecting the final two submissions in the Kaggle UI (no API command
exists) before 2026-09-30 23:59 UTC. Recommendation and reasoning are in
`docs/5_submission_manifest.md`.

## 2026-09-05 — E10 closes the search, and exposes a flaw in my own screening

Kernel v15, 5 h 10 m. Nothing promoted. `e10_onehot10` −0.00006 (but
**33% faster**); `e10_ctr_binarized` and `e10_ctr_comb` **bit-identical**
to the baseline.

**The bit-identity is the story.** Two arms did not produce a null
result — they produced *no variation at all*. Diagnosed locally instead
of guessed: CatBoost accepted and recorded the parameter change
(`get_all_params()` shows `BinarizedTargetMeanValue` replacing `Borders`),
yet predictions matched to the last bit, while a known-effective control
(`max_ctr_complexity=1`) changed them. Cause: for a **binary target with
`TargetBorderCount=1`**, "binarized target mean" and "Borders CTR over
one border" are algebraically the same quantity; and
`combinations_ctr=["Borders","Counter"]` is already CatBoost's default,
so that arm set a parameter to itself.

That makes the CTR-estimator sub-axis **degenerate rather than null** —
a stronger claim, and one that rules out any follow-up on it.

**My screening was at fault, and the lesson generalises.** The pre-run
smoke test verified each config was *accepted* (and correctly rejected an
invalid `FeatureFreq` arm). It never verified an accepted config
*changed the predictions*. So ~2.8 h of compute re-measured the baseline
twice. **A validity check is not a variation check** — recorded in
`docs/0_coding_standards.md`; the fix is to fit two tiny models and
assert the outputs differ before committing to a kernel run.

Predictions: 1 correct (all within ±0.0002, none promoted), 1 **vacuous**
and not counted (a no-op arm could not have promoted), 1 correct by a
wide margin (one-hot ≥5% faster → measured 33%), 1 wrong (5.12 h vs
"under 5 h").

**The search is now closed.** E10 was the last untested axis. Champion
`e08_avg3seeds`, best submission `e09_f2_avg3seeds` at public 0.94570.
The only outstanding action is selecting the final two submissions in the
Kaggle UI before 2026-09-30 23:59 UTC.

## 2026-09-05 — Overlap audit acted on; the 2026-09-02 audit's open items finally dispositioned

A second subagent audit (overlap and lane discipline, distinct from the
2026-09-04 staleness audit) found one live contradiction and a structural
cause for the recurring staleness; both are fixed:

- **The contradiction:** `docs/5` still declared the blend path
  "no longer closed" while the ledger's free screens had measured every
  blend as negative and closed it. The manifest now points at the ledger
  instead of restating model behaviour — that bullet was also a lane
  violation, which is *why* it rotted.
- **The structural cause:** the champion/state block was hand-maintained
  in five files, and `AGENTS.md` had gone stale *again* within one day of
  being fixed (it still said "E01–E09, 7 submissions" with E10, R1 and
  the stacking screen missing). AGENTS.md and README now carry one
  orienting line plus pointers; `docs/3` owns current state, the ledger
  owns numbers. AGENTS.md says explicitly not to widen it again.
- Also: `docs/2`'s superseded baseline plan cut to a pointer and its
  "every number below" claim scoped to §§1–8; `docs/3`'s duplicate
  blending rows, duplicate Phase-4 headings and stitched status merged
  (the early "Final Week" plan is subsumed — its items landed three
  weeks early); `docs/0`'s incident narratives compressed to rules with
  dated pointers here, and the superseded GPU-framing block replaced by
  the measured rule; the `01_`/`02_` notebook naming declared in docs/0
  as a deliberate deviation from master §2 (the master itself says not
  to renumber, and the names are load-bearing).

**The 2026-09-02 audit items that were never closed, now dispositioned:**

1. **Paired-bootstrap construction — verified, closed.** The gate has
   since been re-implemented independently twice (the local fast-AUC
   harness that reproduced all seven historical gate results to the
   quoted digits on 2026-09-02, and the from-scratch re-gates of E06 and
   E08 against saved matrices), with matching CIs and P values each
   time. Two independent implementations agreeing is the verification
   the audit asked for.
2. **Family-wise error across many 95% gates — acknowledged as an
   accepted limitation, not corrected.** No formal multiplicity
   correction is applied. In mitigation: promotion requires majority
   folds AND CI>0 AND P≥0.95 jointly; the one near-threshold case
   (E07's `e07_all_value_ids`, P=0.954) was refused by the CI criterion,
   which is the mechanism working; and every promotion was subsequently
   confirmed on the leaderboard. With the search closed, retrofitting a
   correction would change no decision.
3. **`fold_std` ddof=0 — closed 2026-09-04** when the code was annotated:
   it is deliberately the population std of the observed fold scores, a
   description of the run's spread, never used by the gate.
4. **Unpinned `requirements.txt` — closed 2026-09-04** (pinned to the
   kernel-v13 environment, confirmed against kernel v14's snapshot).

Also today: the first render pipeline in any sibling repo —
`scripts/render_pdf.py` (pandoc → styled HTML → headless Chrome; no
LaTeX dependency) renders all docs plus both notebooks to `renders/`
(gitignored), with a combined `all_docs.pdf`. Notebooks render from
source; `--execute-eda` optionally executes the EDA locally for outputs
(the modeling notebook is never executed locally). One defect found and
fixed in review: pandoc's `title` metadata double-titled every page;
`pagetitle` sets the browser title without the duplicate heading.

## 2026-09-05 — Notebook renamed to what it is; second refinement pass

**`02_baseline_modeling.ipynb` → `02_modeling.ipynb`**, on the user's
question and against my own earlier "declare, don't rename" lean. The
distinction that settled it: the master standard's no-churn rule targets
*renumbering*; here the number stays and only a descriptor that stopped
being true changes — "baseline" described week one of a notebook that
came to hold E01–E10, and the standard's operative rule is that names
describe the workflow performed. What deliberately does **not** change:
the Kaggle kernel slug `ev-purchases-baseline-modeling`, since changing
it would abandon versions 2–15, which the submission manifest cites. The
kernel's *display title* becomes "EV Purchases - Modeling"; the slug is
declared historical in docs/0. Updated in the same commit: kernel dir
(`kernels/modeling/`), metadata `code_file`, push script (new target
`modeling`, `baseline` kept as an alias), `check_frames.py`, and every
live doc reference — dated log/ledger entries keep the historical name,
which was accurate when written.

Refinement pass alongside: `predictions/README.md` and `data/README.md`
grew from one-liners into actual orientation (naming scheme, alignment
guarantee, provenance rule; what each data file is). Verified the
`seaborn==0.13.2` pin I had written without checking — it matches both
the local env and the executed EDA kernel. Noted in passing that the EDA
kernel ran a newer image (numpy 2.4.6) than the modeling kernel (2.0.2);
`requirements.txt` correctly pins the modeling environment, the one the
champion depends on.

Verified after the rename: `check_frames.py` ok on all configurations,
32768/32768 dry-run combinations. The public kernel still displays v15
(pre-refinement markdown, E10 insight placeholder); a push of the
current notebook would fix the public face and validate the renamed
pipeline end-to-end, at the cost of one ~3.5 h champion-refit run.

## 2026-09-05 — Kernel v16: renamed pipeline republished, and a wrong claim of mine corrected

Pushed the refined notebook (v13) to fix the public kernel, which was
still showing pre-refinement markdown with E10's insight as a literal
placeholder. Two outcomes, one of them a correction.

**The correction: the kernel slug was NOT immutable.** Hours earlier I
wrote in `docs/0` that changing the title would abandon versions 2–15,
and kept the historical slug on that basis. Pushing the new title made
Kaggle **re-slug the kernel to `ev-purchases-modeling` while preserving
the entire version lineage** — the push landed as v16 immediately after
v15, and the old slug now 404s on the API. So the rename produced full
name coherence (file, title, slug) with history intact, which is better
than what I predicted, but the assumption was wrong and was already
written into three places. Fixed all three: `kernel-metadata.json` still
pointed at the dead slug and would have forked a brand-new kernel with
no history on the next push; `docs/0`'s deviation note now records what
actually happened rather than the assumption; README's commands use the
live slug. Manifest rows keep the old slug — they record commands as
actually run — with a note saying where those versions live now.

**Eighth consecutive bit-identical reproduction.** v16 ran the champion
re-fit through the *renamed* pipeline and returned all eight vectors
`np.array_equal` True against R1's (kernel v14), with
`sha256(submission.csv)` matching at `aba17f9fe8e08631…`. The rename
touched the notebook filename, kernel directory, metadata, push script
and `check_frames.py`, and changed nothing about the model — which is
exactly the evidence a refactor of that surface needs.

**State unchanged:** champion `e08_avg3seeds` (public 0.94565), best
submission `e09_f2_avg3seeds` (public 0.94570). No submission from this
run — the artifact is byte-identical to submission 5. The public kernel
now shows the finished work at
`kaggle.com/code/tuannm3812/ev-purchases-modeling`.

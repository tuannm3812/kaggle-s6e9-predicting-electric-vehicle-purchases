# Submission Manifest

Every leaderboard submission, recorded the moment it is scored, per
`docs/0_coding_standards.md`. One submission per accepted hypothesis.

| # | Date (UTC) | Sub id | Kernel / version | Model | OOF AUC (fold def. noted) | Public LB | Hypothesis → verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-01 13:19 | 55940961 | `ev-purchases-baseline-modeling` v2 | `e01_cat_2000x05` | 0.94177 (Kaggle run; 0.94176 local) | **0.94169** | CV tracks LB (EDA no-drift evidence) → **confirmed**: gap −0.00008, well inside fold std (~0.0007) |
| 2 | 2026-09-01 19:27 | 55946584 | `ev-purchases-baseline-modeling` v3 | `e02_cat_interactions` | 0.94204 (Kaggle run) | **0.94198** | subsidy crosses improve the champion (E02, paired-gate promoted) → **confirmed**: LB +0.00029 vs. OOF +0.00027; CV↔LB gap −0.00006 |
| 3 | 2026-09-02 02:02 | 55951839 | `ev-purchases-baseline-modeling` v4 | `e03_cat_int_avg5seeds` | 0.94223 (Kaggle run) | **0.94210** | interactions + seed-averaging are additive (E03) → **confirmed**: predicted OOF 0.94220, 3-seed delivered 0.94220 exactly; LB +0.00012 for OOF +0.00019 |
| 4 | 2026-09-03 11:48 | 55980494 | `ev-purchases-baseline-modeling` v9 | `e06_cat_value_ids_src` | 0.94542 (Kaggle run) | **0.94562** | exact numeric values are identities the champion could not see (E06, paired-gate promoted 5/5, P=1.000) → **confirmed**: LB +0.00352 for OOF +0.00319; first positive CV↔LB gap (+0.00020) |
| 5 | 2026-09-04 04:41 | 56004792 | `ev-purchases-baseline-modeling` v11 | `e08_avg3seeds` (gated) | 0.94550 | **0.94565** | 3-seed averaging still pays on the new representation (E08A, promoted 5/5) → **confirmed but far smaller than predicted**: +0.00007 OOF vs +0.00019 predicted; CV↔LB gap +0.00015 |
| 6 | 2026-09-04 04:41 | 56004795 | `ev-purchases-baseline-modeling` v11 | `e08_fulldata_avg3` (**ungated**, no OOF) | — | **0.94569** | full-data refit improves test-time value statistics (E08B) → **direction confirmed, magnitude wrong**: +0.00004 vs +0.0001…+0.0003 predicted. Not promoted — below the noise floor |
| 7 | 2026-09-04 13:12 | 56013125 | `ev-purchases-baseline-modeling` v13 | `e09_f2_avg3seeds` (**cross-class**, F2/10-fold) | 0.94564 (F2 — not comparable to F1 rows) | **0.94570** | 10-fold beats 5-fold at test time (E09) → **confirmed, +0.00005, inside the predicted +0.00003…+0.00012** |

## Notes

- Submitted via the kernel-version flow (`-k tuannm3812/ev-purchases-baseline-modeling -v 2`),
  so the score is tied to code Kaggle executed (master standard §11).
  Every artifact is pre-validated with `scripts/verify_submission.py`
  (checks listed once, in `docs/0_coding_standards.md`) — 286,571 rows
  each; submission 7's range is [0.0000047, 0.99979].
- Quota use: 7 across 4 days. **Five** were backed by a paired-gate
  promotion in the F1 class (1–5). **Two are deliberate exceptions**,
  each predeclared with a falsification threshold before submission:
  submission 6 (`e08_fulldata_avg3`) is ungated because no OOF exists
  for a full-data refit, and submission 7 (`e09_f2_avg3seeds`) is
  cross-class because an F2 OOF cannot be gated against an F1 champion.
- Standing (mutable, re-check live): 79/157 → 83/227 → 106/280 →
  130/531 → 166/624 → **186/699** (26.6th percentile, snapshot
  2026-09-04; leader 0.94656, gap 0.00086). The field is dense here:
  a further +0.0001 would move roughly 10 places.
- **"Champion" and "best submission" now name different artifacts**, and
  deliberately so. `e08_avg3seeds` (0.94565) is the champion — the
  designation earned through a paired OOF gate. `e09_f2_avg3seeds`
  (0.94570) is the best public score, but lives in fold definition F2
  and cannot be gated against an F1 champion. Both are candidates for
  the final two-submission selection. The *rank number* rises while the
  score improves because the field grows fast; percentile moved
  ~37% → ~24% on E06 and holds. Rank is not evidence about the model —
  the OOF/LB deltas are.
- **CV↔LB tracking holds across all six OOF-backed submissions**: gaps
  −0.00008, −0.00006, −0.00013, +0.00020, +0.00015, +0.00006 (the last
  being submission 7's F2 OOF 0.94564 → 0.94570, an in-class gap).
  Submission 6 has no OOF and so no gap. The sign flipped at E06 and
  stayed positive.
- **The sign flip's cause was corrected by E08B** (2026-09-04): mostly a
  construction asymmetry (each OOF row is one model's prediction, each
  test row an average of all fold models), with the data-volume effect
  measured at only +0.00004. Full analysis: `docs/4_experiment_ledger.md`,
  E08 results. Keep gating on OOF; do not read the positive gap as free
  accuracy.
- Decision: `e08_avg3seeds` is the champion; `e08_fulldata_avg3` scored
  higher (0.94569) but is unpromoted. Any further submission needs a new
  paired-gate promotion. *(An earlier bullet here declared the blend path
  re-opened on E06's 0.9868 correlation; the free screens then measured
  every blend weight as negative and closed it for good. The ledger is
  canonical on model behaviour — this doc points there instead of
  restating it.)*

## Final submission selection (decided 2026-09-04, act before 2026-09-30)

Kaggle scores two selected submissions against the private leaderboard.
**This is a UI-only action** — the Kaggle CLI has no command for it
(`kaggle competitions` exposes submit/submissions/leaderboard and nothing
for selection), so it must be done by hand on the competition's My
Submissions page. If nothing is selected, Kaggle defaults to the best
public scorers, which happens to be close to the recommendation below —
but relying on that default is not the same as deciding.

**Recommended pair:**

| Slot | Submission | Public LB | Why this one |
| --- | --- | --- | --- |
| 1 | **7** — `e09_f2_avg3seeds` | 0.94570 | Best public score, and the best-evidenced model: promoted 9/10 folds within F2, with each of its 10 fold models trained on ~602k rows and each test row an average of 10 models |
| 2 | **5** — `e08_avg3seeds` | 0.94565 | The gated champion in class F1, promoted 5/5 folds. An independent validation lineage on a different fold partition, so its errors are not the same errors |

**Why not submission 6** (`e08_fulldata_avg3`, 0.94569, the middle
score): it has **no out-of-fold validation at all** — that is the whole
reason it was never promoted. Picking it over the gated champion would
mean preferring a 0.00004 public-LB margin, itself below the 0.00005
noise floor, to the only evidence that generalises. The pair above trades
a hair of public score for the two artifacts with real validation behind
them.

**Honest caveat on hedging.** All three candidates correlate 0.9996–0.9999
on test predictions, so any pair hedges very little; their private scores
will land within noise of each other. The choice is close to immaterial,
and saying so is more useful than dressing it up as a strategy.

# Submission Manifest

Every leaderboard submission, recorded the moment it is scored, per
`docs/0_coding_standards.md`. One submission per accepted hypothesis.

| # | Date (UTC) | Sub id | Kernel / version | Model | OOF AUC (F1) | Public LB | Hypothesis → verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-01 13:19 | 55940961 | `ev-purchases-baseline-modeling` v2 | `e01_cat_2000x05` | 0.94177 (Kaggle run; 0.94176 local) | **0.94169** | CV tracks LB (EDA no-drift evidence) → **confirmed**: gap −0.00008, well inside fold std (~0.0007) |
| 2 | 2026-09-01 19:27 | 55946584 | `ev-purchases-baseline-modeling` v3 | `e02_cat_interactions` | 0.94204 (Kaggle run) | **0.94198** | subsidy crosses improve the champion (E02, paired-gate promoted) → **confirmed**: LB +0.00029 vs. OOF +0.00027; CV↔LB gap −0.00006 |
| 3 | 2026-09-02 02:02 | 55951839 | `ev-purchases-baseline-modeling` v4 | `e03_cat_int_avg5seeds` | 0.94223 (Kaggle run) | **0.94210** | interactions + seed-averaging are additive (E03) → **confirmed**: predicted OOF 0.94220, 3-seed delivered 0.94220 exactly; LB +0.00012 for OOF +0.00019 |

| 4 | 2026-09-03 11:48 | 55980494 | `ev-purchases-baseline-modeling` v9 | `e06_cat_value_ids_src` | 0.94542 (Kaggle run) | **0.94562** | exact numeric values are identities the champion could not see (E06, paired-gate promoted 5/5, P=1.000) → **confirmed**: LB +0.00352 for OOF +0.00319; first positive CV↔LB gap (+0.00020) |

## Notes

- Submitted via the kernel-version flow (`-k tuannm3812/ev-purchases-baseline-modeling -v 2`),
  so the score is tied to code Kaggle executed (master standard §11).
  Artifact pre-validated with `scripts/verify_submission.py` (286,571 rows,
  range [0.0000, 0.9893]).
- Quota use: one submission per promotion, never per tweak — 4 used
  across 4 days, each backed by a paired-gate promotion.
- Standing (mutable, re-check live): 79/157 → 83/227 → 106/280 →
  **130/531** (24.4th percentile, snapshot 2026-09-03 11:49 UTC). The
  *rank number* rose while the score improved because the field is
  growing fast; percentile moved ~37% → ~24% on E06. Rank is not
  evidence about the model — the OOF/LB deltas are. Leader 0.94644;
  0.94562 sits ~0.0008 back, and the 95th-place score is 0.94602, so
  the field is dense here — small real gains still move rank a lot.
- **CV↔LB tracking holds across all four**, but the sign flipped on
  E06: gaps −0.00008, −0.00006, −0.00013, **+0.00020**. The first three
  were slightly pessimistic; E06's LB *beat* its OOF. The likely cause
  is mechanical rather than luck: the value-identity target statistics
  for test rows are computed from all 668,665 training rows, while each
  OOF fold's statistics came from only ~535k. More rows per category
  means a better-estimated encoding at test time, so OOF is a mild
  *under*-estimate for this feature family specifically. Treat future
  value-id OOF numbers as a floor, and keep gating on OOF regardless —
  it stayed directionally right, which is what the gate needs.
- Decision: `e06_cat_value_ids_src` is the champion and the current
  final answer. Next submission only after a new paired-gate promotion.
  The blend path is **no longer closed** — E06's OOF correlates 0.9868
  with the pre-E06 models, the first pair under the 0.995 diversity bar
  (`docs/4_experiment_ledger.md`, E06 Finding 6).

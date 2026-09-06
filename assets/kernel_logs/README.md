# Archived Kaggle run logs

The raw console log of each Kaggle kernel run behind a ledger row —
unmodified, exactly as `kaggle kernels output` returned it. These are the
**primary evidence** for the results in `docs/4_experiment_ledger.md`:
fold AUCs, gate verdicts, wall-clocks, sanity checks and the full
reproducibility snapshot. `scripts/render_pdf.py --with-kernel-log`
renders one as an "Executed output" appendix.

| File | Kernel | Notebook | What it recorded |
| --- | --- | --- | --- |
| `kernel_v09_E06_value_identities.log` | v9 | v7 | E06 — +0.00337, the project's one large gain |
| `kernel_v10_E07_capacity_encoding.log` | v10 | v8 | E07 — all arms null; capacity closed |
| `kernel_v11_E08_averaging_fulldata.log` | v11 | v9 | E08 — averaging +0.00007, full-data refit |
| `kernel_v13_E09_ten_fold.log` | v13 | v10 | E09 — 10-fold under fold definition F2 |
| `kernel_v14_R1_champion_reproduction.log` | v14 | v11 | R1 — bit-identical champion reproduction |
| `kernel_v15_E10_ctr_type.log` | v15 | v12 | E10 — two arms degenerate, search closed |
| `kernel_v16_republish_champion_refit.log` | v16 | v13 | Republish after the rename; eighth bit-identical reproduction |

## Why these are archived rather than re-fetched

**`kaggle kernels output <owner>/<kernel>/<version>` silently ignores the
version and returns the latest run** (verified 2026-09-07: requests for
versions 9, 11 and 13 all returned kernel v16's log). The CLI's own help
advertises the `<version>` suffix, so this fails in the worst way — no
error, just the wrong run's numbers under a historical label. A run's log
is therefore only obtainable while it is the latest, which is why these
were captured at the time and committed here.

Runs before kernel v9 (v1–v8, covering v1/v2 baselines and E01–E05) were
not archived before their logs became unreachable. Their results are
recorded in the ledger, but the raw logs are gone.

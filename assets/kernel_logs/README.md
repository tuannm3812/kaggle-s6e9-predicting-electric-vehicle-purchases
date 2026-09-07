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
| `kernel_v18_selfexport_champion_refit.log` | v18 | v15 | First run carrying a working self-export; ninth bit-identical reproduction |

## Why these are archived rather than re-fetched

**No Kaggle route serves a past run's output.** Checked exhaustively on
2026-09-07, at the source level rather than by trial:

| Route | Result |
| --- | --- |
| `kernels output <kernel>/<version>` | Version silently dropped. The implementation splits the string and reads only `[0]`/`[1]`; `ApiListKernelSessionOutputRequest` has no version field. Requests for v9/v11/v13 all returned v16's log |
| `kernels pull <kernel>/<version>` | Same — the version element is never read |
| `ApiGetKernelRequest.version_number` | The field **exists**, and is ignored server-side: v9 and v15 returned byte-identical source, both stamped `v13`, with zero cell outputs |
| `kernels_list_files` | Only `/kaggle/working` of the latest run |
| The public kernel page | Client-rendered shell; no notebook content in the HTML |

`kernels pull` is worse than the table suggests: the **official docs
document** `owner/slug/version`, and the installed client (1.7.4.5)
accepts it, validates it, then builds `ApiGetKernelRequest` **without
ever setting `version_number`** — a documented flag the implementation
drops. Asking for a version can also 403 outright.

So the CLI advertises a suffix it does not honour: no error, just the
wrong run's numbers under a historical label. A log is therefore only obtainable **while its run is the latest**,
which is why these were captured at the time and committed here. Use
`scripts/archive_kernel_log.py` immediately after every run.

Runs before kernel v9 (v1–v8, covering v1/v2 baselines and E01–E05) were
not archived before their logs became unreachable. Their results are
recorded in the ledger, but the raw logs are gone.

## The one thing that *does* work: self-export

Kaggle will not hand over an executed notebook, but a running notebook
can export **itself**. Verified 2026-09-07 with a throwaway probe kernel:

- `/kaggle/working/__notebook__.ipynb` **exists during the run** and holds
  the outputs of every cell executed **so far**.
- `jupyter nbconvert --to html` on it succeeds inside the kernel, and
  anything written to `/kaggle/working` is returned by
  `kaggle kernels output`.
- The probe's HTML came back at 569 KB carrying printed stdout *and*
  rendered DataFrame tables.

**Copy the `.ipynb`, do not convert to HTML on Kaggle.** The first
attempt ran `nbconvert --to html` inside the kernel; the HTML came back
fine but is unusable downstream — it wraps code in JupyterLab's
CodeMirror markup, and converting that to markdown yields CSS class names
where the Python should be. Copying `__notebook__.ipynb` out is lossless
and lets the local pipeline convert it exactly as it converts source.

The constraint follows from "so far": the export cell must be the
notebook's **last**, and its own output is never in the file. This is
§10.2 of `notebooks/02_modeling.ipynb`; render with
`scripts/render_pdf.py --executed-notebook <file>`.

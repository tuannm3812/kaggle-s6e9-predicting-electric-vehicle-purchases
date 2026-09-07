#!/usr/bin/env python3
"""Render the project's docs and notebooks to PDF.

No sibling repo had a render pipeline when this was written (checked
S6E7, S6E8 and the master standard on 2026-09-05), so this is the first;
it deliberately uses only tools already on the machine — pandoc,
nbconvert, and headless Google Chrome for the HTML-to-PDF step — because
no LaTeX engine is installed and none should be required for this.

Pipeline (2026-09-07): markdown --pandoc--> Typst --typst--> PDF, adopted
from the sibling 36126-active-fire-research renderer. Typst buys three
things headless Chrome could not: a running header, page numbers, and
tables that paginate instead of being pushed whole to the next page.
Notebooks go through the same path via nbconvert's **markdown** export,
not its HTML: the HTML puts every cell behind an `In [ ]:` prompt gutter
that indents the whole document, while the markdown export drops the
prompts and emits plain ```python blocks that Typst highlights natively.
One pipeline, and the left margin back.

That project imports its template from a `uts-mdsi` repo which is not on
this machine, so `scripts/templates/project-doc.typ` is a fresh template
carrying THIS project's palette: DM Sans, and heading colours stepping
navy → viridis blue → green → muted grey, with lightness stepping too so
the levels survive greyscale. Also adopted: the `path @ commit (date)`
provenance stamp, which suits a project whose whole claim is that results
trace to a recorded source.

What it produces, under renders/ (gitignored):

    renders/docs/<name>.pdf        one PDF per markdown doc
    renders/docs/all_docs.pdf      docs 0-7 concatenated in reading order
    renders/notebooks/<name>.pdf   one PDF per notebook

Kaggle's API exposes no executed notebook — `kernels pull` returns source
with zero cell outputs, and the `__results__.html` a run builds is not
downloadable. Two ways to get real output in anyway, neither of which
executes anything locally (docs/0: runs happen on Kaggle):

  --executed-html    render a **Kaggle self-export**: the notebook's own
                     last cell converts `/kaggle/working/__notebook__.ipynb`
                     to HTML during the run, and anything in
                     /kaggle/working comes back via `kernels output`. This
                     carries real per-cell outputs, from the run that
                     produced the recorded results.
  --with-kernel-log  append the run's console log as an appendix. Coarser
                     than the self-export, but available for every
                     archived historical run.

Usage:
    python3 scripts/render_pdf.py --with-kernel-log --export   # the usual
    python3 scripts/render_pdf.py --executed-html out/executed_notebook.html
    python3 scripts/render_pdf.py --only docs     # or: notebooks
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RENDERS = REPO / "renders"
# Shared export convention (agreed 2026-09-05): rendered PDFs for ANY repo
# go to iCloud under 05_Projects/<category>/<repo>/, where <category> is
# the GitHub parent folder with its "N. " prefix stripped -- so
# "2. Kaggle/kaggle-s6e9-..." lands in "05_Projects/Kaggle/kaggle-s6e9-...".
# This mirrors the GitHub tree, so the same script works unchanged when
# copied into a sibling repo.
ICLOUD = (Path.home() / "Library" / "Mobile Documents"
          / "com~apple~CloudDocs" / "05_Projects")

# Print stylesheet shared by docs and notebooks. Kept small: readable
# serif body, monospace code that wraps instead of clipping, and tables
# that survive an A4 page.
# The palette and page furniture live in
# scripts/templates/project-doc.typ; the driver only needs the
# project label for the running header.
PROJECT = "S6E9 | Predicting Electric Vehicle Purchases"
# Markdown images whose source is a URL, optionally wrapped in a link.
REMOTE_IMAGE = re.compile(r"\[?!\[[^\]]*\]\(https?://[^)]*\)\]?(\([^)]*\))?")
LOCAL_IMAGE = re.compile(r"(!\[[^\]]*\])\(((?!https?://)[^)]+)\)")
LEADING_H1 = re.compile(r"\A\s*#\s+[^\n]*\n+")


def _typ_str(value: str) -> str:
    """Quote a Python string as a Typst string literal."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


DOC_ORDER = [
    "0_coding_standards.md", "1_instructions.md", "2_eda_insights.md",
    "3_implementation_plan.md", "4_experiment_ledger.md",
    "5_submission_manifest.md", "6_agent_log.md",
    "7_source_dataset_provenance.md", "8_model_comparison.md",
]


RUN_FLAG = re.compile(r'^(\s*)(RUN_[A-Z0-9_]+)\s*=\s*True\s*$', re.M)


def flags_off(notebook_json: str) -> str:
    """Set every RUN_* flag to False in a notebook's JSON source.

    Notebook source lives as JSON string lists, so the assignment appears
    as `"RUN_CHAMPION = True\n"`. Rewriting it here rather than editing
    the notebook keeps the committed file untouched.
    """
    return RUN_FLAG.sub(r"\1\2 = False", notebook_json)


def doc_title(source: Path) -> str:
    """The document's own H1, falling back to a tidied filename."""
    for line in source.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return source.stem.replace("_", " ").title()


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a build step, surfacing the tool's own error when it fails.

    Typst and pandoc explain their failures precisely; swallowing that
    into a bare CalledProcessError wastes the diagnosis they did.
    """
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise SystemExit(f"{cmd[0]} failed:\n{detail}")


def git_provenance(source: Path) -> str:
    """`path @ commit (date)` for one file — what this PDF was rendered from.

    Returns "" for a file outside the repo (a generated temp document has
    no history to stamp), rather than raising.
    """
    try:
        rel = source.relative_to(REPO)
    except ValueError:
        return ""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%h|%ad", "--date=short", "--", str(rel)],
            cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", str(rel)],
            cwd=REPO, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return str(rel)
    if not out:
        return f"{rel} (uncommitted)"
    commit, date = out.split("|", 1)
    return f"{rel} @ {commit}{'+dirty' if dirty else ''} ({date})"


def md_to_pdf(sources: list[Path], pdf: Path, title: str,
              kind: str = "Doc", provenance_for: Path | None = None) -> None:
    """Markdown (GitHub flavour) -> Typst via pandoc -> PDF."""
    template = REPO / "scripts" / "templates" / "project-doc.typ"
    fonts = REPO / "assets" / "fonts" / "dm-sans"
    with tempfile.TemporaryDirectory() as td:
        # Typst has no network access, so a remote image (the README's
        # shields.io badges) is a hard error. They are decorative status
        # chips that carry nothing in a PDF, so drop them rather than
        # vendoring PNGs of them.
        staged = []
        for i, src in enumerate(sources):
            text = REMOTE_IMAGE.sub("", src.read_text())
            # Local image paths are relative to the doc; Typst compiles
            # from a temp dir, so resolve them against the doc's own
            # directory and write them absolute.
            def absolutise(m, base=src.parent):
                target = (base / m.group(2)).resolve()
                return f"{m.group(1)}(<{target}>)" if target.exists() else m.group(0)
            text = LOCAL_IMAGE.sub(absolutise, text)
            # The template prints the title, so a leading H1 would show
            # it twice. Only the first doc of a concatenation loses its
            # H1 -- later ones are section titles within a collection.
            if i == 0:
                text = LEADING_H1.sub("", text, count=1)
            copy = Path(td) / f"{i:02d}_{src.name}"
            copy.write_text(text)
            staged.append(copy)
        body = Path(td) / "body.typ"
        # --resource-path lets ../assets/figures/... resolve from docs/.
        run([
            "pandoc", *map(str, staged), "-f", "gfm", "-t", "typst",
            "--wrap=preserve", f"--resource-path={REPO}:{REPO / 'docs'}",
            "-o", str(body),
        ])
        if provenance_for is not None:
            prov = git_provenance(provenance_for)
        elif len(sources) == 1:
            prov = git_provenance(sources[0])
        else:
            prov = ""
        main = Path(td) / "main.typ"
        main.write_text(
            f'#import "{template}": *\n'
            f"#show: doc => conf(project: {_typ_str(PROJECT)}, "
            f"kind: {_typ_str(kind)}, title: {_typ_str(title)}, "
            f"provenance: {_typ_str(prov)}, doc)\n\n"
            + body.read_text()
        )
        # --root / so the absolute template and image paths resolve.
        run(["typst", "compile", "--root", "/",
             "--font-path", str(fonts), str(main), str(pdf)])


# Log lines every Kaggle run emits that carry no information about the
# work — debugger notices, nbconvert chatter, CatBoost's CTR warnings.
LOG_NOISE = (
    "Debugger warning", "frozen modules", "PYDEVD", "MissingIDField",
    "validate(nb)", "SyntaxWarning", "re.sub(", "NbConvertApp",
    "mistune", "filter_links", "make the debugger", "Change of",
)


def kernel_log_markdown(nb: Path, archived: Path | None = None) -> str:
    """Render a Kaggle run log as an appendix.

    With `archived`, reads that file. Otherwise fetches the kernel's
    LATEST run — note that a specific version cannot be fetched:
    `kernels output <kernel>/<version>` accepts the suffix and silently
    returns the latest anyway (verified 2026-09-07), so historical runs
    are archived under assets/kernel_logs/ instead.

    Returns "" (and says why) when no log is reachable — a missing log
    should degrade the PDF, never abort the render.
    """
    if archived is not None:
        if not archived.exists():
            print(f"    (no such log {archived}; appendix skipped)")
            return ""
        try:
            entries = json.loads(archived.read_text())
        except json.JSONDecodeError:
            entries = [{"data": archived.read_text()}]
        return _log_appendix(entries, f"archived log {archived.name}")
    meta = REPO / "notebooks" / "kernels" / nb.stem.lstrip("0123456789_") / "kernel-metadata.json"
    if not meta.exists():
        matches = list((REPO / "notebooks" / "kernels").glob("*/kernel-metadata.json"))
        meta = next((m for m in matches
                     if json.loads(m.read_text()).get("code_file") == nb.name), None)
        if meta is None:
            print(f"    (no kernel metadata for {nb.name}; appendix skipped)")
            return ""
    kernel_id = json.loads(meta.read_text())["id"]
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(["kaggle", "kernels", "output", kernel_id,
                            "-p", td], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"    (could not fetch {kernel_id} log: {exc}; appendix skipped)")
            return ""
        logs = list(Path(td).glob("*.log"))
        if not logs:
            print(f"    (no log in {kernel_id} output; appendix skipped)")
            return ""
        try:
            entries = json.loads(logs[0].read_text())
        except json.JSONDecodeError:
            entries = [{"data": logs[0].read_text()}]
    return _log_appendix(entries, kernel_id)


def _log_appendix(entries: list, source: str) -> str:
    """Filtered log entries as a markdown appendix."""
    lines = [e.get("data", "").rstrip() for e in entries]
    lines = [ln for ln in lines
             if ln.strip() and not any(n in ln for n in LOG_NOISE)]
    if not lines:
        return ""
    body = "\n".join(lines)
    return (
        "\n\n## Executed output\n\n"
        f"Console output of the Kaggle run behind this notebook "
        f"(`{source}`). Kaggle exposes no executed notebook, so this log "
        "— the output of the run that produced the recorded results — "
        "stands in for cell outputs. Noise lines (debugger, nbconvert, "
        "CTR warnings) are filtered.\n\n"
        f"```text\n{body}\n```\n"
    )


def notebook_to_pdf(nb: Path, pdf: Path,
                    with_log: bool = False,
                    archived_log: Path | None = None,
                    executed_html: Path | None = None) -> None:
    """Notebook -> markdown via nbconvert -> Typst, same as the docs.

    Markdown rather than HTML deliberately. nbconvert's HTML puts each
    cell behind an `In [ ]:` prompt gutter, which indents the whole
    document and wastes the left margin; its markdown export drops the
    prompts and emits plain ```python blocks that Typst highlights
    natively. This is the sibling fire-research project's approach, and
    it also puts notebooks and docs through one pipeline instead of two.
    """
    with tempfile.TemporaryDirectory() as td:
        # A Kaggle self-export is an executed notebook saved as HTML by the
        # run itself (Kaggle exposes no executed notebook otherwise). Convert
        # it back to a notebook-shaped markdown so outputs survive.
        source = nb
        if executed_html is not None:
            if not executed_html.exists():
                raise SystemExit(f"no such self-export: {executed_html}")
            run(["pandoc", str(executed_html), "-f", "html", "-t", "markdown",
                 "--wrap=preserve", "-o", str(Path(td) / "body.md")])
        else:
            # --output-dir is where figures land too, beside the markdown.
            run([sys.executable, "-m", "nbconvert", "--to", "markdown",
                 str(source), "--output", "body", "--output-dir", td])
        body_md = Path(td) / "body.md"

        text = body_md.read_text()
        if with_log or archived_log is not None:
            appendix = kernel_log_markdown(nb, archived_log)
            if appendix:
                text += appendix
        body_md.write_text(text)

        md_to_pdf([body_md], pdf, doc_title(body_md), kind="Notebook",
                  provenance_for=nb)


def run_logs_pdf(out_dir: Path) -> None:
    """One PDF holding every archived Kaggle run log, in version order.

    Generated from assets/kernel_logs/ rather than hand-written, so it
    cannot drift from the logs it presents. These are the primary evidence
    behind the ledger's rows and are unfetchable once a newer run exists.
    Assembled as markdown and rendered through the same Typst path as
    everything else.
    """
    logs = sorted((REPO / "assets" / "kernel_logs").glob("*.log"))
    if not logs:
        return
    parts = [
        "The console output of every archived run, exactly as Kaggle "
        "returned it, with noise lines filtered. This is the primary "
        "evidence behind `docs/4_experiment_ledger.md`. Kaggle cannot "
        "serve a past run's log, so each was captured while it was the "
        "latest — see `assets/kernel_logs/README.md`.\n",
    ]
    for log in logs:
        try:
            entries = json.loads(log.read_text())
        except json.JSONDecodeError:
            entries = [{"data": log.read_text()}]
        lines = [e.get("data", "").rstrip() for e in entries]
        lines = [ln for ln in lines
                 if ln.strip() and not any(n in ln for n in LOG_NOISE)]
        parts.append(f"\n## {log.stem}\n\n```text\n" + "\n".join(lines) + "\n```\n")
    with tempfile.TemporaryDirectory() as td:
        md = Path(td) / "9_run_logs.md"
        md.write_text("".join(parts))
        md_to_pdf([md], out_dir / "9_run_logs.pdf",
                  "Archived Kaggle run logs", kind="Evidence",
                  provenance_for=REPO / "assets" / "kernel_logs")
    print(f"  renders/docs/9_run_logs.pdf ({len(logs)} runs)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["docs", "notebooks"],
                        help="render just one half of the pipeline")
    parser.add_argument("--executed-html", type=Path, metavar="HTML",
                        help="render this Kaggle self-export instead of the "
                             "notebook source, so the PDF carries real cell "
                             "outputs (see the notebook's Self-Export cell)")
    parser.add_argument("--with-kernel-log", action="store_true",
                        help="append each notebook's Kaggle run log as an "
                             "'Executed output' appendix (fetches the "
                             "kernel's LATEST run; needs network)")
    parser.add_argument("--kernel-log", type=Path, metavar="LOG",
                        help="use this archived log instead of fetching "
                             "(see assets/kernel_logs/ — a specific run's "
                             "log CANNOT be fetched, the API ignores the "
                             "version suffix)")
    parser.add_argument("--export", action="store_true",
                        help="after rendering, copy renders/ to iCloud "
                             "Drive under 05_Projects/<category>/<repo>/")
    args = parser.parse_args()

    missing = [t for t in ("pandoc", "typst") if shutil.which(t) is None]
    if missing:
        sys.exit(f"missing required tool(s): {', '.join(missing)}")

    if args.only != "notebooks":
        out = RENDERS / "docs"
        out.mkdir(parents=True, exist_ok=True)
        for name in ["README.md", "AGENTS.md"]:
            src = REPO / name
            md_to_pdf([src], out / f"{src.stem}.pdf", doc_title(src))
            print(f"  renders/docs/{src.stem}.pdf")
        for name in DOC_ORDER:
            src = REPO / "docs" / name
            md_to_pdf([src], out / f"{src.stem}.pdf", doc_title(src))
            print(f"  renders/docs/{src.stem}.pdf")
        md_to_pdf([REPO / "docs" / n for n in DOC_ORDER],
                  out / "all_docs.pdf", "Project Documentation",
                  kind="Collected")
        print("  renders/docs/all_docs.pdf")
        run_logs_pdf(out)

    if args.only != "docs":
        out = RENDERS / "notebooks"
        out.mkdir(parents=True, exist_ok=True)
        # Skip dotfiles: a staged copy left behind by an interrupted run
        # would otherwise be rendered as if it were a notebook.
        for nb in sorted(p for p in (REPO / "notebooks").glob("*.ipynb")
                         if not p.name.startswith(".")):
            # An archived log names one specific run, so it only applies
            # to the modeling notebook it came from.
            archived = (args.kernel_log
                        if args.kernel_log and nb.stem.endswith("modeling")
                        else None)
            notebook_to_pdf(nb, out / f"{nb.stem}.pdf",
                            with_log=args.with_kernel_log,
                            archived_log=archived,
                            executed_html=args.executed_html
                            if nb.stem.endswith("modeling") else None)
            tag = (" (Kaggle self-export)" if args.executed_html
                   and nb.stem.endswith("modeling")
                   else f" + {archived.name}" if archived
                   else " + Kaggle run log (latest)" if args.with_kernel_log
                   else " (source; runs live on Kaggle)")
            print(f"  renders/notebooks/{nb.stem}.pdf{tag}")

    if args.export:
        category = re.sub(r"^\d+\.\s*", "", REPO.parent.name)
        dest = ICLOUD / category / REPO.name
        dest.mkdir(parents=True, exist_ok=True)
        wanted = {pdf.relative_to(RENDERS) for pdf in RENDERS.rglob("*.pdf")}
        # Mirror semantics: a rename here must not leave a stale twin in
        # iCloud, so prune PDFs the source no longer produces -- scoped
        # strictly to this repo's own export folder.
        for old_pdf in dest.rglob("*.pdf"):
            if old_pdf.relative_to(dest) not in wanted:
                old_pdf.unlink()
                print(f"  pruned stale {old_pdf.relative_to(dest)}")
        # Copy only what actually changed. Overwriting an identical file
        # still counts as a write to iCloud, and a write while a sync is in
        # flight is what produces "name 2.pdf" conflict copies — so the
        # cheapest fix is not to write.
        copied = skipped = 0
        for rel in sorted(wanted):
            target = dest / rel
            source = RENDERS / rel
            if target.exists() and target.read_bytes() == source.read_bytes():
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied += 1
        note = f", {skipped} unchanged" if skipped else ""
        print(f"\nexported {copied} PDFs{note} -> {dest}")


if __name__ == "__main__":
    main()

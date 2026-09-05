#!/usr/bin/env python3
"""Render the project's docs and notebooks to PDF.

No sibling repo had a render pipeline when this was written (checked
S6E7, S6E8 and the master standard on 2026-09-05), so this is the first;
it deliberately uses only tools already on the machine — pandoc,
nbconvert, and headless Google Chrome for the HTML-to-PDF step — because
no LaTeX engine is installed and none should be required for this.

What it produces, under renders/ (gitignored):

    renders/docs/<name>.pdf        one PDF per markdown doc
    renders/docs/all_docs.pdf      docs 0-7 concatenated in reading order
    renders/notebooks/<name>.pdf   one PDF per notebook

Notebooks render from SOURCE by default — code and markdown, no cell
outputs — because the executed runs live on Kaggle and neither
`kaggle kernels pull` nor `kernels output` returns the executed notebook.
`--execute-eda` runs the EDA notebook locally into a temp copy first so
its PDF carries plots and tables; the modeling notebook is never executed
locally (docs/0: full runs happen on Kaggle only).

Usage:
    python3 scripts/render_pdf.py               # everything, source-only
    python3 scripts/render_pdf.py --execute-eda # EDA with outputs
    python3 scripts/render_pdf.py --only docs   # or: notebooks
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RENDERS = REPO / "renders"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
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
CSS = """
body { font: 11pt/1.5 Georgia, serif; max-width: 48em; margin: 2em auto;
       color: #1a1a1a; }
h1, h2, h3, h4 { font-family: Helvetica, Arial, sans-serif; color: #111;
                 page-break-after: avoid; }
h1 { font-size: 1.6em; border-bottom: 2px solid #333; padding-bottom: .2em; }
h2 { font-size: 1.25em; border-bottom: 1px solid #bbb; padding-bottom: .15em;
     margin-top: 1.6em; }
code, pre { font: 8.5pt/1.45 "SF Mono", Menlo, monospace; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: .7em;
      white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
table { border-collapse: collapse; font-size: 8.5pt; margin: 1em 0;
        page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: .25em .5em; text-align: left; }
th { background: #eee; font-family: Helvetica, sans-serif; }
blockquote { border-left: 3px solid #bbb; margin-left: 0; padding-left: 1em;
             color: #444; }
img { max-width: 100%; }
@page { margin: 18mm 15mm; }
"""

DOC_ORDER = [
    "0_coding_standards.md", "1_instructions.md", "2_eda_insights.md",
    "3_implementation_plan.md", "4_experiment_ledger.md",
    "5_submission_manifest.md", "6_agent_log.md",
    "7_source_dataset_provenance.md",
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def html_to_pdf(html: Path, pdf: Path) -> None:
    """Print an HTML file to PDF with headless Chrome."""
    run([
        CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}", f"file://{html}",
    ])


def md_to_pdf(sources: list[Path], pdf: Path, title: str) -> None:
    """Markdown (GitHub flavour) -> styled HTML via pandoc -> PDF."""
    with tempfile.TemporaryDirectory() as td:
        css = Path(td) / "print.css"
        css.write_text(CSS)
        html = Path(td) / "out.html"
        run([
            "pandoc", *map(str, sources), "-f", "gfm", "-t", "html5",
            "--standalone", "--embed-resources", f"--css={css}",
            "--metadata", f"pagetitle={title}", "-o", str(html),
        ])
        html_to_pdf(html, pdf)


def notebook_to_pdf(nb: Path, pdf: Path, execute: bool) -> None:
    """Notebook -> HTML via nbconvert -> PDF. Optionally execute first."""
    with tempfile.TemporaryDirectory() as td:
        cmd = [
            sys.executable, "-m", "nbconvert", "--to", "html",
            "--output-dir", td, "--output", "nb", str(nb),
        ]
        if execute:
            # Run from notebooks/ so the notebook's ../data path resolves.
            cmd += ["--execute", "--ExecutePreprocessor.timeout=600"]
        subprocess.run(cmd, check=True, capture_output=True, cwd=nb.parent)
        html_to_pdf(Path(td) / "nb.html", pdf)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["docs", "notebooks"],
                        help="render just one half of the pipeline")
    parser.add_argument("--execute-eda", action="store_true",
                        help="execute the EDA notebook locally so its PDF "
                             "has outputs (the modeling notebook is never "
                             "executed locally; see docs/0)")
    parser.add_argument("--export", action="store_true",
                        help="after rendering, copy renders/ to iCloud "
                             "Drive under 05_Projects/<category>/<repo>/")
    args = parser.parse_args()

    if not Path(CHROME).exists():
        sys.exit("Google Chrome not found; it does the HTML-to-PDF step.")

    if args.only != "notebooks":
        out = RENDERS / "docs"
        out.mkdir(parents=True, exist_ok=True)
        for name in ["README.md", "AGENTS.md"]:
            md_to_pdf([REPO / name], out / f"{Path(name).stem}.pdf",
                      Path(name).stem)
            print(f"  renders/docs/{Path(name).stem}.pdf")
        for name in DOC_ORDER:
            src = REPO / "docs" / name
            md_to_pdf([src], out / f"{src.stem}.pdf", src.stem)
            print(f"  renders/docs/{src.stem}.pdf")
        md_to_pdf([REPO / "docs" / n for n in DOC_ORDER],
                  out / "all_docs.pdf", "S6E9 — Project Documentation")
        print("  renders/docs/all_docs.pdf")

    if args.only != "docs":
        out = RENDERS / "notebooks"
        out.mkdir(parents=True, exist_ok=True)
        for nb in sorted((REPO / "notebooks").glob("*.ipynb")):
            execute = args.execute_eda and nb.name == "01_eda.ipynb"
            notebook_to_pdf(nb, out / f"{nb.stem}.pdf", execute)
            tag = " (executed)" if execute else " (source; runs live on Kaggle)"
            print(f"  renders/notebooks/{nb.stem}.pdf{tag}")

    if args.export:
        import re
        import shutil
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
        copied = 0
        for rel in sorted(wanted):
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RENDERS / rel, target)
            copied += 1
        print(f"\nexported {copied} PDFs -> {dest}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render the project's docs and notebooks to PDF.

No sibling repo had a render pipeline when this was written (checked
S6E7, S6E8 and the master standard on 2026-09-05), so this is the first;
it deliberately uses only tools already on the machine — pandoc,
nbconvert, and headless Google Chrome for the HTML-to-PDF step — because
no LaTeX engine is installed and none should be required for this.

Typography and palette (2026-09-05): DM Sans throughout, embedded as
base64 so a PDF renders identically on a machine without the font
installed, and heading colours that step down the hierarchy — navy H1,
viridis blue H2, green H3, muted-grey uppercase H4. The blue and green
are the ones the sibling hackathon repo already uses for charts, so
output across the workspace looks related; the lightness steps as well
as the hue, so the levels stay distinguishable printed in greyscale.

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
import base64
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
# Heading colours descend in weight through the hierarchy — navy for the
# document title, then the viridis blue and green the sibling hackathon
# repo already uses for charts, then muted grey. Continuity across the
# workspace, and each level is distinguishable in greyscale too because
# the lightness steps as well as the hue.
INK, BLUE, GREEN, MUTED = "#1C2333", "#31688E", "#2D7F5E", "#6E7278"
RULE, CODE_BG, CODE_BORDER = "#D9D6CC", "#F7F7F5", "#E2E0DA"

CSS_TEMPLATE = """
@font-face {{
  font-family: "DM Sans"; font-style: normal; font-weight: 100 1000;
  src: url("data:font/ttf;base64,{dm_regular}") format("truetype");
}}
@font-face {{
  font-family: "DM Sans"; font-style: italic; font-weight: 100 1000;
  src: url("data:font/ttf;base64,{dm_italic}") format("truetype");
}}
body {{ font: 10.5pt/1.6 "DM Sans", Helvetica, Arial, sans-serif;
       max-width: 48em; margin: 2em auto; color: {ink}; }}
h1, h2, h3, h4, h5, h6 {{ font-family: "DM Sans", Helvetica, sans-serif;
                          font-weight: 700; page-break-after: avoid;
                          letter-spacing: -0.01em; }}
h1 {{ font-size: 1.75em; color: {ink};
     border-bottom: 2.5px solid {ink}; padding-bottom: .25em;
     margin-top: 1.2em; }}
h2 {{ font-size: 1.3em; color: {blue};
     border-bottom: 1.5px solid {blue}; padding-bottom: .15em;
     margin-top: 1.8em; }}
h3 {{ font-size: 1.08em; color: {green}; margin-top: 1.4em; }}
h4 {{ font-size: .98em; color: {muted}; margin-top: 1.2em;
     text-transform: uppercase; letter-spacing: .04em; }}
h5, h6 {{ font-size: .95em; color: {muted}; margin-top: 1em; }}
a {{ color: {blue}; }}
strong {{ color: {ink}; font-weight: 700; }}
code, pre {{ font: 8.5pt/1.45 "SF Mono", Menlo, Consolas, monospace; }}
code {{ background: {code_bg}; padding: .08em .3em; border-radius: 3px; }}
pre {{ background: {code_bg}; border: 1px solid {code_border};
      border-left: 3px solid {blue}; padding: .7em; border-radius: 3px;
      white-space: pre-wrap; word-wrap: break-word;
      page-break-inside: avoid; }}
pre code {{ background: none; padding: 0; }}
table {{ border-collapse: collapse; font-size: 8.5pt; margin: 1em 0;
        page-break-inside: avoid; }}
th, td {{ border: 1px solid {rule}; padding: .3em .55em; text-align: left; }}
th {{ background: {blue}; color: #fff; font-weight: 700;
     border-color: {blue}; }}
tr:nth-child(even) td {{ background: {code_bg}; }}
blockquote {{ border-left: 3px solid {green}; margin-left: 0;
             padding-left: 1em; color: {muted}; }}
hr {{ border: none; border-top: 1px solid {rule}; margin: 2em 0; }}
img {{ max-width: 100%; }}
@page {{ margin: 18mm 15mm; }}
"""


def build_css() -> str:
    """Print stylesheet with the DM Sans variable fonts embedded.

    The fonts are inlined as base64 rather than named, so a rendered PDF
    reproduces identically on a machine where DM Sans is not installed
    (a named-but-missing font is silently substituted). See
    assets/fonts/dm-sans/README.md.
    """
    fonts = REPO / "assets" / "fonts" / "dm-sans"
    def b64(name: str) -> str:
        return base64.b64encode((fonts / name).read_bytes()).decode()
    return CSS_TEMPLATE.format(
        dm_regular=b64("DMSans-Variable.ttf"),
        dm_italic=b64("DMSans-Italic-Variable.ttf"),
        ink=INK, blue=BLUE, green=GREEN, muted=MUTED,
        rule=RULE, code_bg=CODE_BG, code_border=CODE_BORDER,
    )

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
        css.write_text(build_css())
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
        # nbconvert ships its own stylesheet; append ours last so DM Sans
        # and the heading colours win, without fighting its code styling.
        html_file = Path(td) / "nb.html"
        html = html_file.read_text()
        style = f"<style>{build_css()}</style>"
        html = (html.replace("</head>", style + "</head>", 1)
                if "</head>" in html else style + html)
        html_file.write_text(html)
        html_to_pdf(html_file, pdf)


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

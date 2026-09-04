#!/usr/bin/env python3
"""Execute the notebook's real Config and Data cells and verify that every
feature frame an active experiment references actually exists.

Why this exists. The fast dry-run harness stubs the feature frames into
globals so it can sweep every flag combination cheaply -- which means it
can *never* catch a frame that §2 failed to build. That blind spot let
the same bug ship twice: a guard listing `RUN_E06 or RUN_E07 or RUN_E08`
was not updated when E09 was added, so an E09-only run reached the fit
and died on `NameError: X_v3s`. This check closes it by running §1 and §2
for real, then statically resolving the names each experiment cell uses.

Usage:
    python scripts/check_frames.py                 # check every experiment
    python scripts/check_frames.py --flags RUN_E09 # check one configuration
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import sys
import types
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "02_baseline_modeling.ipynb"
EXPERIMENT_FLAGS = [
    "RUN_V1_SANITY", "RUN_V2_STRONG", "RUN_ANX_CATEGORICAL_AB",
    "RUN_E01_TUNING", "RUN_E02", "RUN_E03", "RUN_E04", "RUN_E05",
    "RUN_E06", "RUN_E07", "RUN_E08", "RUN_E09",
]


def _stub_heavy_imports() -> None:
    """CatBoost/LightGBM are not needed to build feature frames."""
    for name in ("lightgbm", "catboost"):
        if name in sys.modules:
            continue
        module = types.ModuleType(name)
        module.__version__ = "stub"

        class _Model:
            def __init__(self, *args, **kwargs):
                pass

        module.CatBoostClassifier = _Model
        module.LGBMClassifier = _Model
        sys.modules[name] = module


def _code_cells() -> list[str]:
    nb = json.loads(NOTEBOOK.read_text())
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def _referenced_frames(source: str) -> set[str]:
    """Frame-like names a cell reads without first assigning them.

    Names the cell binds itself (`X_tr, X_te = FRAMES[key]`) are excluded
    -- only names that must already exist in the namespace matter.
    """
    tree = ast.parse(source)
    assigned = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    return {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and (node.id.startswith("X_") or node.id == "SOURCE_LOOKUP")
        and node.id not in assigned
    }


def check(flag: str, cells: list[str]) -> list[str]:
    """Run Config+Data with `flag` on, return missing frame names."""
    _stub_heavy_imports()
    namespace: dict = {}
    config = cells[0]
    for other in EXPERIMENT_FLAGS:
        config = config.replace(f"{other} = True", f"{other} = False")
    config = config.replace(f"{flag} = False", f"{flag} = True")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(config, "<config>", "exec"), namespace)
    assert namespace[flag] is True, f"{flag} did not take effect"
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(cells[1], "<data>", "exec"), namespace)

    missing: list[str] = []
    for cell in cells[2:]:
        if f"if {flag}" not in cell and f"{flag} and" not in cell:
            continue
        for name in sorted(_referenced_frames(cell)):
            if name not in namespace:
                missing.append(name)
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flags", nargs="*", default=EXPERIMENT_FLAGS)
    args = parser.parse_args()
    cells = _code_cells()
    failures = 0
    for flag in args.flags:
        missing = check(flag, cells)
        if missing:
            failures += 1
            print(f"FAIL {flag}: §2 never builds {', '.join(missing)}")
        else:
            print(f"ok   {flag}")
    if failures:
        print(f"\n{failures} configuration(s) would die with NameError on Kaggle.")
        sys.exit(1)
    print("\nall configurations have the frames they reference")


if __name__ == "__main__":
    main()

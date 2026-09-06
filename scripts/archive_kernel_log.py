#!/usr/bin/env python3
"""Archive the log of a Kaggle kernel's LATEST run.

Run this after every kernel run. It has to be done at the time: Kaggle
offers no way to fetch a past run's log. `kernels output
<owner>/<kernel>/<version>` accepts the version suffix its own help
advertises and silently returns the latest run; `ApiGetKernelRequest`
carries a `version_number` field that the server also ignores (both
verified 2026-09-07 — see assets/kernel_logs/README.md). Logs for kernels
v1-v8 of this project were lost that way before it was noticed.

Usage:
    python3 scripts/archive_kernel_log.py 17 E11_something
    python3 scripts/archive_kernel_log.py 17 E11_something --kernel eda
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
ARCHIVE = REPO / "assets" / "kernel_logs"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="kernel version this run produced")
    parser.add_argument("label", help="what it recorded, e.g. E11_new_features")
    parser.add_argument("--kernel", default="modeling",
                        help="kernel directory under notebooks/kernels/")
    args = parser.parse_args()

    meta = REPO / "notebooks" / "kernels" / args.kernel / "kernel-metadata.json"
    if not meta.exists():
        sys.exit(f"no kernel metadata at {meta}")
    kernel_id = json.loads(meta.read_text())["id"]

    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["kaggle", "kernels", "output", kernel_id, "-p", td],
                       check=True, capture_output=True)
        logs = list(Path(td).glob("*.log"))
        if not logs:
            sys.exit(f"no log in the output of {kernel_id}")
        entries = json.loads(logs[0].read_text())
        text = "\n".join(e.get("data", "") for e in entries)
        stamped = re.findall(r'"notebook_version":\s*"(v\d+)"', text)

        ARCHIVE.mkdir(parents=True, exist_ok=True)
        dest = ARCHIVE / f"kernel_v{int(args.version):02d}_{args.label}.log"
        if dest.exists():
            sys.exit(f"{dest.name} already archived — refusing to overwrite")
        shutil.copy2(logs[0], dest)

    print(f"archived {dest.relative_to(REPO)} ({dest.stat().st_size // 1024} KB)")
    if stamped:
        print(f"  the log reports notebook_version {stamped[0]} — check this "
              f"matches the run you meant to archive; a mismatch means the "
              f"fetch returned a later run than kernel v{args.version}")
    print("  add a row to assets/kernel_logs/README.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env bash
# Push a notebook to its Kaggle kernel (public or private, per target).
#
# Copies the source notebook (the single source of truth, in notebooks/)
# into its kernel-metadata.json folder under notebooks/kernels/, then runs
# `kaggle kernels push`. The copied .ipynb is gitignored and regenerated
# every run, so notebooks/ never has two versions to keep in sync by hand.
#
# Usage: scripts/push_kaggle_kernel.sh <eda|modeling>
#
# ("baseline" is accepted as an alias for "modeling". The notebook was
# renamed 2026-09-05; pushing the new title made Kaggle re-slug the
# kernel to ev-purchases-modeling WITH its full version lineage intact
# (v16 followed v15). The old slug 404s; kernel-metadata.json carries
# the current id.)
#
# Both targets push public kernels. A third "experiments" target once
# existed for a separate private GPU kernel, but notebooks/kernels/
# experiments/ was never created, so the target could only ever fail at
# the copy step; it is removed rather than left as a trap. Every run in
# the ledger went through "baseline".
#
# On GPU: enabling it in kernel metadata does NOT make the model use it --
# CatBoost must also be given task_type="GPU" (the notebook's USE_GPU flag
# does this). Note that GPU results are a separate comparability class and
# are screening-only here; see docs/0_coding_standards.md.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOTEBOOKS_DIR="$REPO_ROOT/notebooks"

case "${1:-}" in
  eda)
    NOTEBOOK="01_eda.ipynb"
    KERNEL_DIR="$NOTEBOOKS_DIR/kernels/eda"
    ;;
  modeling|baseline)
    NOTEBOOK="02_modeling.ipynb"
    KERNEL_DIR="$NOTEBOOKS_DIR/kernels/modeling"
    ;;
  *)
    echo "Usage: $0 <eda|modeling>" >&2
    exit 1
    ;;
esac

if command -v kaggle >/dev/null 2>&1; then
  KAGGLE=kaggle
elif [ -x "/Users/tuannm3812/Library/Python/3.9/bin/kaggle" ]; then
  KAGGLE="/Users/tuannm3812/Library/Python/3.9/bin/kaggle"
else
  echo "kaggle CLI not found on PATH or at the known local install path." >&2
  exit 1
fi

cp "$NOTEBOOKS_DIR/$NOTEBOOK" "$KERNEL_DIR/$NOTEBOOK"
"$KAGGLE" kernels push -p "$KERNEL_DIR"

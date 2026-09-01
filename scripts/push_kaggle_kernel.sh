#!/usr/bin/env bash
# Push a notebook to its Kaggle kernel (public or private, per target).
#
# Copies the source notebook (the single source of truth, in notebooks/)
# into its kernel-metadata.json folder under notebooks/kernels/, then runs
# `kaggle kernels push`. The copied .ipynb is gitignored and regenerated
# every run, so notebooks/ never has two versions to keep in sync by hand.
#
# Usage: scripts/push_kaggle_kernel.sh <eda|baseline|experiments>
#
# "eda" and "baseline" push the public kernels. "experiments" pushes the
# same notebooks/02_baseline_modeling.ipynb source to a separate, private,
# GPU-enabled kernel (notebooks/kernels/experiments/) used for
# tuning/search runs -- kept out of the public baseline kernel's version
# history. GPU availability does not imply the model code actually runs on
# GPU; none of this project's LightGBM/CatBoost/HGB configurations select
# GPU computation.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOTEBOOKS_DIR="$REPO_ROOT/notebooks"

case "${1:-}" in
  eda)
    NOTEBOOK="01_eda.ipynb"
    KERNEL_DIR="$NOTEBOOKS_DIR/kernels/eda"
    ;;
  baseline)
    NOTEBOOK="02_baseline_modeling.ipynb"
    KERNEL_DIR="$NOTEBOOKS_DIR/kernels/baseline_modeling"
    ;;
  experiments)
    NOTEBOOK="02_baseline_modeling.ipynb"
    KERNEL_DIR="$NOTEBOOKS_DIR/kernels/experiments"
    ;;
  *)
    echo "Usage: $0 <eda|baseline|experiments>" >&2
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

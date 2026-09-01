#!/usr/bin/env python3
"""Validate an S6E8 submission artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def validate_submission(
    submission_path: Path,
    test_path: Path,
    sample_path: Path,
) -> dict[str, int | float]:
    """Validate schema, IDs, and probabilities for an S6E8 submission."""
    submission = pd.read_csv(submission_path)
    test = pd.read_csv(test_path, usecols=["id"])
    sample = pd.read_csv(sample_path)
    expected_columns = sample.columns.tolist()
    if submission.columns.tolist() != expected_columns:
        raise ValueError(f"Expected columns {expected_columns}")
    if len(submission) != len(test):
        raise ValueError("Submission row count does not match test")
    if not submission["id"].equals(test["id"]):
        raise ValueError("Submission IDs are not in test order")
    predictions = submission["addicted_label"].to_numpy(dtype=float)
    if not np.isfinite(predictions).all():
        raise ValueError("Predictions contain NaN or infinity")
    if not ((predictions >= 0.0) & (predictions <= 1.0)).all():
        raise ValueError("Predictions must be within [0, 1]")
    return {
        "rows": len(submission),
        "unique_predictions": int(np.unique(predictions).size),
        "minimum": float(predictions.min()),
        "maximum": float(predictions.max()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", type=Path)
    parser.add_argument("--test", type=Path, default=Path("data/test.csv"))
    parser.add_argument(
        "--sample",
        type=Path,
        default=Path("data/sample_submission.csv"),
    )
    args = parser.parse_args()
    print(validate_submission(args.submission, args.test, args.sample))


if __name__ == "__main__":
    main()

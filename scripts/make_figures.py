#!/usr/bin/env python3
"""Build the model-comparison figures for docs/8_model_comparison.md.

Everything here is derived from artifacts already on disk — the aligned
OOF matrices in predictions/ and the gate results recorded in
docs/4_experiment_ledger.md — so no model is refit and nothing depends on
a Kaggle run. Numbers are hard-coded from the ledger rather than parsed
out of it: the ledger is prose with tables, and a brittle parser that
silently mis-scrapes would be worse than an explicit table that a reader
can check against the source rows.

Typography and palette match scripts/render_pdf.py so figures sit with
the rendered docs rather than beside them.

Usage: python3 scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "assets" / "figures"
INK, BLUE, GREEN, MUTED = "#1C2333", "#31688E", "#2D7F5E", "#6E7278"
RED, RULE = "#B3472F", "#D9D6CC"
DPI = 200

for ttf in (REPO / "assets" / "fonts" / "dm-sans").glob("*.ttf"):
    font_manager.fontManager.addfont(str(ttf))
plt.rcParams.update({
    "font.family": "DM Sans", "font.size": 9,
    "axes.edgecolor": RULE, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

# --- The experiment record, transcribed from docs/4_experiment_ledger.md ---
# (label, standing F1 champion OOF after this step, public LB or None,
#  promoted, F2-only OOF where the step was measured in the other class)
#
# The F1 line is the champion's own series. E09 ran under fold definition
# F2, whose OOF is NOT comparable to an F1 number -- the project asserts
# that in code (paired_gate refuses a cross-class comparison), so it must
# not be drawn as a continuation of the F1 line either. It is plotted as
# a separate marker, and the F1 champion correctly stays flat at 0.94550
# because an F2 run cannot displace an F1 champion.
JOURNEY = [
    ("v1/v2\nbaselines", 0.94157, None, True, None),
    ("E01\nbudget", 0.94177, 0.94169, True, None),
    ("E02\ninteractions", 0.94204, 0.94198, True, None),
    ("E03\nseed avg", 0.94223, 0.94210, True, None),
    ("E04\nGPU/reg", 0.94223, None, False, None),
    ("E05\nsource rows", 0.94223, None, False, None),
    ("E06\nvalue identity", 0.94542, 0.94562, True, None),
    ("E07\ncapacity", 0.94542, None, False, None),
    ("E08\navg + fulldata", 0.94550, 0.94565, True, None),
    ("E09\n10-fold", 0.94550, 0.94570, True, 0.94564),
    ("E10\nCTR type", 0.94550, None, False, None),
]

# (candidate, delta, ci_low, ci_high, promoted) — every gate the project ran
GATES = [
    ("E01 cat_2000x05", 0.000192, 0.000145, 0.000239, True),
    ("E02 interactions", 0.000263, 0.000209, 0.000317, True),
    ("E02 avg3seeds", 0.000152, 0.000122, 0.000182, True),
    ("E02 lgbm interactions", 0.000050, -0.000032, 0.000132, False),
    ("E03 avg3seeds", 0.000166, 0.000134, 0.000199, True),
    ("E03 avg5seeds", 0.000191, 0.000155, 0.000227, True),
    ("E04 gpu_best_avg3", 0.000009, -0.000034, 0.000051, False),
    ("E05 plus_source", 0.000012, -0.000049, 0.000073, False),
    ("E06 value_ids", 0.003373, 0.003236, 0.003510, True),
    ("E06 value_ids_src", 0.003390, 0.003248, 0.003530, True),
    ("E07 all_value_ids", 0.000034, -0.000009, 0.000076, False),
    ("E07 cap_4000x025", 0.000014, -0.000009, 0.000036, False),
    ("E08 avg3seeds", 0.000074, 0.000053, 0.000099, True),
    ("E09 f2_avg3seeds", 0.000073, 0.000050, 0.000095, True),
]

# (experiment, kernel hours, OOF gain kept)
COST = [
    ("E01", 2.8, 0.00020), ("E02", 3.1, 0.00027), ("E03", 4.2, 0.00019),
    ("E04", 2.5, 0.0), ("E05", 1.9, 0.0), ("E06", 2.9, 0.00337),
    ("E07", 7.5, 0.0), ("E08", 5.2, 0.00007), ("E09", 5.2, 0.00005),
    ("E10", 5.1, 0.0),
]


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  assets/figures/{name}")


def fig_journey() -> None:
    """OOF and leaderboard across the whole experiment sequence."""
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = np.arange(len(JOURNEY))
    oof = [j[1] for j in JOURNEY]
    ax.plot(x, oof, "-", color=BLUE, lw=1.8, zorder=2, label="Champion OOF AUC")
    for i, (lab, o, lb, promoted, f2) in enumerate(JOURNEY):
        ax.plot(i, o, "o", ms=9 if promoted else 7, zorder=3,
                color=GREEN if promoted else "white",
                mec=GREEN if promoted else MUTED, mew=1.6)
        if lb is not None:
            ax.plot(i, lb, "D", ms=5.5, color=INK, zorder=3)
        if f2 is not None:
            ax.plot(i, f2, "s", ms=7, color="white", mec=BLUE, mew=1.8,
                    zorder=3)
            ax.annotate("F2 (10-fold) OOF —\na different measurement,\n"
                        "not comparable to the F1 line",
                        xy=(i, f2), xytext=(i - 2.5, 0.94595),
                        fontsize=7.6, color=BLUE, ha="left",
                        arrowprops=dict(arrowstyle="->", color=BLUE, lw=.9))
    ax.plot([], [], "o", color=GREEN, mec=GREEN, ms=8, label="Promoted (gate cleared)")
    ax.plot([], [], "o", color="white", mec=MUTED, mew=1.6, ms=7, label="Not promoted")
    ax.plot([], [], "D", color=INK, ms=5.5, label="Public leaderboard")
    ax.plot([], [], "s", color="white", mec=BLUE, mew=1.8, ms=7,
            label="F2 OOF (separate class)")
    ax.annotate("E06: value identities\n+0.00337 — 26x the noise floor,\n"
                "5x every other accepted step combined",
                xy=(6, 0.94542), xytext=(3.15, 0.94465),
                fontsize=8.5, color=INK, ha="left",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1))
    ax.set_xticks(x)
    ax.set_xticklabels([j[0] for j in JOURNEY], fontsize=7.5)
    ax.set_ylabel("ROC AUC")
    ax.set_title("Every step, kept or rejected — and the one that mattered",
                 fontsize=12, fontweight="bold", color=INK, loc="left", pad=12)
    ax.grid(axis="y", color=RULE, lw=.6, alpha=.7)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.text(0.01, -0.06,
             "The F1 line is the champion's own series. E09 is drawn apart "
             "because its 10-fold OOF is a different measurement — it was "
             "promoted within F2\nyet could not displace the F1 champion, "
             "which is why the line stays flat after E08.",
             fontsize=8, color=MUTED)
    save(fig, "01_experiment_journey.png")


def fig_gates() -> None:
    """Forest plot: every gate's delta with its 95% CI."""
    fig, ax = plt.subplots(figsize=(9, 5.4))
    y = np.arange(len(GATES))[::-1]
    for yi, (lab, d, lo, hi, promoted) in zip(y, GATES):
        c = GREEN if promoted else MUTED
        ax.plot([lo, hi], [yi, yi], "-", color=c, lw=2.2, solid_capstyle="round")
        ax.plot(d, yi, "o", ms=6, color=c, zorder=3)
    ax.axvline(0, color=RED, lw=1.2, ls="--", zorder=1)
    ax.text(0, len(GATES) - .3, "  no effect", color=RED, fontsize=8, va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([g[0] for g in GATES], fontsize=8.5)
    ax.set_xscale("symlog", linthresh=1e-4)
    ax.set_xlabel("AUC gain vs. the run's own in-run baseline "
                  "(symlog scale, bars are 95% CI)")
    ax.set_title("The gate is what separated signal from noise",
                 fontsize=12, fontweight="bold", color=INK, loc="left", pad=12)
    ax.grid(axis="x", color=RULE, lw=.6, alpha=.7)
    ax.set_axisbelow(True)
    ax.plot([], [], "o-", color=GREEN, label="Promoted")
    ax.plot([], [], "o-", color=MUTED, label="Rejected (CI touches zero)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    save(fig, "02_gate_forest.png")


def fig_correlation() -> None:
    """Why every blend failed: the candidates are one model repeated."""
    names = ["e09_f2_avg3seeds", "e08_avg3seeds", "e06_cat_value_ids",
             "e07_all_value_ids", "e02_cat_interactions",
             "e02_lgbm_1000x05_interactions", "e01_hgb_2000x03_63l",
             "v1b_logistic"]
    short = ["E09 F2 avg", "E08 avg3", "E06 value-id", "E07 all-ids",
             "E02 cat", "E02 lgbm", "E01 hgb", "logistic"]
    vecs = []
    for n in names:
        p = REPO / "predictions" / f"{n}_oof.npy"
        if not p.exists():
            print(f"  (skipped {n}: matrix not on disk)")
            return
        vecs.append(np.load(p))
    m = np.corrcoef(np.vstack(vecs))
    fig, ax = plt.subplots(figsize=(7.2, 6))
    im = ax.imshow(m, cmap="viridis", vmin=0.90, vmax=1.0)
    ax.set_xticks(range(len(short))); ax.set_xticklabels(short, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(short))); ax.set_yticklabels(short, fontsize=8)
    for i in range(len(short)):
        for j in range(len(short)):
            ax.text(j, i, f"{m[i, j]:.3f}", ha="center", va="center", fontsize=6.8,
                    color="white" if m[i, j] < 0.978 else INK)
    ax.set_title("OOF correlation — the diversity bar was never the problem",
                 fontsize=11.5, fontweight="bold", color=INK, loc="left", pad=12)
    fig.colorbar(im, ax=ax, shrink=.8, label="Pearson r")
    fig.text(0.01, -0.03,
             "Blending needs r ≤ 0.995. The strong models sit at 0.998–0.9999 "
             "(one model repeated);\nthe genuinely decorrelated ones are 0.003+ weaker, "
             "so no weighting can pay for the deficit.",
             fontsize=8, color=MUTED)
    save(fig, "03_oof_correlation.png")


def fig_cost() -> None:
    """Compute spent against OOF actually kept, per experiment."""
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(COST))
    hours = [c[1] for c in COST]
    gains = [c[2] for c in COST]
    ax.bar(x, hours, color=[GREEN if g > 0 else MUTED for g in gains],
           width=.62, zorder=2)
    for i, (lab, h, g) in enumerate(COST):
        ax.text(i, h + .12, f"+{g:.5f}" if g > 0 else "null",
                ha="center", fontsize=7.6,
                color=GREEN if g > 0 else MUTED,
                fontweight="bold" if g > 0.001 else "normal")
    ax.set_xticks(x); ax.set_xticklabels([c[0] for c in COST], fontsize=9)
    ax.set_ylabel("Kaggle compute (hours)")
    ax.set_ylim(0, max(hours) * 1.22)
    ax.set_title("Cost against what was kept — the cheapest run bought the most",
                 fontsize=12, fontweight="bold", color=INK, loc="left", pad=12)
    ax.grid(axis="y", color=RULE, lw=.6, alpha=.7); ax.set_axisbelow(True)
    fig.text(0.01, -0.04,
             "E06 (2.9 h) returned +0.00337; the four runs after it cost 23 h "
             "for +0.00012 combined.\nE06 came from a 30-second local diagnostic, "
             "not from a sweep.", fontsize=8, color=MUTED)
    save(fig, "04_cost_vs_gain.png")


if __name__ == "__main__":
    fig_journey(); fig_gates(); fig_correlation(); fig_cost()

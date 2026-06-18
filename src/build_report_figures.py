# -*- coding: utf-8 -*-
"""Report-only figures and tables derived from already-committed result CSVs.

This script does NOT recompute any analysis. It reads the outputs produced by
build_idf_weighted_analysis.py and build_card_sorting_analysis.py and renders
extra figures/tables for the final report, keeping the two analysis scripts
untouched.

Run:
    python src/build_report_figures.py
"""
from __future__ import annotations

import pathlib

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

BASE = pathlib.Path(__file__).resolve().parents[1]
REPORT_TABLES = BASE / "results" / "tables" / "keep_for_report"
REPORT_FIGURES = BASE / "results" / "figures" / "keep_for_report"

AMBIGUITY_INPUT = REPORT_TABLES / "cardsort_department_ambiguity.csv"

AMBIGUITY_THRESHOLD = 0.5
EMPHASIS_COLOR = "#b2182b"   # burgundy: ambiguous (below threshold)
BASE_COLOR = "#9e9e9e"       # gray: robustly grouped (at/above threshold)


def setup_style() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def fig_ambiguity_bars() -> None:
    df = pd.read_csv(AMBIGUITY_INPUT, encoding="utf-8-sig")
    df = df.sort_values("max_co_classification", ascending=True).reset_index(drop=True)

    departments = df["department"].tolist()
    values = df["max_co_classification"].tolist()
    partners = df["closest_partner"].tolist()
    colors = [EMPHASIS_COLOR if v < AMBIGUITY_THRESHOLD else BASE_COLOR for v in values]

    positions = range(len(df))
    plt.figure(figsize=(8.5, 9))
    ax = plt.gca()
    ax.barh(positions, values, color=colors)
    ax.set_yticks(positions)
    ax.set_yticklabels(departments, fontsize=9)
    ax.invert_yaxis()  # most ambiguous (lowest value) at the top

    for i, (value, partner) in enumerate(zip(values, partners)):
        ax.text(value + 0.012, i, f"{partner} ({value:.2f})", va="center", fontsize=8)

    ax.axvline(AMBIGUITY_THRESHOLD, linestyle=":", color="gray", linewidth=1.0, alpha=0.8)
    ax.set_xlim(0, 1.28)
    ax.set_xlabel("최대 동시분류율 (전문가 합의 강도)")
    ax.set_title("학과별 모호성: 어떤 군집에도 합의되지 않는 boundary 학과")
    ax.legend(
        handles=[
            Patch(color=EMPHASIS_COLOR, label="합의 모호 (< 0.5)"),
            Patch(color=BASE_COLOR, label="견고하게 묶임 (≥ 0.5)"),
        ],
        loc="lower right",
        fontsize=9,
    )
    plt.tight_layout()
    plt.savefig(REPORT_FIGURES / "cardsort_department_ambiguity_bars.png", dpi=200)
    plt.close()


def main() -> None:
    REPORT_FIGURES.mkdir(parents=True, exist_ok=True)
    setup_style()
    fig_ambiguity_bars()
    print("figure -> results/figures/keep_for_report/cardsort_department_ambiguity_bars.png")


if __name__ == "__main__":
    main()

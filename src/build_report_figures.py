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
PROCESSED = BASE / "data" / "processed"
REPORT_TABLES = BASE / "results" / "tables" / "keep_for_report"
REPORT_FIGURES = BASE / "results" / "figures" / "keep_for_report"

AMBIGUITY_INPUT = REPORT_TABLES / "cardsort_department_ambiguity.csv"
COURSE_IDF_INPUT = REPORT_TABLES / "course_idf_weights.csv"
EVIDENCE_INPUT = PROCESSED / "course_coding_evidence.csv"

AMBIGUITY_THRESHOLD = 0.5
EMPHASIS_COLOR = "#b2182b"   # burgundy: ambiguous (below threshold)
BASE_COLOR = "#9e9e9e"       # gray: robustly grouped (at/above threshold)

N_HIGH_DISCRIMINATIVE = 6    # block A: one df=1 course per distinct broad_field
N_LOW_DISCRIMINATIVE = 5     # block B: most common courses


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


def table_discriminative_courses() -> pd.DataFrame:
    """Contrast table: highly discriminative (rare, df=1) vs common (low-IDF) courses.

    Block A samples one df=1 course per distinct broad_field (rare courses tie at
    the maximum IDF, so listing all of them is uninformative; one per field keeps
    the departments diverse). Each df=1 course is recommended by exactly one
    department, which is shown. Block B lists the most common courses, which are
    shared across many departments and therefore carry little discriminative
    signal. Outputs a CSV and a LaTeX tabular snippet for main.tex.
    """
    weights = pd.read_csv(COURSE_IDF_INPUT, encoding="utf-8-sig")
    evidence = pd.read_csv(EVIDENCE_INPUT, encoding="utf-8-sig")

    course_dept = evidence.groupby("course_name_standardized")["department_name_ko"].agg(
        lambda s: sorted(set(s))
    )
    course_field = evidence.groupby("course_name_standardized")["broad_field"].agg(
        lambda s: sorted(set(s))[0]
    )
    idf_of = dict(zip(weights["course"], weights["idf"]))

    rows: list[dict] = []
    # Block A: one df=1 course per distinct broad_field
    df1 = weights[weights["document_frequency"] == 1].sort_values("course")
    seen_fields: set[str] = set()
    for course in df1["course"]:
        field = course_field.get(course)
        if field is None or field in seen_fields:
            continue
        seen_fields.add(field)
        rows.append(
            {
                "tier": "high_discriminative",
                "course": course,
                "document_frequency": 1,
                "idf": round(float(idf_of[course]), 3),
                "recommending": course_dept[course][0],
            }
        )
        if len(rows) >= N_HIGH_DISCRIMINATIVE:
            break

    # Block B: most common courses (low IDF, shared)
    common = weights.sort_values(["document_frequency", "course"], ascending=[False, True]).head(
        N_LOW_DISCRIMINATIVE
    )
    for record in common.itertuples():
        rows.append(
            {
                "tier": "low_discriminative",
                "course": record.course,
                "document_frequency": int(record.document_frequency),
                "idf": round(float(record.idf), 3),
                "recommending": f"공통({int(record.document_frequency)}개 학과)",
            }
        )

    table = pd.DataFrame(rows)
    table.to_csv(REPORT_TABLES / "discriminative_courses.csv", index=False, encoding="utf-8-sig")

    # LaTeX tabular for main.tex
    lines = [
        r"\begin{tabular}{lccl}",
        r"\hline",
        r"과목 & df & IDF & 권장 학과 \\",
        r"\hline",
        r"\multicolumn{4}{l}{\textit{고변별 (희소 과목, df=1 $\rightarrow$ 특정 학과 직결)}} \\",
    ]
    for row in rows:
        if row["tier"] == "high_discriminative":
            lines.append(f"{row['course']} & {row['document_frequency']} & {row['idf']:.2f} & {row['recommending']} \\\\")
    lines.append(r"\hline")
    lines.append(r"\multicolumn{4}{l}{\textit{저변별 (공통 과목, 변별 거의 없음)}} \\")
    for row in rows:
        if row["tier"] == "low_discriminative":
            lines.append(f"{row['course']} & {row['document_frequency']} & {row['idf']:.2f} & {row['recommending']} \\\\")
    lines += [r"\hline", r"\end{tabular}"]
    tex = "\n".join(lines)
    (REPORT_TABLES / "discriminative_courses.tex").write_text(tex, encoding="utf-8")

    print("\n--- discriminative_courses (LaTeX) ---")
    print(tex)
    return table


def main() -> None:
    REPORT_FIGURES.mkdir(parents=True, exist_ok=True)
    REPORT_TABLES.mkdir(parents=True, exist_ok=True)
    setup_style()
    fig_ambiguity_bars()
    table_discriminative_courses()
    print("\nfigure -> results/figures/keep_for_report/cardsort_department_ambiguity_bars.png")
    print("table  -> results/tables/keep_for_report/discriminative_courses.{csv,tex}")


if __name__ == "__main__":
    main()

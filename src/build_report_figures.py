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
from collections import Counter

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

N_CLUSTER_DISCRIMINATIVE = 6   # block A cap (one per field; how many qualify depends on data)
N_LOW_DISCRIMINATIVE = 5       # block B: most common courses
CLUSTER_DF_MIN, CLUSTER_DF_MAX = 2, 6   # block A: courses recommended by a small group
CLUSTER_PURITY_MIN = 0.66      # fraction of the small group falling in one academic field


def coarse_field(broad_field: str) -> str:
    """Map a fine broad_field label to a coarse academic field."""
    f = str(broad_field)
    if "medical" in f or "health" in f:
        return "의약보건"
    if "engineering" in f or "industry" in f:
        return "공학"
    if "arts" in f:
        return "예술"
    if "social" in f:
        return "사회"
    if "humanities" in f:
        return "인문"
    if "natural" in f:
        return "자연"
    return "기타"


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
    course_fields = evidence.groupby("course_name_standardized")["broad_field"].agg(
        lambda s: [coarse_field(x) for x in s]
    )
    df_of = dict(zip(weights["course"], weights["document_frequency"]))
    idf_of = dict(zip(weights["course"], weights["idf"]))

    def group_label(departments: list[str], field: str) -> str:
        if len(departments) <= 3:
            return "·".join(d[:-1] if d.endswith("과") else d for d in departments)
        return f"{field} {len(departments)}개"

    rows: list[dict] = []
    # Block A: courses concentrated in one coherent academic field (cluster-discriminative).
    # A course recommended by a small group whose departments share a field flags that
    # cluster; this avoids the circular df=1 case (a single department is tautologically
    # "discriminative" without being defining).
    candidates = []
    for course, fields in course_fields.items():
        df = int(df_of.get(course, len(fields)))
        if not (CLUSTER_DF_MIN <= df <= CLUSTER_DF_MAX):
            continue
        field, top = Counter(fields).most_common(1)[0]
        purity = top / df
        if purity >= CLUSTER_PURITY_MIN:
            candidates.append((purity, df, course, field))
    candidates.sort(key=lambda t: (-t[0], -t[1], t[2]))
    seen_fields: set[str] = set()
    for purity, df, course, field in candidates:
        if field in seen_fields:
            continue
        seen_fields.add(field)
        rows.append(
            {
                "tier": "cluster_discriminative",
                "course": course,
                "document_frequency": df,
                "idf": round(float(idf_of[course]), 3),
                "recommending": group_label(course_dept[course], field),
            }
        )
        if len(rows) >= N_CLUSTER_DISCRIMINATIVE:
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
        r"과목 & df & IDF & 권장 학과 군집 \\",
        r"\hline",
        r"\multicolumn{4}{l}{\textit{군집 변별 과목 (특정 계열 군집에만 등장)}} \\",
    ]
    for row in rows:
        if row["tier"] == "cluster_discriminative":
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

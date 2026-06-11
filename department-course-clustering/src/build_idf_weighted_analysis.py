# -*- coding: utf-8 -*-
"""IDF-weighted course-vector clustering with a weighting-sensitivity analysis.

Motivation
----------
The baseline pipeline treats every recommended course as an independent 0/1
feature, so near-ubiquitous courses (e.g. 확률과 통계, present in 21/25
departments) carry the same weight as highly department-specific courses.
This collapses most STEM/health departments into one undifferentiated cluster.

This script down-weights common courses with standard inverse document
frequency (IDF), which requires NO hand-tuned weights:

    weight(course) = ln(N / df(course)),  N = number of departments

(A) IDF-weighted clustering: binary presence x IDF -> cosine similarity ->
    hierarchical clustering.
(C) Sensitivity analysis: a single knob alpha scales the weighting,
    weight = idf**alpha, so alpha=0 reproduces the plain binary baseline and
    alpha=1 is standard IDF. We report silhouette, agreement (ARI) with the
    binary baseline, and pair co-assignment robustness across the sweep, so the
    chosen weighting is shown to be a defensible point on a continuum rather
    than a cherry-picked setting.

Card sorting is deliberately NOT used here: it is reserved as an independent
external criterion, so it must not influence preprocessing choices.

Run:
    python src/build_idf_weighted_analysis.py
"""
from __future__ import annotations

import pathlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import adjusted_rand_score, silhouette_score

BASE = pathlib.Path(__file__).resolve().parents[1]
INPUT_MATRIX = BASE / "data" / "processed" / "department_course_matrix_binary.csv"
PROCESSED = BASE / "data" / "processed"
REPORT_TABLES = BASE / "results" / "tables" / "keep_for_report"
REPORT_FIGURES = BASE / "results" / "figures" / "keep_for_report"

METADATA_COLUMNS = {
    "department_id",
    "department_name",
    "department_name_ko",
    "broad_field",
    "selected_reason",
}
LINKAGE_METHOD = "average"          # primary method (most stable under the sweep)
N_CLUSTERS = 4
ALPHA_SWEEP = [round(a, 2) for a in np.linspace(0.0, 2.0, 9)]
PRIMARY_ALPHA = 1.0                 # standard IDF, no hand tuning


def setup_plot_style() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def load() -> tuple[pd.DataFrame, list[str], str]:
    matrix = pd.read_csv(INPUT_MATRIX, encoding="utf-8-sig")
    course_columns = [c for c in matrix.columns if c not in METADATA_COLUMNS]
    name_col = "department_name" if "department_name" in matrix.columns else "department_name_ko"
    return matrix, course_columns, name_col


def idf_weights(x: np.ndarray) -> np.ndarray:
    n = x.shape[0]
    df = x.sum(axis=0)
    df = np.where(df == 0, 1, df)        # guard; all-zero columns get idf 0 below
    return np.log(n / df)


def weighted_matrix(x: np.ndarray, idf: np.ndarray, alpha: float) -> np.ndarray:
    return x * (idf ** alpha)


def cluster(xf: np.ndarray, method: str, k: int) -> tuple[np.ndarray, float, np.ndarray]:
    distance = pdist(xf, metric="cosine")
    z = linkage(distance, method=method)
    labels = fcluster(z, t=k, criterion="maxclust")
    try:
        sil = silhouette_score(squareform(distance), labels, metric="precomputed")
    except ValueError:
        sil = float("nan")
    return labels, sil, z


def save_idf_table(course_columns: list[str], x: np.ndarray, idf: np.ndarray) -> None:
    table = pd.DataFrame(
        {
            "course": course_columns,
            "document_frequency": x.sum(axis=0).astype(int),
            "idf": np.round(idf, 4),
        }
    ).sort_values(["document_frequency", "course"])
    table.to_csv(REPORT_TABLES / "course_idf_weights.csv", index=False, encoding="utf-8-sig")


def save_assignments(matrix: pd.DataFrame, name_col: str, labels: np.ndarray) -> pd.DataFrame:
    assignments = pd.DataFrame(
        {
            "department_id": matrix["department_id"],
            "department_name": matrix[name_col],
            "cluster_id": labels,
        }
    ).sort_values(["cluster_id", "department_id"])
    assignments.to_csv(REPORT_TABLES / "idf_cluster_assignments.csv", index=False, encoding="utf-8-sig")
    return assignments


def save_cluster_summary(matrix: pd.DataFrame, name_col: str, course_columns: list[str],
                         xf: np.ndarray, labels: np.ndarray) -> None:
    weighted = pd.DataFrame(xf, columns=course_columns)
    weighted["cluster_id"] = labels
    weighted["__name"] = matrix[name_col].to_numpy()
    rows = []
    for cluster_id, group in weighted.groupby("cluster_id"):
        means = group[course_columns].mean().sort_values(ascending=False)
        top = [c for c, v in means.items() if v > 0][:5]
        rows.append(
            {
                "cluster_id": int(cluster_id),
                "departments": "; ".join(group["__name"].tolist()),
                "top_distinctive_courses": ", ".join(top),
            }
        )
    pd.DataFrame(rows).sort_values("cluster_id").to_csv(
        REPORT_TABLES / "idf_cluster_summary.csv", index=False, encoding="utf-8-sig"
    )


def sensitivity(x: np.ndarray, idf: np.ndarray) -> pd.DataFrame:
    rows = []
    for method in ["average", "complete"]:
        base_labels, _, _ = cluster(weighted_matrix(x, idf, 0.0), method, N_CLUSTERS)
        for alpha in ALPHA_SWEEP:
            labels, sil, _ = cluster(weighted_matrix(x, idf, alpha), method, N_CLUSTERS)
            sizes = sorted((np.bincount(labels)[1:]).tolist(), reverse=True)
            rows.append(
                {
                    "linkage": method,
                    "alpha": alpha,
                    "silhouette_cosine": round(sil, 4),
                    "ari_vs_binary": round(adjusted_rand_score(base_labels, labels), 4),
                    "cluster_sizes": "|".join(str(s) for s in sizes),
                }
            )
    table = pd.DataFrame(rows)
    table.to_csv(REPORT_TABLES / "weighting_sensitivity.csv", index=False, encoding="utf-8-sig")
    return table


def robustness(matrix: pd.DataFrame, name_col: str, x: np.ndarray, idf: np.ndarray,
               labels: np.ndarray) -> pd.DataFrame:
    names = matrix[name_col].to_numpy()
    n = len(names)
    co = np.zeros((n, n))
    for alpha in ALPHA_SWEEP:
        lab, _, _ = cluster(weighted_matrix(x, idf, alpha), LINKAGE_METHOD, N_CLUSTERS)
        co += (lab[:, None] == lab[None, :]).astype(float)
    co /= len(ALPHA_SWEEP)
    rows = []
    for cluster_id in sorted(set(labels)):
        members = np.where(labels == cluster_id)[0]
        if len(members) > 1:
            vals = [co[i, j] for a, i in enumerate(members) for j in members[a + 1:]]
            mean_co = float(np.mean(vals))
        else:
            mean_co = float("nan")
        rows.append(
            {
                "cluster_id": int(cluster_id),
                "n": int(len(members)),
                "mean_co_assignment_over_alpha": round(mean_co, 3),
                "departments": "; ".join(names[members]),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(REPORT_TABLES / "cluster_robustness.csv", index=False, encoding="utf-8-sig")
    return table


def plot_dendrogram(z: np.ndarray, matrix: pd.DataFrame, name_col: str) -> None:
    labels = [f"{i} {n}" for i, n in zip(matrix["department_id"], matrix[name_col])]
    plt.figure(figsize=(13, 7))
    dendrogram(z, labels=labels, leaf_rotation=75, leaf_font_size=9, color_threshold=None)
    plt.title(f"IDF-weighted hierarchical clustering ({LINKAGE_METHOD}, alpha={PRIMARY_ALPHA})")
    plt.ylabel("Cosine distance")
    plt.tight_layout()
    plt.savefig(REPORT_FIGURES / "idf_dendrogram.png", dpi=200)
    plt.close()


def main() -> None:
    REPORT_TABLES.mkdir(parents=True, exist_ok=True)
    REPORT_FIGURES.mkdir(parents=True, exist_ok=True)
    setup_plot_style()

    matrix, course_columns, name_col = load()
    x = matrix[course_columns].to_numpy(dtype=float)
    idf = idf_weights(x)
    save_idf_table(course_columns, x, idf)

    xf = weighted_matrix(x, idf, PRIMARY_ALPHA)
    pd.concat(
        [matrix[["department_id", name_col]].reset_index(drop=True),
         pd.DataFrame(np.round(xf, 4), columns=course_columns)],
        axis=1,
    ).to_csv(PROCESSED / "department_course_matrix_idf_weighted.csv", index=False, encoding="utf-8-sig")

    labels, sil, z = cluster(xf, LINKAGE_METHOD, N_CLUSTERS)
    assignments = save_assignments(matrix, name_col, labels)
    save_cluster_summary(matrix, name_col, course_columns, xf, labels)
    plot_dendrogram(z, matrix, name_col)

    sens = sensitivity(x, idf)
    robust = robustness(matrix, name_col, x, idf, labels)

    print(f"input={INPUT_MATRIX.name}  departments={len(matrix)}  features={len(course_columns)}")
    print(f"primary: idf alpha={PRIMARY_ALPHA}, linkage={LINKAGE_METHOD}, k={N_CLUSTERS}, silhouette={sil:.3f}")
    print("\nclusters (alpha=1, average):")
    for cid, grp in assignments.groupby("cluster_id"):
        print(f"  C{cid}: " + ", ".join(grp["department_name"]))
    print("\nrobustness (mean co-assignment over alpha sweep):")
    for _, r in robust.iterrows():
        print(f"  C{r['cluster_id']} (n={r['n']}): {r['mean_co_assignment_over_alpha']}")
    print("\noutputs -> results/tables/keep_for_report (idf_*, course_idf_weights, "
          "weighting_sensitivity, cluster_robustness), results/figures/keep_for_report/idf_dendrogram.png")


if __name__ == "__main__":
    main()

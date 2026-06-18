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

import os
import pathlib

os.environ.setdefault("OMP_NUM_THREADS", "1")  # silence KMeans MKL warning on Windows

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import normalize

BASE = pathlib.Path(__file__).resolve().parents[1]
INPUT_MATRIX = BASE / "data" / "processed" / "department_course_matrix_binary.csv"
EVIDENCE = BASE / "data" / "processed" / "course_coding_evidence.csv"
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
CORE_SUBCLUSTERS_K = 3              # sub-clusters within the largest primary cluster
SUB_LINKAGE = "complete"           # sharper splits for the dense STEM-health core


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


def save_selection_type_idf(course_columns: list[str], idf: np.ndarray) -> pd.DataFrame:
    """Mean IDF per selection type, justifying course-level (not type-level) weighting.

    Shows that 융합선택 > 진로선택 > 일반선택 in discriminativeness, which is the
    opposite of the intuitive hand-weighting (진로 highest) and therefore supports
    using data-driven per-course IDF instead of arbitrary per-type weights.
    """
    if not EVIDENCE.exists():
        return pd.DataFrame()
    evidence = pd.read_csv(EVIDENCE, encoding="utf-8-sig")
    idf_by_course = dict(zip(course_columns, idf))
    evidence = evidence[evidence["course_name_standardized"].isin(idf_by_course)].copy()
    evidence["idf"] = evidence["course_name_standardized"].map(idf_by_course)
    table = (
        evidence.groupby("selection_type")["idf"]
        .agg(mentions="count", mean_idf="mean")
        .reset_index()
        .sort_values("mean_idf")
    )
    table["mean_idf"] = table["mean_idf"].round(3)
    table.to_csv(REPORT_TABLES / "selection_type_idf.csv", index=False, encoding="utf-8-sig")
    return table


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


def subcluster_core(matrix: pd.DataFrame, name_col: str, course_columns: list[str],
                    labels: np.ndarray) -> pd.DataFrame:
    """Sub-cluster the largest primary cluster (the dense STEM-health core).

    IDF is recomputed *within* the subset, because courses common to every
    core department carry no within-core discriminative signal; local IDF
    down-weights them so the sub-structure can emerge.
    """
    core_id = pd.Series(labels).value_counts().idxmax()
    mask = labels == core_id
    core_names = matrix[name_col].to_numpy()[mask]
    core_ids = matrix["department_id"].to_numpy()[mask]

    xc = matrix[course_columns].to_numpy(dtype=float)[mask]
    present = xc.sum(axis=0) > 0
    xc = xc[:, present]
    features = np.array(course_columns)[present]
    local_idf = np.log(xc.shape[0] / xc.sum(axis=0))
    weighted = xc * local_idf

    distance = pdist(weighted, metric="cosine")
    z = linkage(distance, method=SUB_LINKAGE)
    sub_labels = fcluster(z, t=CORE_SUBCLUSTERS_K, criterion="maxclust")

    rows = []
    for sub_id in sorted(set(sub_labels)):
        members = sub_labels == sub_id
        mean = weighted[members].mean(axis=0)
        top = features[np.argsort(-mean)][:5]
        rows.append(
            {
                "subcluster_id": int(sub_id),
                "n": int(members.sum()),
                "departments": "; ".join(core_names[members]),
                "distinctive_courses": ", ".join(top),
            }
        )
    table = pd.DataFrame(rows).sort_values("subcluster_id")
    table.to_csv(REPORT_TABLES / "core_subclusters.csv", index=False, encoding="utf-8-sig")

    fig_labels = [f"{i} {n}" for i, n in zip(core_ids, core_names)]
    plt.figure(figsize=(11, 6))
    dendrogram(z, labels=fig_labels, leaf_rotation=75, leaf_font_size=9, color_threshold=None)
    plt.title(f"Sub-clustering of the STEM-health core (local IDF, {SUB_LINKAGE})")
    plt.ylabel("Cosine distance")
    plt.tight_layout()
    plt.savefig(REPORT_FIGURES / "idf_core_subdendrogram.png", dpi=200)
    plt.close()
    return table


def kmeans_comparison(x: np.ndarray, idf: np.ndarray) -> pd.DataFrame:
    """Agreement between hierarchical (primary) and k-means clusters on IDF vectors.

    A method-robustness check: the two algorithms agree on the macro structure
    but diverge on the finer k=4 boundary. (The exact k=4 k-means membership
    is not characterised here.)
    """
    w = normalize(x * (idf ** PRIMARY_ALPHA))
    rows = []
    for k in (3, 4, 5, 6):
        hier = fcluster(linkage(pdist(w, metric="cosine"), method=LINKAGE_METHOD), t=k, criterion="maxclust")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=50).fit_predict(w)
        rows.append(
            {
                "k": k,
                "ari_hier_vs_kmeans": round(adjusted_rand_score(hier, kmeans), 3),
                "nmi_hier_vs_kmeans": round(normalized_mutual_info_score(hier, kmeans), 3),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(REPORT_TABLES / "kmeans_vs_hierarchical.csv", index=False, encoding="utf-8-sig")
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
    type_idf = save_selection_type_idf(course_columns, idf)

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
    subclusters = subcluster_core(matrix, name_col, course_columns, labels)
    km_compare = kmeans_comparison(x, idf)

    print(f"input={INPUT_MATRIX.name}  departments={len(matrix)}  features={len(course_columns)}")
    if not type_idf.empty:
        print("mean IDF by selection type (justifies per-course IDF):")
        for _, r in type_idf.iterrows():
            print(f"  {r['selection_type']}: mean_idf={r['mean_idf']} (mentions={int(r['mentions'])})")
    print(f"primary: idf alpha={PRIMARY_ALPHA}, linkage={LINKAGE_METHOD}, k={N_CLUSTERS}, silhouette={sil:.3f}")
    print("\nclusters (alpha=1, average):")
    for cid, grp in assignments.groupby("cluster_id"):
        print(f"  C{cid}: " + ", ".join(grp["department_name"]))
    print("\nrobustness (mean co-assignment over alpha sweep):")
    for _, r in robust.iterrows():
        print(f"  C{r['cluster_id']} (n={r['n']}): {r['mean_co_assignment_over_alpha']}")
    print(f"\ncore sub-clusters (largest primary cluster, local IDF, {SUB_LINKAGE}, k={CORE_SUBCLUSTERS_K}):")
    for _, r in subclusters.iterrows():
        print(f"  S{r['subcluster_id']} (n={r['n']}): {r['departments']}")
    print("\nhierarchical vs k-means agreement (IDF vectors):")
    for _, r in km_compare.iterrows():
        print(f"  k={int(r['k'])}: ARI={r['ari_hier_vs_kmeans']}, NMI={r['nmi_hier_vs_kmeans']}")
    print("\noutputs -> results/tables/keep_for_report (idf_*, course_idf_weights, "
          "weighting_sensitivity, cluster_robustness, core_subclusters), "
          "results/figures/keep_for_report/{idf_dendrogram,idf_core_subdendrogram}.png")


if __name__ == "__main__":
    main()

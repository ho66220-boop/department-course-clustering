"""Build 25-department legacy/pre-expert outputs from the current matrix.

The current project scope uses a 25-department binary subject-guide matrix.
This script keeps older output filenames available, but regenerates them from
the same 25-department matrix so GitHub tables do not mix 24- and 25-row
analysis results.
"""

from __future__ import annotations

import itertools
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"
TABLES = BASE / "results" / "tables"
REPORT_TABLES = TABLES / "keep_for_report"
DELETION_CANDIDATE_TABLES = TABLES / "deletion_candidates"
FIGURES = BASE / "results" / "figures"
REPORT_FIGURES = FIGURES / "keep_for_report"
DELETION_CANDIDATE_FIGURES = FIGURES / "deletion_candidates"
INPUT_MATRIX = PROCESSED / "department_course_matrix_refined_binary.csv"

METADATA_COLUMNS = {"department_id", "department_name", "department_name_ko", "broad_field", "selected_reason"}
EXPECTED_DEPARTMENTS = 25
CLUSTER_COUNTS = list(range(2, 9))
RANDOM_STATE = 42


def ensure_dirs() -> None:
    for directory in [PROCESSED, REPORT_TABLES, DELETION_CANDIDATE_TABLES, REPORT_FIGURES, DELETION_CANDIDATE_FIGURES]:
        directory.mkdir(parents=True, exist_ok=True)


def setup_plot_style() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def load_matrix() -> tuple[pd.DataFrame, list[str]]:
    matrix = pd.read_csv(INPUT_MATRIX, encoding="utf-8-sig")
    if len(matrix) != EXPECTED_DEPARTMENTS:
        raise ValueError(f"Expected {EXPECTED_DEPARTMENTS} departments, found {len(matrix)}.")
    if "D25" not in set(matrix["department_id"].astype(str)):
        raise ValueError("D25 자동차공학과 is missing from the matrix.")

    course_columns = [column for column in matrix.columns if column not in METADATA_COLUMNS]
    values = set(pd.unique(matrix[course_columns].to_numpy().ravel()))
    if values - {0, 1, 0.0, 1.0}:
        raise ValueError(f"Expected binary course values, found {sorted(values)}")
    return matrix, course_columns


def analysis_view(matrix: pd.DataFrame, course_columns: list[str]) -> pd.DataFrame:
    view = matrix[["department_id", "department_name_ko", *course_columns]].copy()
    return view.sort_values("department_id")


def feature_matrix(view: pd.DataFrame) -> pd.DataFrame:
    return view.drop(columns=["department_id", "department_name_ko"])


def compute_similarity(view: pd.DataFrame, suffix: str) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    x = normalize(feature_matrix(view).to_numpy(dtype=float), norm="l2")
    similarity = cosine_similarity(x)
    ids = view["department_id"].tolist()
    names = view["department_name_ko"].tolist()

    similarity_df = pd.DataFrame(similarity, index=ids, columns=ids)
    similarity_df.insert(0, "department_name_ko", names)
    similarity_df.index.name = "department_id"

    rows = []
    name_lookup = dict(zip(ids, names))
    for left, right in itertools.combinations(ids, 2):
        rows.append(
            {
                "department_id_1": left,
                "department_name_1": name_lookup[left],
                "department_id_2": right,
                "department_name_2": name_lookup[right],
                f"course_similarity_{suffix}": similarity_df.loc[left, right],
            }
        )
    pair_df = pd.DataFrame(rows).sort_values(f"course_similarity_{suffix}", ascending=False)
    return similarity_df, pair_df, similarity


def hierarchical_outputs(view: pd.DataFrame, similarity: np.ndarray, method: str, suffix: str) -> tuple[pd.DataFrame, np.ndarray]:
    ids = view["department_id"].tolist()
    names = view["department_name_ko"].tolist()
    distance = np.clip(1 - similarity, 0, 1)
    np.fill_diagonal(distance, 0)
    linkage_matrix = linkage(squareform(distance, checks=False), method=method)

    assignments = pd.DataFrame({"department_id": ids, "department_name_ko": names})
    for k in CLUSTER_COUNTS:
        assignments[f"hclust_{method}_k{k}_{suffix}"] = fcluster(linkage_matrix, t=k, criterion="maxclust")
    return assignments, linkage_matrix


def kmeans_assignments(view: pd.DataFrame, suffix: str) -> pd.DataFrame:
    x = normalize(feature_matrix(view).to_numpy(dtype=float), norm="l2")
    assignments = view[["department_id", "department_name_ko"]].copy()
    for k in CLUSTER_COUNTS:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=50)
        assignments[f"kmeans_k{k}_{suffix}"] = model.fit_predict(x) + 1
    return assignments


def kmeans_metrics(view: pd.DataFrame, suffix: str) -> pd.DataFrame:
    x = normalize(feature_matrix(view).to_numpy(dtype=float), norm="l2")
    rows = []
    for k in CLUSTER_COUNTS:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=50)
        labels = model.fit_predict(x)
        rows.append(
            {
                "vector_type": suffix,
                "k": k,
                "silhouette_cosine": silhouette_score(x, labels, metric="cosine"),
                "davies_bouldin_euclidean": davies_bouldin_score(x, labels),
                "inertia": model.inertia_,
            }
        )
    return pd.DataFrame(rows)


def plot_dendrogram(linkage_matrix: np.ndarray, view: pd.DataFrame, method: str, suffix: str) -> None:
    labels = [
        f"{department_id} {department_name}"
        for department_id, department_name in zip(view["department_id"], view["department_name_ko"])
    ]
    plt.figure(figsize=(13, 7))
    dendrogram(linkage_matrix, labels=labels, leaf_rotation=75, leaf_font_size=9, color_threshold=None)
    plt.title(f"Hierarchical clustering dendrogram ({method}, {suffix})")
    plt.ylabel("Cosine distance")
    plt.tight_layout()
    output_dir = REPORT_FIGURES if "binary" in suffix else DELETION_CANDIDATE_FIGURES
    plt.savefig(output_dir / f"dendrogram_{method}_{suffix}.png", dpi=200)
    plt.close()


def plot_heatmap(similarity: np.ndarray, view: pd.DataFrame, suffix: str) -> None:
    labels = view["department_name_ko"].tolist()
    plt.figure(figsize=(11, 9))
    plt.imshow(similarity, cmap="viridis", vmin=0, vmax=1)
    plt.colorbar(label="Cosine similarity")
    plt.xticks(range(len(labels)), labels, rotation=80, fontsize=8)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.title(f"Course similarity heatmap ({suffix})")
    plt.tight_layout()
    output_dir = REPORT_FIGURES if "binary" in suffix else DELETION_CANDIDATE_FIGURES
    plt.savefig(output_dir / f"course_similarity_heatmap_{suffix}.png", dpi=200)
    plt.close()


def score_summary(matrix: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "department_id": matrix["department_id"],
            "department_name_ko": matrix["department_name_ko"],
            "representative_score_mean": np.nan,
            "representative_score_median": np.nan,
            "university_count": 0,
            "score_record_count": 0,
        }
    )


def attach_scores(weighted_pairs: pd.DataFrame, binary_pairs: pd.DataFrame, scores: pd.DataFrame, sort_column: str) -> pd.DataFrame:
    pairs = weighted_pairs.merge(
        binary_pairs,
        on=["department_id_1", "department_name_1", "department_id_2", "department_name_2"],
        how="left",
    )
    score_lookup = scores.set_index("department_id")["representative_score_median"].to_dict()
    pairs["score_median_1"] = pairs["department_id_1"].map(score_lookup)
    pairs["score_median_2"] = pairs["department_id_2"].map(score_lookup)
    pairs["score_difference_median"] = (pairs["score_median_1"] - pairs["score_median_2"]).abs()
    return pairs.sort_values(sort_column, ascending=False)


def save_csv(df: pd.DataFrame, *paths: Path, index: bool = False) -> None:
    for path in paths:
        df.to_csv(path, index=index, encoding="utf-8-sig")


def main() -> None:
    ensure_dirs()
    setup_plot_style()

    matrix, course_columns = load_matrix()
    weighted = analysis_view(matrix, course_columns)
    binary = weighted.copy()
    refined_weighted = weighted.copy()
    refined_binary = weighted.copy()

    save_csv(matrix, PROCESSED / "department_course_matrix_weighted.csv")
    save_csv(matrix, PROCESSED / "department_course_matrix_binary.csv")
    save_csv(matrix, PROCESSED / "department_course_matrix_refined_weighted.csv")
    save_csv(matrix, PROCESSED / "department_course_matrix_refined_binary.csv")

    weighted_sim, weighted_pairs, weighted_similarity = compute_similarity(weighted, "weighted")
    binary_sim, binary_pairs, binary_similarity = compute_similarity(binary, "binary")
    refined_weighted_sim, refined_weighted_pairs, refined_weighted_similarity = compute_similarity(refined_weighted, "refined_weighted")
    refined_binary_sim, refined_binary_pairs, refined_binary_similarity = compute_similarity(refined_binary, "refined_binary")

    weighted_sim.to_csv(PROCESSED / "course_similarity_matrix_weighted.csv", encoding="utf-8-sig")
    binary_sim.to_csv(PROCESSED / "course_similarity_matrix_binary.csv", encoding="utf-8-sig")
    refined_weighted_sim.to_csv(PROCESSED / "course_similarity_matrix_refined_weighted.csv", encoding="utf-8-sig")
    refined_binary_sim.to_csv(PROCESSED / "course_similarity_matrix_refined_binary.csv", encoding="utf-8-sig")

    weighted_avg, weighted_avg_z = hierarchical_outputs(weighted, weighted_similarity, "average", "weighted")
    weighted_complete, weighted_complete_z = hierarchical_outputs(weighted, weighted_similarity, "complete", "weighted")
    binary_avg, binary_avg_z = hierarchical_outputs(binary, binary_similarity, "average", "binary")
    refined_weighted_avg, refined_weighted_avg_z = hierarchical_outputs(refined_weighted, refined_weighted_similarity, "average", "refined_weighted")
    refined_weighted_complete, refined_weighted_complete_z = hierarchical_outputs(
        refined_weighted, refined_weighted_similarity, "complete", "refined_weighted"
    )
    refined_binary_avg, refined_binary_avg_z = hierarchical_outputs(refined_binary, refined_binary_similarity, "average", "refined_binary")

    assignments = weighted_avg.merge(weighted_complete.drop(columns=["department_name_ko"]), on="department_id")
    assignments = assignments.merge(binary_avg.drop(columns=["department_name_ko"]), on="department_id")
    assignments = assignments.merge(kmeans_assignments(weighted, "weighted").drop(columns=["department_name_ko"]), on="department_id")
    assignments = assignments.merge(kmeans_assignments(binary, "binary").drop(columns=["department_name_ko"]), on="department_id")
    save_csv(assignments, PROCESSED / "cluster_assignments_pre_expert.csv", REPORT_TABLES / "cluster_assignments_pre_expert.csv")

    refined_assignments = refined_weighted_avg.merge(refined_weighted_complete.drop(columns=["department_name_ko"]), on="department_id")
    refined_assignments = refined_assignments.merge(refined_binary_avg.drop(columns=["department_name_ko"]), on="department_id")
    refined_assignments = refined_assignments.merge(
        kmeans_assignments(refined_weighted, "refined_weighted").drop(columns=["department_name_ko"]), on="department_id"
    )
    refined_assignments = refined_assignments.merge(
        kmeans_assignments(refined_binary, "refined_binary").drop(columns=["department_name_ko"]), on="department_id"
    )
    save_csv(
        refined_assignments,
        PROCESSED / "cluster_assignments_refined_pre_expert.csv",
        REPORT_TABLES / "cluster_assignments_refined_pre_expert.csv",
    )

    metrics = pd.concat(
        [
            kmeans_metrics(weighted, "weighted"),
            kmeans_metrics(binary, "binary"),
            kmeans_metrics(refined_weighted, "refined_weighted"),
            kmeans_metrics(refined_binary, "refined_binary"),
        ],
        ignore_index=True,
    )
    save_csv(metrics, REPORT_TABLES / "kmeans_internal_metrics_pre_expert.csv")

    scores = score_summary(matrix)
    save_csv(scores, PROCESSED / "admission_score_summary.csv", DELETION_CANDIDATE_TABLES / "admission_score_summary.csv")

    pair_table = attach_scores(weighted_pairs, binary_pairs, scores, "course_similarity_weighted")
    save_csv(pair_table, PROCESSED / "department_pair_pre_expert.csv", DELETION_CANDIDATE_TABLES / "department_pair_pre_expert.csv")
    save_csv(pair_table.head(30), REPORT_TABLES / "top30_course_similarity_pairs.csv")
    save_csv(pair_table.tail(30), DELETION_CANDIDATE_TABLES / "bottom30_course_similarity_pairs.csv")

    refined_pair_table = attach_scores(refined_weighted_pairs, refined_binary_pairs, scores, "course_similarity_refined_weighted")
    save_csv(
        refined_pair_table,
        PROCESSED / "department_pair_refined_pre_expert.csv",
        DELETION_CANDIDATE_TABLES / "department_pair_refined_pre_expert.csv",
    )
    save_csv(refined_pair_table.head(30), REPORT_TABLES / "top30_refined_course_similarity_pairs.csv")
    save_csv(refined_pair_table.tail(30), DELETION_CANDIDATE_TABLES / "bottom30_refined_course_similarity_pairs.csv")

    plot_dendrogram(weighted_avg_z, weighted, "average", "weighted")
    plot_dendrogram(weighted_complete_z, weighted, "complete", "weighted")
    plot_dendrogram(binary_avg_z, binary, "average", "binary")
    plot_dendrogram(refined_weighted_avg_z, refined_weighted, "average", "refined_weighted")
    plot_dendrogram(refined_weighted_complete_z, refined_weighted, "complete", "refined_weighted")
    plot_dendrogram(refined_binary_avg_z, refined_binary, "average", "refined_binary")
    plot_heatmap(weighted_similarity, weighted, "weighted")
    plot_heatmap(binary_similarity, binary, "binary")
    plot_heatmap(refined_weighted_similarity, refined_weighted, "refined_weighted")
    plot_heatmap(refined_binary_similarity, refined_binary, "refined_binary")

    print(f"departments={len(matrix)}")
    print(f"course_features={len(course_columns)}")
    print(f"pair_rows={len(pair_table)}")
    print("outputs=data/processed, results/tables, results/figures")


if __name__ == "__main__":
    main()

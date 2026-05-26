"""Legacy broad analysis script.

The current Progress-stage scope uses `src/build_progress_analysis.py` with
25 departments and binary CareerNet course vectors. This older script is kept
only for historical/future-extension reference because it includes weighted
vectors and admission-score feasibility logic.
"""

from __future__ import annotations

import itertools
import os
import pathlib

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


BASE = pathlib.Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
TABLES = BASE / "results" / "tables"
FIGURES = BASE / "results" / "figures"
GENERAL_COURSES = {"국어", "수학", "영어", "사회", "과학"}


def ensure_dirs() -> None:
    for directory in [PROCESSED, TABLES, FIGURES]:
        directory.mkdir(parents=True, exist_ok=True)


def setup_korean_font() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def load_departments() -> pd.DataFrame:
    departments = pd.read_excel(RAW / "departments_raw.xlsx", sheet_name="departments")
    departments = departments[departments["include_in_cardsort"].fillna(0).astype(int) == 1].copy()
    departments["department_id"] = departments["department_id"].astype(str)
    return departments.sort_values("department_id")


def build_course_matrices(departments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(RAW / "recommended_courses_raw.xlsx", sheet_name="recommended_courses")
    raw = raw[raw["department_id"].isin(departments["department_id"])].copy()
    raw = raw.dropna(subset=["course_name_standardized", "assigned_weight"])
    raw["assigned_weight"] = pd.to_numeric(raw["assigned_weight"], errors="coerce").fillna(0)

    evidence = (
        raw.groupby(["department_id", "department_name_ko", "course_name_standardized", "subject_group"], as_index=False)
        .agg(
            assigned_weight=("assigned_weight", "max"),
            evidence_count=("assigned_weight", "size"),
            source_count=("source_name", "nunique"),
            example_original=("course_name_original", "first"),
            example_note=("coding_note", "first"),
        )
        .sort_values(["department_id", "subject_group", "course_name_standardized"])
    )

    weighted = evidence.pivot_table(
        index="department_id",
        columns="course_name_standardized",
        values="assigned_weight",
        aggfunc="max",
        fill_value=0,
    )
    weighted = weighted.reindex(departments["department_id"]).fillna(0)
    binary = (weighted > 0).astype(int)

    names = departments.set_index("department_id")["department_name_ko"]
    weighted.insert(0, "department_name_ko", names)
    binary.insert(0, "department_name_ko", names)
    return weighted, binary, evidence


def refine_course_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    refined = matrix.drop(columns=[column for column in GENERAL_COURSES if column in matrix.columns]).copy()
    feature_columns = [column for column in refined.columns if column != "department_name_ko"]
    if not feature_columns:
        raise ValueError("refined matrix has no course feature columns")
    return refined


def compute_similarity(matrix: pd.DataFrame, suffix: str) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    feature_matrix = matrix.drop(columns=["department_name_ko"])
    normalized = normalize(feature_matrix.to_numpy(dtype=float), norm="l2")
    similarity = cosine_similarity(normalized)
    ids = matrix.index.to_list()
    names = matrix["department_name_ko"].to_dict()

    sim_df = pd.DataFrame(similarity, index=ids, columns=ids)
    sim_named = sim_df.copy()
    sim_named.insert(0, "department_name_ko", [names[item] for item in ids])

    pairs = []
    for left, right in itertools.combinations(ids, 2):
        pairs.append(
            {
                "department_id_1": left,
                "department_name_1": names[left],
                "department_id_2": right,
                "department_name_2": names[right],
                f"course_similarity_{suffix}": sim_df.loc[left, right],
            }
        )
    pair_df = pd.DataFrame(pairs).sort_values(f"course_similarity_{suffix}", ascending=False)
    return sim_named, pair_df, similarity


def hierarchical_outputs(
    matrix: pd.DataFrame,
    similarity: np.ndarray,
    method: str,
    suffix: str,
    cluster_counts: list[int],
) -> tuple[pd.DataFrame, np.ndarray]:
    ids = matrix.index.to_list()
    names = matrix["department_name_ko"].to_dict()
    distance = np.clip(1 - similarity, 0, 1)
    np.fill_diagonal(distance, 0)
    condensed = squareform(distance, checks=False)
    z = linkage(condensed, method=method)

    assignment = pd.DataFrame(
        {
            "department_id": ids,
            "department_name_ko": [names[item] for item in ids],
        }
    )
    for k in cluster_counts:
        assignment[f"hclust_{method}_k{k}_{suffix}"] = fcluster(z, t=k, criterion="maxclust")
    return assignment, z


def plot_dendrogram(z: np.ndarray, matrix: pd.DataFrame, method: str, suffix: str) -> None:
    labels = [f"{row.department_id} {row.department_name_ko}" for row in matrix.reset_index().itertuples()]
    plt.figure(figsize=(13, 7))
    dendrogram(z, labels=labels, leaf_rotation=75, leaf_font_size=9, color_threshold=None)
    plt.title(f"Hierarchical clustering dendrogram ({method}, {suffix})")
    plt.ylabel("Cosine distance")
    plt.tight_layout()
    plt.savefig(FIGURES / f"dendrogram_{method}_{suffix}.png", dpi=200)
    plt.close()


def plot_heatmap(similarity: np.ndarray, matrix: pd.DataFrame, suffix: str) -> None:
    labels = matrix["department_name_ko"].to_list()
    plt.figure(figsize=(11, 9))
    plt.imshow(similarity, cmap="viridis", vmin=0, vmax=1)
    plt.colorbar(label="Cosine similarity")
    plt.xticks(range(len(labels)), labels, rotation=80, fontsize=8)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.title(f"Course similarity heatmap ({suffix})")
    plt.tight_layout()
    plt.savefig(FIGURES / f"course_similarity_heatmap_{suffix}.png", dpi=200)
    plt.close()


def kmeans_metrics(matrix: pd.DataFrame, suffix: str, cluster_counts: list[int]) -> pd.DataFrame:
    x = normalize(matrix.drop(columns=["department_name_ko"]).to_numpy(dtype=float), norm="l2")
    rows = []
    for k in cluster_counts:
        model = KMeans(n_clusters=k, random_state=42, n_init=50)
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


def kmeans_assignments(matrix: pd.DataFrame, suffix: str, cluster_counts: list[int]) -> pd.DataFrame:
    x = normalize(matrix.drop(columns=["department_name_ko"]).to_numpy(dtype=float), norm="l2")
    assignment = pd.DataFrame(
        {
            "department_id": matrix.index,
            "department_name_ko": matrix["department_name_ko"].to_numpy(),
        }
    )
    for k in cluster_counts:
        model = KMeans(n_clusters=k, random_state=42, n_init=50)
        assignment[f"kmeans_k{k}_{suffix}"] = model.fit_predict(x) + 1
    return assignment


def summarize_admission_scores(departments: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_excel(RAW / "admission_scores_raw.xlsx", sheet_name="admission_scores")
    raw = raw[raw["department_id"].isin(departments["department_id"])].copy()
    raw["score_value"] = pd.to_numeric(raw["score_value"], errors="coerce")
    raw = raw.dropna(subset=["score_value"])

    priority = {
        "70~90%컷 등급②": 1,
        "평균/50%컷 등급": 2,
        "최저 등급": 3,
    }
    raw["score_type_priority"] = raw["score_type"].map(priority).fillna(99)
    raw = raw.sort_values(["department_id", "university", "score_type_priority", "score_value"])
    representative_by_university = raw.groupby(["department_id", "department_name_standardized", "university"], as_index=False).first()

    summary = (
        representative_by_university.groupby(["department_id", "department_name_standardized"], as_index=False)
        .agg(
            representative_score_mean=("score_value", "mean"),
            representative_score_median=("score_value", "median"),
            university_count=("university", "nunique"),
            score_record_count=("score_value", "size"),
        )
        .rename(columns={"department_name_standardized": "department_name_ko"})
        .sort_values("department_id")
    )
    return summary


def build_pair_tables(
    weighted_pairs: pd.DataFrame,
    binary_pairs: pd.DataFrame,
    score_summary: pd.DataFrame,
    sort_column: str = "course_similarity_weighted",
) -> pd.DataFrame:
    pairs = weighted_pairs.merge(
        binary_pairs,
        on=["department_id_1", "department_name_1", "department_id_2", "department_name_2"],
        how="left",
    )
    score_lookup = score_summary.set_index("department_id")["representative_score_median"].to_dict()
    pairs["score_median_1"] = pairs["department_id_1"].map(score_lookup)
    pairs["score_median_2"] = pairs["department_id_2"].map(score_lookup)
    pairs["score_difference_median"] = (pairs["score_median_1"] - pairs["score_median_2"]).abs()
    return pairs.sort_values(sort_column, ascending=False)


def main() -> None:
    ensure_dirs()
    setup_korean_font()
    cluster_counts = list(range(2, 9))

    departments = load_departments()
    weighted, binary, evidence = build_course_matrices(departments)
    refined_weighted = refine_course_matrix(weighted)
    refined_binary = (refined_weighted.drop(columns=["department_name_ko"]) > 0).astype(int)
    refined_binary.insert(0, "department_name_ko", refined_weighted["department_name_ko"])

    weighted.to_csv(PROCESSED / "department_course_matrix_weighted.csv", encoding="utf-8-sig")
    binary.to_csv(PROCESSED / "department_course_matrix_binary.csv", encoding="utf-8-sig")
    refined_weighted.to_csv(PROCESSED / "department_course_matrix_refined_weighted.csv", encoding="utf-8-sig")
    refined_binary.to_csv(PROCESSED / "department_course_matrix_refined_binary.csv", encoding="utf-8-sig")
    evidence.to_csv(PROCESSED / "course_coding_evidence.csv", index=False, encoding="utf-8-sig")

    weighted_sim, weighted_pairs, weighted_similarity = compute_similarity(weighted, "weighted")
    binary_sim, binary_pairs, binary_similarity = compute_similarity(binary, "binary")
    refined_weighted_sim, refined_weighted_pairs, refined_weighted_similarity = compute_similarity(
        refined_weighted, "refined_weighted"
    )
    refined_binary_sim, refined_binary_pairs, refined_binary_similarity = compute_similarity(refined_binary, "refined_binary")
    weighted_sim.to_csv(PROCESSED / "course_similarity_matrix_weighted.csv", encoding="utf-8-sig")
    binary_sim.to_csv(PROCESSED / "course_similarity_matrix_binary.csv", encoding="utf-8-sig")
    refined_weighted_sim.to_csv(PROCESSED / "course_similarity_matrix_refined_weighted.csv", encoding="utf-8-sig")
    refined_binary_sim.to_csv(PROCESSED / "course_similarity_matrix_refined_binary.csv", encoding="utf-8-sig")

    weighted_avg_assignment, weighted_avg_z = hierarchical_outputs(weighted, weighted_similarity, "average", "weighted", cluster_counts)
    weighted_complete_assignment, weighted_complete_z = hierarchical_outputs(
        weighted, weighted_similarity, "complete", "weighted", cluster_counts
    )
    binary_avg_assignment, binary_avg_z = hierarchical_outputs(binary, binary_similarity, "average", "binary", cluster_counts)
    refined_weighted_avg_assignment, refined_weighted_avg_z = hierarchical_outputs(
        refined_weighted, refined_weighted_similarity, "average", "refined_weighted", cluster_counts
    )
    refined_weighted_complete_assignment, refined_weighted_complete_z = hierarchical_outputs(
        refined_weighted, refined_weighted_similarity, "complete", "refined_weighted", cluster_counts
    )
    refined_binary_avg_assignment, refined_binary_avg_z = hierarchical_outputs(
        refined_binary, refined_binary_similarity, "average", "refined_binary", cluster_counts
    )

    assignments = weighted_avg_assignment.merge(
        weighted_complete_assignment.drop(columns=["department_name_ko"]), on="department_id", how="left"
    ).merge(binary_avg_assignment.drop(columns=["department_name_ko"]), on="department_id", how="left")

    kmeans_weighted = kmeans_assignments(weighted, "weighted", cluster_counts)
    kmeans_binary = kmeans_assignments(binary, "binary", cluster_counts)
    assignments = assignments.merge(kmeans_weighted.drop(columns=["department_name_ko"]), on="department_id", how="left")
    assignments = assignments.merge(kmeans_binary.drop(columns=["department_name_ko"]), on="department_id", how="left")
    assignments.to_csv(PROCESSED / "cluster_assignments_pre_expert.csv", index=False, encoding="utf-8-sig")
    assignments.to_csv(TABLES / "cluster_assignments_pre_expert.csv", index=False, encoding="utf-8-sig")

    refined_assignments = refined_weighted_avg_assignment.merge(
        refined_weighted_complete_assignment.drop(columns=["department_name_ko"]), on="department_id", how="left"
    ).merge(refined_binary_avg_assignment.drop(columns=["department_name_ko"]), on="department_id", how="left")
    kmeans_refined_weighted = kmeans_assignments(refined_weighted, "refined_weighted", cluster_counts)
    kmeans_refined_binary = kmeans_assignments(refined_binary, "refined_binary", cluster_counts)
    refined_assignments = refined_assignments.merge(
        kmeans_refined_weighted.drop(columns=["department_name_ko"]), on="department_id", how="left"
    )
    refined_assignments = refined_assignments.merge(
        kmeans_refined_binary.drop(columns=["department_name_ko"]), on="department_id", how="left"
    )
    refined_assignments.to_csv(PROCESSED / "cluster_assignments_refined_pre_expert.csv", index=False, encoding="utf-8-sig")
    refined_assignments.to_csv(TABLES / "cluster_assignments_refined_pre_expert.csv", index=False, encoding="utf-8-sig")

    metrics = pd.concat(
        [
            kmeans_metrics(weighted, "weighted", cluster_counts),
            kmeans_metrics(binary, "binary", cluster_counts),
            kmeans_metrics(refined_weighted, "refined_weighted", cluster_counts),
            kmeans_metrics(refined_binary, "refined_binary", cluster_counts),
        ]
    )
    metrics.to_csv(TABLES / "kmeans_internal_metrics_pre_expert.csv", index=False, encoding="utf-8-sig")

    score_summary = summarize_admission_scores(departments)
    score_summary.to_csv(PROCESSED / "admission_score_summary.csv", index=False, encoding="utf-8-sig")
    score_summary.to_csv(TABLES / "admission_score_summary.csv", index=False, encoding="utf-8-sig")

    pair_table = build_pair_tables(weighted_pairs, binary_pairs, score_summary)
    pair_table.to_csv(PROCESSED / "department_pair_pre_expert.csv", index=False, encoding="utf-8-sig")
    pair_table.to_csv(TABLES / "department_pair_pre_expert.csv", index=False, encoding="utf-8-sig")
    pair_table.head(30).to_csv(TABLES / "top30_course_similarity_pairs.csv", index=False, encoding="utf-8-sig")
    pair_table.tail(30).to_csv(TABLES / "bottom30_course_similarity_pairs.csv", index=False, encoding="utf-8-sig")

    refined_pair_table = build_pair_tables(
        refined_weighted_pairs,
        refined_binary_pairs,
        score_summary,
        sort_column="course_similarity_refined_weighted",
    )
    refined_pair_table.to_csv(PROCESSED / "department_pair_refined_pre_expert.csv", index=False, encoding="utf-8-sig")
    refined_pair_table.to_csv(TABLES / "department_pair_refined_pre_expert.csv", index=False, encoding="utf-8-sig")
    refined_pair_table.head(30).to_csv(TABLES / "top30_refined_course_similarity_pairs.csv", index=False, encoding="utf-8-sig")
    refined_pair_table.tail(30).to_csv(
        TABLES / "bottom30_refined_course_similarity_pairs.csv", index=False, encoding="utf-8-sig"
    )

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

    print(f"departments={len(departments)}")
    print(f"courses={weighted.shape[1] - 1}")
    print(f"refined_courses={refined_weighted.shape[1] - 1}")
    print(f"pair_rows={len(pair_table)}")
    print(f"refined_pair_rows={len(refined_pair_table)}")
    print(f"evidence_rows={len(evidence)}")
    print("outputs=data/processed, results/tables, results/figures")


if __name__ == "__main__":
    main()

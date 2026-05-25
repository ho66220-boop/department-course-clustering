from __future__ import annotations

import pathlib

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


BASE = pathlib.Path(__file__).resolve().parents[1]
INPUT_MATRIX = BASE / "data" / "processed" / "department_course_matrix_refined_weighted.csv"
TABLES = BASE / "results" / "tables"
FIGURES = BASE / "results" / "figures"

METADATA_COLUMNS = {
    "department_id",
    "department_name",
    "department_name_ko",
    "broad_field",
    "selected_reason",
}
VALID_COURSE_VALUES = {0.0, 0.5, 1.0}
N_CLUSTERS = 4


def ensure_dirs() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)


def setup_plot_style() -> None:
    matplotlib.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def load_matrix(path: pathlib.Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input matrix not found: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def get_name_column(matrix: pd.DataFrame) -> str:
    if "department_name" in matrix.columns:
        return "department_name"
    if "department_name_ko" in matrix.columns:
        return "department_name_ko"
    raise ValueError("Matrix must include either department_name or department_name_ko")


def get_course_columns(matrix: pd.DataFrame) -> list[str]:
    course_columns = [column for column in matrix.columns if column not in METADATA_COLUMNS]
    if not course_columns:
        raise ValueError("No course columns found. Metadata columns cannot be used for clustering.")
    return course_columns


def validate_matrix(matrix: pd.DataFrame, course_columns: list[str]) -> None:
    errors: list[str] = []

    if len(matrix) != 24:
        errors.append(f"Expected 24 departments, found {len(matrix)}.")
    if "department_id" not in matrix.columns:
        errors.append("Missing department_id column.")
    elif matrix["department_id"].duplicated().any():
        duplicated = matrix.loc[matrix["department_id"].duplicated(), "department_id"].tolist()
        errors.append(f"Duplicated department_id values: {duplicated}")

    missing_values = int(matrix[course_columns].isna().sum().sum())
    if missing_values:
        errors.append(f"Course columns contain {missing_values} missing values.")

    values = pd.unique(matrix[course_columns].to_numpy().ravel())
    invalid_values = sorted({float(value) for value in values if pd.notna(value) and float(value) not in VALID_COURSE_VALUES})
    if invalid_values:
        errors.append(f"Invalid course values found: {invalid_values}. Allowed values are 0.0, 0.5, 1.0.")

    all_zero_rows = matrix.loc[(matrix[course_columns].fillna(0) == 0).all(axis=1), "department_id"].tolist()
    if all_zero_rows:
        errors.append(f"Departments with all-zero course values: {all_zero_rows}")

    forbidden = [column for column in matrix.columns if any(term in column.lower() for term in ["expert", "consensus", "admission", "score", "candidate"])]
    if forbidden:
        errors.append(f"Future-work columns must not be included in the clustering matrix: {forbidden}")

    if errors:
        raise ValueError("Matrix validation failed:\n- " + "\n- ".join(errors))


def compute_similarity(matrix: pd.DataFrame, course_columns: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    x = matrix[course_columns].to_numpy(dtype=float)
    x_normalized = normalize(x, norm="l2")
    similarity = cosine_similarity(x_normalized)

    ids = matrix["department_id"].tolist()
    name_column = get_name_column(matrix)
    similarity_df = pd.DataFrame(similarity, index=ids, columns=ids)
    similarity_df.insert(0, "department_name", matrix[name_column].tolist())
    similarity_df.index.name = "department_id"
    return similarity_df, similarity


def plot_heatmap(similarity: np.ndarray, matrix: pd.DataFrame) -> None:
    name_column = get_name_column(matrix)
    labels = matrix[name_column].tolist()

    plt.figure(figsize=(11, 9))
    plt.imshow(similarity, cmap="viridis", vmin=0, vmax=1)
    plt.colorbar(label="Cosine similarity")
    plt.xticks(range(len(labels)), labels, rotation=80, fontsize=8)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.title("Course-profile cosine similarity")
    plt.tight_layout()
    plt.savefig(FIGURES / "course_similarity_heatmap.png", dpi=200)
    plt.close()


def hierarchical_cluster(matrix: pd.DataFrame, similarity: np.ndarray) -> tuple[pd.DataFrame, np.ndarray]:
    distance = np.clip(1 - similarity, 0, 1)
    np.fill_diagonal(distance, 0)
    linkage_matrix = linkage(squareform(distance, checks=False), method="average")
    cluster_labels = fcluster(linkage_matrix, t=N_CLUSTERS, criterion="maxclust")

    name_column = get_name_column(matrix)
    assignments = pd.DataFrame(
        {
            "department_id": matrix["department_id"],
            "department_name": matrix[name_column],
            "cluster_id": cluster_labels,
        }
    ).sort_values(["cluster_id", "department_id"])
    return assignments, linkage_matrix


def plot_dendrogram(linkage_matrix: np.ndarray, matrix: pd.DataFrame) -> None:
    name_column = get_name_column(matrix)
    labels = [f"{row.department_id} {getattr(row, name_column)}" for row in matrix.itertuples()]

    plt.figure(figsize=(13, 7))
    dendrogram(linkage_matrix, labels=labels, leaf_rotation=75, leaf_font_size=9, color_threshold=None)
    plt.title("Hierarchical clustering dendrogram")
    plt.ylabel("Cosine distance")
    plt.tight_layout()
    plt.savefig(FIGURES / "hierarchical_dendrogram.png", dpi=200)
    plt.close()


def summarize_clusters(matrix: pd.DataFrame, assignments: pd.DataFrame, course_columns: list[str]) -> pd.DataFrame:
    name_column = get_name_column(matrix)
    matrix_with_clusters = matrix.merge(assignments[["department_id", "cluster_id"]], on="department_id", how="left")
    rows = []

    for cluster_id, group in matrix_with_clusters.groupby("cluster_id"):
        course_means = group[course_columns].mean().sort_values(ascending=False)
        common_courses = [course for course, value in course_means.items() if value > 0]
        top_courses = common_courses[:5]
        departments = "; ".join(group[name_column].tolist())
        characteristics = ", ".join(top_courses) if top_courses else "No common non-zero course features"
        interpretation = (
            "Preliminary cluster based on shared detailed recommended-course features: "
            + characteristics
        )
        rows.append(
            {
                "cluster_id": int(cluster_id),
                "departments": departments,
                "common_course_characteristics": characteristics,
                "preliminary_interpretation": interpretation,
            }
        )

    return pd.DataFrame(rows).sort_values("cluster_id")


def main() -> None:
    ensure_dirs()
    setup_plot_style()

    # Progress-stage input: metadata columns are kept for labels only.
    # Only course columns enter cosine similarity and clustering.
    matrix = load_matrix(INPUT_MATRIX)
    course_columns = get_course_columns(matrix)
    validate_matrix(matrix, course_columns)

    similarity_df, similarity = compute_similarity(matrix, course_columns)
    similarity_df.to_csv(TABLES / "course_similarity_matrix.csv", encoding="utf-8-sig")
    plot_heatmap(similarity, matrix)

    assignments, linkage_matrix = hierarchical_cluster(matrix, similarity)
    assignments.to_csv(TABLES / "hierarchical_cluster_assignments.csv", index=False, encoding="utf-8-sig")
    plot_dendrogram(linkage_matrix, matrix)

    cluster_summary = summarize_clusters(matrix, assignments, course_columns)
    cluster_summary.to_csv(TABLES / "cluster_summary.csv", index=False, encoding="utf-8-sig")

    print(f"input={INPUT_MATRIX}")
    print(f"departments={len(matrix)}")
    print(f"course_features={len(course_columns)}")
    print(f"clusters={N_CLUSTERS}")
    print("outputs=results/tables, results/figures")


if __name__ == "__main__":
    main()

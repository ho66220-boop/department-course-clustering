# Course-Based Clustering of Academic Departments for Admission Counseling Support

## 1. Project Overview

This repository contains an exploratory clustering project for the NOVA50301 AI Toolkit term project.

The project explores whether recommended high-school course profiles can be used to cluster academic departments in an interpretable way for college admission counseling support. The goal is not to build a complete department recommendation system. Instead, the project focuses on constructing department-course vectors and examining whether the resulting clusters reflect meaningful course-preparation patterns across departments.

The main analytical object is a department-course matrix for 25 selected academic departments. Recommended high-school elective subjects listed in `학과 과목 선택 가이드.xlsx` are coded into binary vectors, then compared using cosine similarity and clustering methods.

## 2. Research Question

The main research question is:

> Can recommended high-school course profiles produce interpretable clusters of academic departments for admission counseling support?

The project also considers two supporting questions:

1. How can recommended-course information be converted into department-course vectors?
2. Does down-weighting courses common to many departments (inverse document frequency) produce more interpretable and field-consistent clusters than an unweighted baseline vector?

## 3. Why 25 Departments?

The project uses 25 selected departments.

The 25 departments were selected as a purposive sample to maximize course-profile diversity and counseling relevance, while keeping the analysis interpretable within the scope of a short exploratory clustering study.

This means the departments are not intended to be a statistically representative sample of all academic departments. They were selected to include departments with different preparation patterns, counseling relevance, and boundary cases such as humanities/social science, engineering, natural science, health/medical, design, and interdisciplinary fields.

Shipbuilding and Ocean Engineering and Automotive Engineering are included as industry-specific engineering boundary cases related to the Ulsan regional industrial context. These two departments are not treated as statistically representative of all industry-specific departments; they are exploratory cases for examining how applied engineering fields are positioned in course-based clustering.

More detail is provided in `docs/department_selection_rationale.md`.

## 4. Data Structure

The core data source is recommended high-school elective subject information matched to the 25 departments in `학과 과목 선택 가이드.xlsx`.

The main data objects are:

- `data/raw/departments_raw.xlsx`: selected department list
- `data/raw/recommended_courses_raw.xlsx`: raw recommended-course evidence
- `data/processed/course_coding_evidence.csv`: cleaned evidence for department-course coding
- `data/processed/department_course_matrix_binary.csv`: baseline binary matrix
- `data/processed/department_course_matrix_idf_weighted.csv`: IDF-weighted matrix (main analysis input)
- `results/tables/keep_for_report/course_idf_weights.csv`: per-course document frequency and IDF weight

The main matrix uses the following binary coding rule:

| Value | Meaning |
| ---: | --- |
| 1 | Listed as a related high-school elective subject in the subject selection guide |
| 0 | Not listed |

The baseline vector uses the raw binary presence of each course, so a near-ubiquitous course such as 확률과 통계 (listed by 21 of 25 departments) is as influential as a highly department-specific one. Because the guide lists specific elective subjects rather than broad subject labels, simply deleting broad labels is not applicable here. The main analysis instead re-weights each course by inverse document frequency (IDF), `weight = ln(N / df)`, which down-weights widely shared courses with no hand-tuned parameter. The chosen weighting is supported by a sensitivity sweep in `results/tables/keep_for_report/weighting_sensitivity.csv`.

The cleaned schema for a simplified department-course matrix is documented in `docs/department_course_matrix_schema.md`. In that schema, `department_id`, `department_name`, `broad_field`, and `selected_reason` are metadata columns and should not be used as clustering features.

## 5. Method

The analysis follows these steps:

1. Build a department-course matrix from recommended-course evidence.
2. Construct baseline binary vectors.
3. Construct IDF-weighted vectors (`weight = ln(N / df)`) to down-weight courses common to many departments.
4. Compute cosine similarity between department vectors.
5. Apply hierarchical clustering (average linkage) as the main clustering method.
6. Use k-means clustering as a comparison method.
7. Compare baseline and IDF-weighted results using cluster interpretability, recovery of academic-field structure (ARI/NMI against `broad_field`), and a weighting-sensitivity sweep. Silhouette is reported but interpreted with caution, because it rewards a single dominant cluster and therefore favours the undifferentiated baseline.

The project treats clustering results as exploratory patterns, not as final department recommendations.

## 6. Progress Meeting Scope

The Progress Meeting focuses on the completed pre-final analysis:

- construction of department-course matrices
- baseline binary versus IDF-weighted vector design
- cosine similarity computation
- hierarchical clustering results
- k-means comparison
- weighting-sensitivity analysis
- preliminary dendrogram and heatmap interpretation
- initial discussion of limitations

Main progress-stage outputs (IDF-weighted analysis) include:

- `results/figures/keep_for_report/idf_dendrogram.png`
- `results/figures/keep_for_report/idf_core_subdendrogram.png`
- `results/tables/keep_for_report/idf_cluster_assignments.csv`
- `results/tables/keep_for_report/idf_cluster_summary.csv`
- `results/tables/keep_for_report/core_subclusters.csv`
- `results/tables/keep_for_report/course_idf_weights.csv`
- `results/tables/keep_for_report/weighting_sensitivity.csv`
- `results/tables/keep_for_report/cluster_robustness.csv`

Expert card-sorting outputs (`src/build_card_sorting_analysis.py`):

- `results/figures/keep_for_report/cardsort_cooccurrence_heatmap.png`
- `results/figures/keep_for_report/cardsort_agreement_bars.png`
- `results/figures/keep_for_report/cardsort_consensus_dendrogram.png`
- `results/figures/keep_for_report/cardsort_cooccur_vs_idf_scatter.png`
- `results/tables/keep_for_report/cardsort_agreement.csv`
- `results/tables/keep_for_report/cardsort_consensus_assignments.csv`
- `results/tables/keep_for_report/cardsort_department_ambiguity.csv`
- `results/tables/keep_for_report/cardsort_disagreement_pairs.csv` (internal-vs-external divergence)

The baseline binary outputs (`hierarchical_cluster_assignments.csv`, `cluster_summary.csv`, `course_similarity_matrix.csv`, `course_similarity_heatmap.png`, `hierarchical_dendrogram.png`) are retained for the baseline-versus-IDF comparison.

Report-relevant outputs are kept under `keep_for_report/`. Earlier weighted-vector variants are not used as evidence and are not version-controlled.

Some generated file names still contain `pre_expert` for historical reasons. Expert card-sorting validation is conducted separately from the Progress Meeting core clustering analysis (see Section 8) and is not required for the Progress Meeting milestone.

## 7. Expected Final Report Scope

The final 5-page report will focus on the course-based clustering analysis.

Expected report components:

1. Motivation and research question
2. Explanation of the 25-department purposive sample
3. Department-course matrix construction
4. Baseline and IDF-weighted vector design
5. Cosine similarity and clustering methods
6. Preliminary clustering results
7. Expert card-sorting validation (consensus co-grouping versus clustering, ARI/NMI)
8. Discussion of interpretability, limitations, and future extensions

The final report will not claim that the project recommends departments automatically. The intended claim is that recommended-course profiles can provide an interpretable basis for exploratory department clustering.

## 8. Expert Validation and Future Extensions

Expert card-sorting validation is complete, separate from the Progress Meeting core clustering analysis. Fourteen practicing admission consultants independently grouped the 25 departments by recommended-course similarity in an open card sort, with no constraint on the number of groups. Responses were aggregated into a 25-by-25 co-occurrence matrix to derive a consensus clustering, then compared with the algorithmic clusters using Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI). The IDF clustering matches the expert consensus far better than the binary baseline (k=4 ARI 0.85 vs 0.59; co-occurrence vs IDF cosine r=0.68), which externally validates the IDF weighting choice. Outputs: `results/figures/keep_for_report/cardsort_*.png` and `results/tables/keep_for_report/cardsort_*.csv` (the raw response workbook holds real respondent names and is not version-controlled).

The following components remain genuine future extensions, outside the core scope of the current term project:

- admission score feasibility analysis
- disagreement case analysis between course-based similarity and expert co-grouping
- candidate-generation tables for counseling workflows
- validation of the clustering output in real counseling settings

These extensions may help evaluate practical usefulness later, but they are not part of the current term project.

## 9. Repository Structure

```text
department-course-clustering/
|- data/
|  |- raw/          # Raw department and recommended-course files
|  |- processed/    # Analysis-ready matrices, similarities, and cluster outputs
|  |- interim/      # Intermediate files if needed
|  `- external/     # Source Excel files used for raw data construction
|- docs/            # Project design, selection rationale, and matrix schema notes
|- reports/
|  `- progress/     # Progress Meeting materials
|- results/
|  |- figures/      # Dendrograms and heatmaps
|  `- tables/       # Cluster assignments, metrics, and similarity tables
|- src/             # Reproducible data processing and analysis code
`- templates/       # Core data templates and optional future-extension templates
```

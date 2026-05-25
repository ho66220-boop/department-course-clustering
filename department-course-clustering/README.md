# Course-Based Clustering of Academic Departments for Admission Counseling Support

## 1. Project Overview

This repository contains an exploratory clustering project for the NOVA50301 AI Toolkit term project.

The project explores whether recommended high-school course profiles can be used to cluster academic departments in an interpretable way for college admission counseling support. The goal is not to build a complete department recommendation system. Instead, the project focuses on constructing department-course vectors and examining whether the resulting clusters reflect meaningful course-preparation patterns across departments.

The main analytical object is a department-course matrix for 24 selected academic departments. Recommended high-school subjects are coded into weighted and binary vectors, then compared using cosine similarity and clustering methods.

## 2. Research Question

The main research question is:

> Can recommended high-school course profiles produce interpretable clusters of academic departments for admission counseling support?

The project also considers two supporting questions:

1. How can recommended-course information be converted into department-course vectors?
2. Does a refined course vector, excluding broad subject labels, produce more interpretable clusters than a baseline vector?

## 3. Why 24 Departments?

The project uses 24 selected departments.

The 24 departments were selected as a purposive sample to maximize course-profile diversity and counseling relevance, while keeping the analysis interpretable within the scope of a short exploratory clustering study.

This means the departments are not intended to be a statistically representative sample of all academic departments. They were selected to include departments with different preparation patterns, counseling relevance, and boundary cases such as humanities/social science, engineering, natural science, health/medical, design, and interdisciplinary fields.

More detail is provided in `docs/department_selection_rationale.md`.

## 4. Data Structure

The core data source is recommended high-school course information matched to the 24 departments.

The main data objects are:

- `data/raw/departments_raw.xlsx`: selected department list
- `data/raw/recommended_courses_raw.xlsx`: raw recommended-course evidence
- `data/processed/course_coding_evidence.csv`: cleaned evidence for department-course coding
- `data/processed/department_course_matrix_weighted.csv`: baseline weighted matrix
- `data/processed/department_course_matrix_binary.csv`: baseline binary matrix
- `data/processed/department_course_matrix_refined_weighted.csv`: refined weighted matrix
- `data/processed/department_course_matrix_refined_binary.csv`: refined binary matrix

The weighted matrix uses the following coding rule:

| Value | Meaning |
| ---: | --- |
| 1.0 | Core recommended course |
| 0.5 | Related or supporting recommended course |
| 0.0 | Not mentioned |

The baseline vector includes all standardized course features. The refined vector removes broad common subject labels such as Korean, general mathematics, English, general social studies, and general science so that clustering is driven more by detailed course features.

The cleaned schema for a simplified department-course matrix is documented in `docs/department_course_matrix_schema.md`. In that schema, `department_id`, `department_name`, `broad_field`, and `selected_reason` are metadata columns and should not be used as clustering features.

## 5. Method

The analysis follows these steps:

1. Build a department-course matrix from recommended-course evidence.
2. Construct baseline weighted and binary vectors.
3. Construct refined weighted and binary vectors by excluding broad subject labels.
4. Compute cosine similarity between department vectors.
5. Apply hierarchical clustering as the main clustering method.
6. Use k-means clustering as a comparison method.
7. Compare baseline and refined results using cluster interpretability and internal metrics such as silhouette score and Davies-Bouldin index.

The project treats clustering results as exploratory patterns, not as final department recommendations.

## 6. Progress Meeting Scope

The Progress Meeting focuses on the completed pre-final analysis:

- construction of department-course matrices
- baseline versus refined vector design
- cosine similarity computation
- hierarchical clustering results
- k-means comparison
- preliminary dendrogram and heatmap interpretation
- initial discussion of limitations

Main progress-stage outputs include:

- `results/figures/dendrogram_average_refined_weighted.png`
- `results/figures/course_similarity_heatmap_refined_weighted.png`
- `results/tables/cluster_assignments_refined_pre_expert.csv`
- `results/tables/top30_refined_course_similarity_pairs.csv`
- `results/tables/kmeans_internal_metrics_pre_expert.csv`

Some generated file names still contain `pre_expert` for historical reasons. In the simplified Progress Meeting scope, expert consensus analysis is treated as future work and is not part of the main clustering analysis.

## 7. Expected Final Report Scope

The final 5-page report will focus on the course-based clustering analysis.

Expected report components:

1. Motivation and research question
2. Explanation of the 24-department purposive sample
3. Department-course matrix construction
4. Baseline and refined vector design
5. Cosine similarity and clustering methods
6. Preliminary clustering results
7. Discussion of interpretability, limitations, and future extensions

The final report will not claim that the project recommends departments automatically. The intended claim is that recommended-course profiles can provide an interpretable basis for exploratory department clustering.

## 8. Future Extensions

The following components are treated as future extensions, not as core Progress Meeting tasks:

- expert consensus using consultant card sorting
- comparison between course-based similarity and expert co-grouping
- admission score feasibility analysis
- disagreement case analysis
- candidate-generation tables for counseling workflows
- validation of the clustering output in real counseling settings

These extensions may help evaluate practical usefulness later, but they are outside the simplified core scope of the current term project.

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

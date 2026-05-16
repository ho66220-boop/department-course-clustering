# Pre-Expert Analysis Summary

This note summarizes the analysis stage completed before consultant card-sorting responses are collected.

## Completed Outputs

- Built weighted department-course matrix from `recommended_courses_raw.xlsx`.
- Built binary department-course matrix as a sensitivity check.
- Computed 24 x 24 cosine similarity matrices.
- Generated 276 department-pair similarity table.
- Ran hierarchical clustering with cosine distance.
- Ran k-means baseline for k = 2 to 8.
- Summarized admission score data by department for later disagreement interpretation.

## Main Files

- `data/processed/department_course_matrix_weighted.csv`
- `data/processed/department_course_matrix_binary.csv`
- `data/processed/course_similarity_matrix_weighted.csv`
- `data/processed/course_similarity_matrix_binary.csv`
- `data/processed/department_pair_pre_expert.csv`
- `data/processed/cluster_assignments_pre_expert.csv`
- `data/processed/admission_score_summary.csv`
- `results/figures/dendrogram_average_weighted.png`
- `results/figures/dendrogram_complete_weighted.png`
- `results/figures/course_similarity_heatmap_weighted.png`

## Preliminary Findings

The weighted matrix contains 24 departments and 33 standardized course features. Each department-course cell uses the maximum coded recommendation weight across source evidence, rather than raw mention frequency, to avoid over-weighting departments with more source rows.

The average-linkage hierarchical clustering result shows a broad split between humanities/social-science-oriented departments and science/engineering/medical-oriented departments. In the weighted k = 4 result, the first cluster contains Korean language and literature, psychology, business, sociology, media communication, and history. Design appears as a separate cluster, while most science, engineering, health, and quantitative departments are grouped together. Industrial engineering and naval architecture/ocean engineering form a separate engineering-oriented branch.

At k = 6, the science/engineering side becomes more interpretable: mechanical engineering, materials, mathematics, life science, chemical engineering, electrical/electronic engineering, statistics, and computer science form one group, while architecture, chemistry, medicine, pharmacy, economics, food nutrition, and nursing form another. Industrial engineering and naval architecture/ocean engineering remain relatively isolated.

K-means internal metrics prefer a coarse k = 2 split for both weighted and binary vectors. This is useful as a baseline, but the hierarchical dendrogram is more informative for this project because the counseling problem does not require a fixed number of clusters in advance.

## Points To Validate With Experts

- Medicine and pharmacy have extremely high course similarity, but expert consensus may be lower or more conditional because of score feasibility and counseling context.
- Some humanities/social-science departments are close in course space because many source descriptions use broad subject-level recommendations.
- Industrial engineering and naval architecture/ocean engineering may be separated because their source evidence is narrower or less consistently represented.
- Score difference should not be used as a clustering feature, but it is ready as an interpretation variable for high-similarity/low-consensus or low-similarity/high-consensus cases.

## Next Step After Card Sorting

Convert consultant responses into pairwise expert consensus for all 276 department pairs, then merge that table with `department_pair_pre_expert.csv`. The key validation analyses will be Spearman correlation between course similarity and expert consensus, same-cluster versus different-cluster consensus comparison, and disagreement case analysis using admission score difference.

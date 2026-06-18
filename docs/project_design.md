# Project Design Notes

## Project Positioning

This project is an exploratory clustering study for the NOVA50301 AI Toolkit term project.

The project examines whether recommended high-school course profiles can be converted into department-course vectors and used to produce interpretable clusters of academic departments for admission counseling support.

The project should be described as:

> an exploratory course-based clustering study of academic departments.

It should not be described as a complete department recommendation system.

## Simplified Core Scope

The core scope is intentionally limited to the following:

1. Use 25 selected academic departments.
2. Treat the 25 departments as a purposive sample, not as a statistically representative sample.
3. Build a department-course matrix from recommended high-school course evidence.
4. Compare baseline and IDF-weighted course vectors.
5. Compute cosine similarity between department vectors.
6. Apply hierarchical clustering as the main clustering method.
7. Use k-means clustering as a comparison method.
8. Interpret preliminary clusters as exploratory patterns.

The 25 departments were selected to maximize course-profile diversity, counseling relevance, interpretability, and feasibility within a 5-page term project. Shipbuilding and Ocean Engineering and Automotive Engineering are included as Ulsan-related industry-specific engineering boundary cases, not as statistically representative examples of all industry-specific departments.

## Unit Of Analysis

- Department-level analysis: 25 departments
- Pairwise similarity analysis: 300 department pairs

The pairwise table is used to inspect course-based similarity between departments. It should not be interpreted as a final recommendation list.

## Main Variables

| Variable | Level | Role | Description |
| --- | --- | --- | --- |
| `course_feature` | department-course | clustering feature | Coded recommended-course feature value |
| `course_similarity` | pair | similarity output | Cosine similarity from department-course vectors |
| `cluster_assignment` | department | clustering output | Cluster label from hierarchical clustering or k-means |
| `broad_field` | department | metadata | Broad academic field label, not used for clustering |
| `selected_reason` | department | metadata | Short rationale for including the department, not used for clustering |

Only course-feature columns should be used as clustering inputs. Metadata columns such as `department_id`, `department_name`, `broad_field`, and `selected_reason` must be excluded from the feature matrix.

## Vector Design

The baseline vector uses the raw binary presence of each course.

The main analysis re-weights each course by inverse document frequency (IDF), `weight = ln(N / df)`, so that courses listed by many departments (for example 확률과 통계, listed by 21 of 25 departments) contribute less than department-specific courses. The subject guide lists specific elective subjects rather than broad subject labels, so deleting broad labels is not applicable to this data; IDF is the data-driven, parameter-free way to express the same intent of reducing the influence of widely shared courses.

The weighting strength is examined with a single-knob sensitivity sweep (`weight = idf ** alpha`, where `alpha = 0` is the unweighted baseline and `alpha = 1` is standard IDF).

The main binary coding rule is:

| Value | Meaning |
| ---: | --- |
| `1` | Listed as a related high-school elective subject in `학과 과목 선택 가이드.xlsx` |
| `0` | Not listed |

Repeated mentions are not summed. The matrix records whether a related elective subject is listed for the department in the guide.

## Progress Meeting Scope

The Progress Meeting should focus on:

- department-course matrix construction
- baseline versus IDF-weighted vector design
- cosine similarity
- hierarchical clustering
- k-means comparison
- preliminary dendrogram and heatmap interpretation
- limitations of the exploratory analysis

This is sufficient for the Progress Meeting requirement of implementing at least one clustering method and presenting preliminary results.

## Expert Validation (Complete)

Expert card-sorting validation is complete, distinct from the Progress Meeting core clustering analysis. Fourteen practicing admission consultants independently grouped the 25 departments by recommended-course similarity in an open card sort; responses were aggregated into a 25-by-25 co-occurrence matrix and compared with the clustering output using ARI and NMI. The IDF clustering matches the expert consensus much better than the binary baseline (k=4 ARI 0.85 vs 0.59; co-occurrence vs IDF cosine r=0.68), externally validating the IDF choice. The medical/bio-health boundary is genuinely fuzzy among experts, and 건축/디자인 are the least-agreed boundary departments (max co-classification 0.14). Reproduced by `src/build_card_sorting_analysis.py`.

## Future Work

The following remain genuine future extensions, not core term-project tasks:

- admission score feasibility analysis
- candidate-generation tables
- real counseling workflow validation

These extensions may be discussed briefly in the final report, but they should not be framed as completed analysis unless explicitly implemented later.

## Recommended Final Claim

Strong claim to avoid:

> This model recommends departments automatically.

Safer claim to use:

> Recommended high-school course profiles can provide an interpretable basis for exploratory clustering of academic departments for admission counseling support.

# Project Design Notes

## Project Positioning

This project is an exploratory clustering study for the NOVA50301 AI Toolkit term project.

The project examines whether recommended high-school course profiles can be converted into department-course vectors and used to produce interpretable clusters of academic departments for admission counseling support.

The project should be described as:

> an exploratory course-based clustering study of academic departments.

It should not be described as a complete department recommendation system.

## Simplified Core Scope

The core scope is intentionally limited to the following:

1. Use 24 selected academic departments.
2. Treat the 24 departments as a purposive sample, not as a statistically representative sample.
3. Build a department-course matrix from recommended high-school course evidence.
4. Compare baseline and refined course vectors.
5. Compute cosine similarity between department vectors.
6. Apply hierarchical clustering as the main clustering method.
7. Use k-means clustering as a comparison method.
8. Interpret preliminary clusters as exploratory patterns.

The 24 departments were selected to maximize course-profile diversity, counseling relevance, interpretability, and feasibility within a 5-page term project.

## Unit Of Analysis

- Department-level analysis: 24 departments
- Pairwise similarity analysis: 276 department pairs

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

The baseline vector includes all standardized course features.

The refined vector removes broad subject-level labels such as Korean, general mathematics, English, general social studies, and general science. This refinement is used because broad subject labels appear across many departments and can reduce department-specific discriminative power.

The refined vector keeps more specific course features, such as calculus, geometry, probability/statistics, physics, chemistry, biology, earth science, information, economics, and ethics.

The weighted coding rule is:

| Value | Meaning |
| ---: | --- |
| `1.0` | Core recommended course |
| `0.5` | Related or supporting recommended course |
| `0.0` | Not mentioned |

If the same department-course pair appears in multiple sources, the maximum coded value is used rather than summing repeated mentions.

## Progress Meeting Scope

The Progress Meeting should focus on:

- department-course matrix construction
- baseline versus refined vector design
- cosine similarity
- hierarchical clustering
- k-means comparison
- preliminary dendrogram and heatmap interpretation
- limitations of the exploratory analysis

This is sufficient for the Progress Meeting requirement of implementing at least one clustering method and presenting preliminary results.

## Future Work

The following are future extensions, not core Progress Meeting tasks:

- expert consensus using consultant card sorting
- comparison between course-based similarity and expert co-grouping
- admission score feasibility analysis
- disagreement case analysis
- candidate-generation tables
- real counseling workflow validation

These extensions may be discussed briefly in the final report, but they should not be framed as completed core analysis unless explicitly implemented later.

## Recommended Final Claim

Strong claim to avoid:

> This model recommends departments automatically.

Safer claim to use:

> Recommended high-school course profiles can provide an interpretable basis for exploratory clustering of academic departments for admission counseling support.

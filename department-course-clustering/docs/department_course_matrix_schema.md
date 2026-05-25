# Department-Course Matrix Schema

This note defines the cleaned data structure for the simplified project scope. The goal is to build a department-course matrix for 24 academic departments and use the course-feature columns for cosine similarity, hierarchical clustering, and k-means clustering.

The template file is a blank structural template. It is not a clustering-ready matrix until the course-feature values are populated from recommended-course evidence.

## Final CSV Schema

Recommended template file:

```text
templates/data_collection/department_course_matrix_template.csv
```

Required metadata columns:

| Column | Role | Use in clustering |
| --- | --- | --- |
| `department_id` | Stable department identifier | No |
| `department_name` | Department name | No |
| `broad_field` | Broad academic field label | No |
| `selected_reason` | Short rationale for inclusion in the 24-department purposive sample | No |

Recommended refined course-feature columns:

| Column | Role | Use in clustering |
| --- | --- | --- |
| `calculus` | Calculus or advanced calculus preparation | Yes |
| `geometry` | Geometry preparation | Yes |
| `probability_statistics` | Probability and statistics preparation | Yes |
| `physics` | Physics preparation | Yes |
| `chemistry` | Chemistry preparation | Yes |
| `biology` | Biology or life science preparation | Yes |
| `earth_science` | Earth science preparation | Yes |
| `information` | Information, computing, or AI-related preparation | Yes |
| `economics` | Economics preparation | Yes |
| `ethics` | Ethics or philosophy-related preparation | Yes |
| `other_relevant_courses` | Other relevant recommended courses not captured above | Yes |

Only the refined course-feature columns should be used as clustering features. Metadata columns must be excluded before computing cosine similarity or fitting clustering models.

The refined matrix intentionally excludes broad common subject labels such as Korean, general mathematics, English, general social studies, and general science. These broad labels are useful for baseline documentation, but they are not used in the main refined clustering input because they appear across many departments and can obscure department-specific preparation patterns.

## Coding Rule

Each department-course cell should use the following coding rule:

| Value | Meaning |
| ---: | --- |
| `1.0` | Core recommended course |
| `0.5` | Related or supporting recommended course |
| `0.0` | Not mentioned |

If the same department-course pair appears in multiple sources, use the maximum coded value rather than summing repeated mentions. This prevents departments with more source rows from being over-weighted.

## Clustering Input

For cosine similarity, hierarchical clustering, and k-means clustering, the feature matrix should exclude:

- `department_id`
- `department_name`
- `broad_field`
- `selected_reason`

The clustering input should include only numeric refined course-feature columns. It should not include metadata columns, broad common subject columns, expert consensus, admission score feasibility, candidate-generation variables, or any other future-work variables.

## Validation Expectations

A clustering-ready matrix should satisfy the following checks:

- exactly 24 department rows
- no duplicate `department_id`
- no duplicate `department_name`
- non-empty `broad_field`
- non-empty or documented `selected_reason`
- course-feature values limited to `0.0`, `0.5`, and `1.0`
- no missing values in course-feature columns
- no department row with all course-feature values equal to `0.0`
- no course-feature column entirely equal to `0.0` unless intentionally retained and documented
- no expert consensus, admission score, or candidate-generation columns

The blank template may fail the all-zero row and all-zero column checks by design. Those checks must pass before the matrix is used for cosine similarity or clustering.

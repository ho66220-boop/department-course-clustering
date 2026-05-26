# Raw Data Plan

## Collection Principle

Raw data should be collected only to the extent needed for the simplified project goal:

> building department-course vectors and testing whether recommended high-school course profiles produce interpretable department clusters.

The project does not require exhaustive nationwide department data, multi-year admission data, or student-level counseling records. A controlled and explainable scope is more appropriate for a 5-page exploratory clustering report.

## Core Raw Data

### 1. Department List

Core file:

```text
data/raw/departments_raw.xlsx
```

The file defines the 25 selected departments used in the clustering analysis.

Recommended fields:

| Field | Description |
| --- | --- |
| `department_id` | Stable department ID |
| `department_name_ko` | Korean department name |
| `broad_category` | Broad academic field, used as metadata only |
| `boundary_flag` | Whether the department is a boundary/interdisciplinary case |
| `note` | Rationale or context for inclusion |

The 25 departments are a purposive sample. They are not intended to statistically represent all university departments. Shipbuilding and Ocean Engineering and Automotive Engineering are included as Ulsan-related industry-specific engineering boundary cases for exploratory analysis.

### 2. Recommended Courses

Core file:

```text
data/raw/recommended_courses_raw.xlsx
```

This is the main raw data source for constructing department-course vectors.

Recommended fields:

| Field | Description |
| --- | --- |
| `department_id` | Stable department ID |
| `department_name_ko` | Department name |
| `source_type` | Type of source |
| `source_name` | Source title |
| `source_url_or_file` | URL or file reference |
| `course_name_original` | Course text as written in the source |
| `course_name_standardized` | Standardized course feature |
| `subject_group` | Broad subject group |
| `recommendation_level_original` | Original recommendation wording |
| `binary_value` | `1` if listed as a related high-school elective subject in `학과 과목 선택 가이드.xlsx`, otherwise `0` |
| `coding_rule` | Rule used for assigning the binary value |
| `coding_note` | Matching or coding note |
| `source_access_date` | Access or processing date |

## Processed Core Data

Core processed outputs should include:

- department-course matrix
- refined department-course matrix
- cosine similarity matrix
- clustering assignments
- clustering metrics

Metadata columns such as department ID, department name, broad field, and selected reason should not be used as clustering features.

## Future-Extension Data

The following data may be useful later but is outside the simplified core scope:

- consultant card sorting responses
- expert consensus scores
- admission score or grade-cut data
- candidate-generation tables
- real counseling workflow data

These data sources should be treated as future work unless explicitly added to a later final-stage analysis.

## Data Not Recommended For The Current Scope

Avoid adding these to the current Progress Meeting scope:

- all departments nationwide
- all universities and recruitment units
- multi-year full admission score histories
- student-level counseling history
- individual pass/fail records
- consultant real-name comparison data

These would increase cleaning, privacy, and interpretation risks without being necessary for the current exploratory clustering study.

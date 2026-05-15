# Raw Data Collection Plan

## Collection Principle

Raw data should be collected only to the extent needed for the project goal:

> testing whether course-based clustering can support practical admission counseling.

The project does not need nationwide exhaustive admission data. A controlled and explainable scope is better.

## Required Raw Data

### 1. Department List

Fixed scope: 24 departments used in card sorting.

Fill this file:

```text
data/raw/departments_raw.xlsx
```

Fields:

| Field | Description |
| --- | --- |
| department_id | Stable department ID |
| department_name_ko | Korean department name |
| broad_category | Traditional broad category, for reference only |
| note | Boundary or counseling-context note |

### 2. Recommended Courses

This is the main raw data for course vectors.

Fill this file:

```text
data/raw/recommended_courses_raw.xlsx
```

Sources:

- 대교협 권장 이수과목 자료
- 커리어넷 학과정보
- public high-school course-selection guidance where useful

Fields:

| Field | Description |
| --- | --- |
| department_name | Standardized department name |
| source | Source name |
| source_url_or_file | URL or file reference |
| course_name_original | Course name as written in source |
| course_name_standardized | Standardized course feature name |
| recommendation_level_original | Original wording |
| assigned_weight | 1.0 / 0.5 / 0.0 |
| coding_note | Why this weight was assigned |

### 3. Card Sorting Responses

Raw individual responses from 14 consultants.

Save response files here:

```text
data/raw/card_sorting_responses/
```

Fields:

| Field | Description |
| --- | --- |
| respondent_id | T01-T14 in processed data |
| department_name | Department name |
| group_number | Group number assigned by respondent |
| memo | Optional ambiguity note |
| response_date | Date received |

Personal names should be removed from processed/public data.

## Recommended Additional Raw Data

### 4. Admission Grade/Cut Data

This data is needed for practical feasibility interpretation.

Fill this file:

```text
data/raw/admission_scores_raw.xlsx
```

Recommended university scope:

- 부산대
- 경북대
- 전남대
- 충남대
- 충북대
- 전북대
- 강원대
- 경상국립대
- 울산대

Optional additions:

- 부경대
- 동아대

Fields:

| Field | Description |
| --- | --- |
| university | University name |
| admission_year | Admission year |
| admission_type | 교과 / 종합 / 지역인재 등 |
| unit_name_original | Original recruitment unit name |
| department_name_standardized | Matched one of the 24 departments |
| score_value | Grade/cut/percentile value |
| score_type | 평균 / 70% cut / 최종등록자 등 |
| source | Source file or URL |
| matching_note | Department-name matching note |

## Data Not Recommended at This Stage

Avoid collecting these in the first version:

- all universities nationwide
- all departments and recruitment units
- 3-5 years of full admission data
- student-level counseling history
- individual pass/fail records
- consultant real-name comparison data

These would increase privacy, cleaning, and scope risks without being necessary for the term project.

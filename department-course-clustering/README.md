# Department Course Clustering

NOVA50301 Term Project repository for analyzing department similarity from recommended high-school course selections and validating the result against real admission-consulting judgments.

이 프로젝트의 핵심 목표는 단순히 군집 결과를 만드는 것이 아니라, **진학 상담 현장에서 사용할 수 있는 유사 학과 추천 후보군 생성 방식**을 검토하는 것입니다.

## Practical Motivation

In real admission counseling, a consultant often recommends multiple departments to one student. Official discipline categories such as humanities, social science, natural science, engineering, and medicine are useful, but they do not fully explain practical recommendation decisions.

This project defines department similarity as:

> the likelihood that two departments can be recommended together to the same student.

The project combines three views of similarity:

1. **Course similarity**: Are the recommended high-school courses similar?
2. **Expert consensus**: Do admission consultants group the departments together?
3. **Admission score feasibility**: Are the departments realistically comparable in grade/cut range?

## Research Questions

1. How does a recommended-course vector represent similarity between departments?
2. How well does course-based similarity align with admission consultants' co-recommendation consensus?
3. When course similarity and expert consensus disagree, can admission score difference help explain the gap?
4. Can the result be converted into a practical candidate-generation table for admission counseling?

## Expected Practical Output

The final result should not stop at a dendrogram. The intended counseling-oriented output is a table like this:

| Input department | Candidate department | Course similarity | Expert consensus | Score difference | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Chemistry | Chemical Engineering | high | high | small | Similar preparation and practical co-recommendation |
| Chemistry | Pharmacy | high | low | large | Course preparation overlaps, but grade feasibility may differ |
| Mathematics | Applied Statistics | high | high | small | Strong practical candidate pair |

This is framed as an **early prototype for recommendation support**, not as a complete automated recommendation system.

## Repository Structure

```text
department-course-clustering/
├─ data/
│  ├─ raw/          # Original private data: responses, admission cut data
│  ├─ interim/      # Intermediate cleaned data
│  ├─ processed/    # Analysis-ready de-identified data
│  └─ external/     # Public source materials and source notes
├─ docs/            # Design notes, raw data plan, practical-use plan
├─ notebooks/       # Exploratory analysis notebooks
├─ reports/
│  ├─ progress/     # Progress report materials
│  ├─ final/        # Final report materials
│  └─ slides/       # Presentation slides
├─ results/
│  ├─ figures/      # Dendrograms, heatmaps, plots
│  └─ tables/       # Pairwise consensus, recommendation candidate tables
├─ src/             # Reproducible analysis code
└─ templates/
   └─ card_sorting/ # Consultant response and collection templates
```

## Design Documents

- [Project design](docs/project_design.md): research positioning, variables, modeling decisions
- [Raw data collection plan](docs/raw_data_plan.md): what to collect and what to exclude
- [Practical use plan](docs/practical_use_plan.md): how the result can support admission counseling

## Data Collection Templates

- [Department list template](templates/data_collection/departments_template.csv)
- [Recommended courses template](templates/data_collection/recommended_courses_template.csv)
- [Admission scores template](templates/data_collection/admission_scores_template.csv)
- [Card sorting long-format template](templates/data_collection/card_sorting_long_template.csv)
- [Raw source register template](templates/data_collection/raw_source_register_template.csv)

CareerNet collection helper:

```powershell
$env:CAREERNET_API_KEY="YOUR_API_KEY"
python src/collect_careernet_majors.py --out data/raw/careernet_major_raw.json
```

Fill-in Excel templates are also prepared under `data/raw/`:

- `data/raw/departments_raw.xlsx`
- `data/raw/recommended_courses_raw.xlsx`
- `data/raw/admission_scores_raw.xlsx`
- `data/raw/raw_source_register.xlsx`
- `data/raw/collection_checklist.xlsx`
- `data/raw/card_sorting_responses/`

## Current Scope

- Departments: 24
- Department pairs: 276
- Expert evaluators: 14 admission consultants
- Main clustering feature: recommended-course vector
- Admission score data: interpretation variable, not clustering feature
- Practical target: candidate-generation support for counseling

## Core Data

### 1. Course Vector

Recommended high-school courses are converted into a department x course matrix.

| Value | Meaning |
| --- | --- |
| 1.0 | Core recommended course |
| 0.5 | Related or supporting recommended course |
| 0.0 | Not mentioned |

The main analysis uses the weighted vector. A binary vector is used as a sensitivity check.

### 2. Expert Consensus

Consultants sort 24 departments into groups based on whether they would recommend those departments together to one student.

```text
expert_consensus(i, j) =
  number of consultants who grouped i and j together
  / number of valid responses for both i and j
```

### 3. Admission Score Difference

Admission cut/grade data is collected for national flagship universities and local universities where available. It is used only to interpret disagreement cases.

```text
score_difference(i, j) = |representative_score_i - representative_score_j|
```

## Analysis Plan

1. Build the recommended-course matrix.
2. Compute cosine similarity after normalization.
3. Run hierarchical clustering as the main clustering method.
4. Run k-means as a baseline.
5. Convert card sorting responses into pairwise expert consensus.
6. Compare course similarity with expert consensus.
7. Extract disagreement cases.
8. Interpret disagreement using score difference and qualitative notes.
9. Produce a counseling-oriented candidate table.

## Card Sorting Files

`templates/card_sorting/` contains:

- `CardSorting_distribution_individual_response.xlsx`: individual response file for consultants
- `CardSorting_master_improved.xlsx`: master file for collecting responses and computing expert consensus

## Data Privacy

Raw consultant responses, private admission score files, and internal company data should not be uploaded to a public GitHub repository. Public files should be limited to:

- empty templates
- de-identified processed data
- reproducible analysis code
- public figures/tables
- reports and slides

## Status

- Card sorting templates prepared
- 24-department evaluation design prepared
- Course-vector feature set to be finalized
- University/admission-score scope to be finalized
- Practical recommendation-output format added to the project design

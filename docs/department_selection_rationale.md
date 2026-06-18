# Department Selection Rationale

This project uses 25 academic departments as the unit of clustering analysis. The 25 departments are not intended to statistically represent all university departments. Instead, they were selected as a purposive sample for a short exploratory clustering study.

The purpose of the selection is to test whether recommended high-school course profiles can produce interpretable department clusters for admission counseling support. Because the project is designed as a 5-page term project, the department set needs to be broad enough to show meaningful differences in course-preparation patterns, but small enough to keep the analysis interpretable.

## Selection Criteria

The 25 departments were selected according to four criteria:

1. **Course-profile diversity**: The sample should include departments with different expected high-school course preparation patterns.
2. **Counseling relevance**: The departments should be relevant to real admission counseling situations, where students often compare or consider multiple adjacent fields.
3. **Interpretability**: The clusters should be understandable within a short exploratory report.
4. **Feasibility**: The scope should be manageable within a 5-page term project and a short progress presentation.

## Coverage Of Course-Preparation Patterns

The selected departments include fields with different course-preparation patterns:

- **Math/physics-oriented fields**: examples include mechanical engineering, electrical and electronic engineering, naval architecture and ocean engineering, automotive engineering, and related engineering fields.
- **Chemistry/materials-related fields**: examples include chemistry, chemical engineering, and materials science and engineering.
- **Biology/health-related fields**: examples include life science, medicine, pharmacy, nursing, and food and nutrition.
- **Information/math-related fields**: examples include mathematics, applied statistics, computer science, and industrial engineering.
- **Selected social science and humanities fields**: examples include economics, business, psychology, sociology, media communication, Korean language and literature, and history.

This mixture allows the clustering analysis to examine whether recommended-course vectors can distinguish broad preparation patterns as well as boundary cases between adjacent fields.

## Ulsan Regional Industry Boundary Cases

Shipbuilding and Ocean Engineering and Automotive Engineering are included because they are industry-specific applied engineering fields related to the Ulsan regional industrial context. Their inclusion helps the project examine whether applied engineering departments with strong regional relevance are positioned near general engineering fields, physics-oriented fields, or other course-preparation patterns in a course-based clustering result.

These two departments should not be interpreted as statistically representative of all industry-specific departments. They are exploratory boundary cases that make the department set more relevant to local admission counseling while preserving the limited scope of a short exploratory clustering study.

## Why Not Only Engineering Departments Across Multiple Universities?

An alternative scope would be to focus only on engineering departments across multiple universities. That design would be useful for comparing institutional differences, but it would be less suitable for this exploratory clustering project.

First, an engineering-only sample would reduce course-profile diversity because many engineering departments share similar math and science preparation requirements. Second, it would make the project more about university-level variation than department-level course-preparation similarity. Third, it would provide fewer contrasts with social science, health, humanities, and interdisciplinary departments, making it harder to evaluate whether the vector representation produces interpretable clusters across a broader counseling context.

For this reason, the current project prioritizes diversity across selected departments rather than exhaustive coverage within one field.

## Limitations

The results cannot be generalized to all academic departments. The 25 departments are a purposive sample, not a statistically representative sample. The goal is to test whether course-profile-based vectors produce interpretable and practically useful clustering patterns, not to build a full department recommendation system.

Expert card-sorting validation is complete (14 admission consultants): at the macro level (k=3) both IDF and binary clusterings match the consensus strongly (ARI 0.84), while the top-level k=4 partition agrees only modestly (IDF 0.52, binary 0.59); IDF's benefit is limited to earlier medical-health separation (k=5 vs binary's k=7), feature discrimination, and k=5–6 agreement. Admission score feasibility and candidate-generation tables are treated as possible future extensions rather than core components of the current progress-stage analysis.

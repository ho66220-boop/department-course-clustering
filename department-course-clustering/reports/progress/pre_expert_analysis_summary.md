# Legacy Pre-Expert Analysis Summary

This file is kept as historical context only. It was produced before the project was refocused to the current 25-department subject-guide binary-vector scope.

For the current Progress Meeting, use the IDF-weighted analysis:

- `reports/progress/progress_report_one_page_draft.md`
- `src/build_idf_weighted_analysis.py` (main); `src/build_progress_analysis.py` (baseline binary, for comparison)
- `results/figures/keep_for_report/idf_dendrogram.png`
- `results/tables/keep_for_report/idf_cluster_assignments.csv`
- `results/tables/keep_for_report/idf_cluster_summary.csv`
- `results/tables/keep_for_report/weighting_sensitivity.csv`
- `results/tables/keep_for_report/cluster_robustness.csv`

Current framing:

- The project is an exploratory clustering study, not a complete recommendation system.
- The selected departments are a purposive sample, not a statistically representative sample.
- The current scope uses 25 departments.
- Course-feature values should be binary: `1` if a related high-school elective subject is listed in `학과 과목 선택 가이드.xlsx`, and `0` if it is not listed.
- Expert card-sorting validation is now in progress as an external-validation component, reported in the Final Report; admission score feasibility and candidate generation remain future work.

Earlier weighted outputs and `pre_expert` file names should not be used as the main Progress-stage evidence unless they are explicitly regenerated and reframed under the current scope.

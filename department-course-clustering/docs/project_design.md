# Project Design Notes

## Project Positioning

This project is a clustering analysis project with a practical counseling goal.

The academic task is to analyze department similarity through clustering. The practical task is to test whether the clustering result can support admission consultants by generating reasonable candidate departments for a student.

The project should be described as:

> an early prototype for department candidate generation in admission counseling.

It should not be described as a complete recommendation system.

## Unit of Analysis

- Department-level analysis: 24 departments
- Pairwise analysis: 276 department pairs

## Main Variables

| Variable | Level | Role | Description |
| --- | --- | --- | --- |
| course_similarity | pair | main signal | Cosine similarity from recommended-course vectors |
| cluster_co_membership | pair | clustering output | Whether two departments belong to the same algorithmic cluster |
| expert_consensus | pair | practical validation | Fraction of consultants who grouped the pair together |
| score_difference | pair | feasibility interpretation | Difference in representative admission grade/cut |

## Three Views of Practical Similarity

### 1. Course Preparation Similarity

This is measured by the recommended-course vector. It answers:

> Do these departments require similar high-school course preparation?

### 2. Expert Co-Recommendation Similarity

This is measured by card sorting consensus. It answers:

> Would consultants recommend these departments together to one student?

### 3. Admission Feasibility Similarity

This is measured by admission score difference. It answers:

> Are these departments realistic alternatives for a similar grade band?

## Recommended Modeling Decisions

- Use hierarchical clustering as the main clustering method.
- Use k-means only as a baseline comparison.
- Treat admission score data as an interpretation variable, not as a clustering feature.
- Report binary-vector sensitivity analysis to reduce concern about the 1.0/0.5 weighting rule.
- Report disagreement cases instead of hiding them. Disagreement is useful for practical interpretation.

## Practical Output Design

The final report should include at least one counseling-oriented output table.

Suggested columns:

| Column | Meaning |
| --- | --- |
| input_department | Department selected as a starting point |
| candidate_department | Similar or co-recommended department |
| course_similarity | Similarity based on recommended-course vector |
| expert_consensus | Consultant co-recommendation ratio |
| score_difference | Difference in representative grade/cut |
| interpretation | Practical explanation for counseling use |

Suggested interpretation categories:

| Pattern | Meaning |
| --- | --- |
| high course similarity + high expert consensus | Strong practical candidate pair |
| high course similarity + low expert consensus | Similar preparation, but practical recommendation differs |
| low course similarity + high expert consensus | Different preparation, but consultants see them as alternatives |
| low course similarity + low expert consensus | Weak candidate pair |

## Practical Risks

- Some consultants may leave items blank.
- Some consultants may use one very large group or too many singleton groups.
- Admission score data may not align cleanly across universities and departments.
- Department names may differ between sources.
- Grade/cut data differs by year, admission type, and reporting standard.

These risks should be handled through documentation, sensitivity analysis, and conservative interpretation.

## Recommended Final Claim

Strong claim to avoid:

> This model recommends departments automatically.

Safer claim to use:

> This analysis can support consultants by generating interpretable candidate department pairs based on course preparation, expert consensus, and admission feasibility.


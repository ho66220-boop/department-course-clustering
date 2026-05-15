# Practical Use Plan

## Practical Question

The practical question is:

> Can course-based department clustering help consultants generate reasonable alternative department candidates?

This is different from asking whether the algorithm can replace consultants.

## Counseling Workflow Assumption

The intended use case is:

1. A student shows interest in one or more departments.
2. The consultant checks course-preparation similarity.
3. The consultant checks whether experts tend to co-recommend similar pairs.
4. The consultant checks whether admission score ranges are practically comparable.
5. The consultant uses the result as a candidate list, not as a final recommendation.

## Prototype Output

For each input department, produce a candidate table.

| Rank | Candidate department | Course similarity | Expert consensus | Score difference | Counseling note |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | TBD | TBD | TBD | TBD | Strong candidate |
| 2 | TBD | TBD | TBD | TBD | Similar courses but check feasibility |
| 3 | TBD | TBD | TBD | TBD | Expert-supported alternative |

## Interpretation Rules

| Pattern | Counseling Interpretation |
| --- | --- |
| High course similarity, high expert consensus, small score difference | Strong practical alternative |
| High course similarity, low expert consensus | Course overlap exists, but consultants do not naturally recommend together |
| Low course similarity, high expert consensus | Consultants see a practical alternative beyond course preparation |
| High course similarity, large score difference | Academically related but may target different grade bands |

## Minimum Evidence Needed

To argue practical usefulness, the final report should include:

1. A dendrogram or heatmap showing course-based structure.
2. A pairwise table comparing course similarity and expert consensus.
3. A small set of disagreement cases.
4. A candidate-generation table for 2-3 example input departments.
5. A limitation paragraph explaining that final recommendations remain consultant-mediated.


# Future Practical Use Plan

## Status Of This Document

This document describes possible future extensions. It is not part of the simplified core Progress Meeting scope.

The current term project is limited to exploratory course-based clustering of academic departments. It does not build a complete department recommendation system.

## Current Core Project

The core project asks:

> Can recommended high-school course profiles produce interpretable clusters of academic departments for admission counseling support?

The current analysis focuses on:

- department-course matrix construction
- baseline and IDF-weighted course vectors
- cosine similarity
- hierarchical clustering
- k-means comparison
- preliminary cluster interpretation

## Possible Future Practical Workflow

A future counseling-support workflow could use the clustering results as one input among several:

1. A student shows interest in one or more departments.
2. A counselor inspects course-preparation similarity.
3. Expert consensus is checked if consultant card sorting data are available.
4. Admission score feasibility is checked if comparable score data are available.
5. The counselor uses the result as supporting information, not as an automatic recommendation.

This workflow is not implemented as part of the current simplified project.

## Expert Validation (In Progress)

Expert card-sorting validation — expert consensus, the comparison between course-based similarity and expert co-grouping, and disagreement-case analysis — is already in progress and is reported in the Final Report (see the project README, Section 8). It is a validation component, separate from the practical-use workflow described above.

## Future Extensions

The following remain future work and are not required Progress Meeting deliverables:

- admission score feasibility analysis
- candidate-generation tables for counseling examples
- validation in real counseling settings

## Risk Of Overextension

Adding admission scores and candidate-generation tables too early can make the project look like a recommendation system. It can also expand the report beyond the scope of a 5-page exploratory clustering study.

For the current term project, the safer claim is:

> Course-profile vectors can support exploratory analysis of department similarity, but final counseling decisions require human interpretation and additional validation.

# 권장과목 기반 학과 군집화: 입시 상담 지원을 위한 탐색적 분석

**Progress Update · NOVA50301 AI Toolkit**

## 핵심 질문과 범위

본 프로젝트의 핵심 질문은 “고등학교 권장과목 profile이 학과들을 해석 가능한 방식으로 군집화할 수 있는가?”이다. 이 연구는 완성된 학과 추천 시스템을 만드는 것이 아니라, 학과별 선택과목 profile을 벡터화하여 학과 간 준비과목 유사성을 탐색하는 Progress-stage clustering project이다.

## 데이터와 표본

분석 대상은 25개 학과이다. 이 25개 학과는 전체 학과를 통계적으로 대표하기 위한 표본이 아니라, course-profile diversity, counseling relevance, interpretability를 고려하여 선정한 purposive sample이다. 특히 조선해양공학과와 자동차공학과는 울산 지역 산업 맥락을 반영한 industry-specific engineering boundary case로 포함하였다. 원자료는 `학과 과목 선택 가이드.xlsx`이며, A열은 학과명, B-D열은 각각 일반선택, 진로선택, 융합선택 과목으로 구성되어 있다. 각 학과-과목 값은 가이드에 제시되면 `1`, 제시되지 않으면 `0`으로 코딩하였다.

## 분석 절차

분석 pipeline은 다음과 같다. 첫째, 25개 학과의 선택과목 정보를 long-form evidence로 변환하였다. 둘째, 이를 25 × 92 binary department-course matrix로 구성하였다. 셋째, metadata columns인 `department_id`, `department_name`, `broad_field`, `selected_reason`은 제외하고 course columns만 clustering feature로 사용하였다. 넷째, cosine similarity를 계산하고 average-linkage hierarchical clustering을 적용하였다.

## 예비 결과

현재 결과에서는 공학, 자연과학, 의약/보건, 정량 계열 학과들이 큰 quantitative/STEM-health cluster로 묶였고, 사회과학 중심 학과들은 별도 군집을 형성하였다. 국어국문학과와 디자인학과는 각각 singleton cluster로 나타났다. 상위 유사도 pair에서는 화학과-화학공학과, 경영학과-경제학과가 매우 높게 나타났으며, 자동차공학과는 기계공학과 및 전기전자공학과와 높은 유사도를 보였다. 이는 산업 특화 공학 boundary case가 권장과목 profile상 어디에 위치하는지 논의할 수 있는 예비 근거를 제공한다.

## 다음 단계와 한계

이 결과는 exploratory pattern으로 해석해야 하며, 학과 추천의 최종 판단으로 사용하지 않는다. 다음 단계에서는 k-means clustering과 cluster-number sensitivity를 추가하여 방법 간 안정성을 확인하고, 큰 군집과 singleton cluster의 해석 한계를 정리할 예정이다. 전문가 card sorting 기반 외부 검증은 현재 진행 중이며 Final Report에서 일치도(ARI/NMI)를 보고한다. admission score feasibility와 candidate generation은 future work로 남겨둔다.

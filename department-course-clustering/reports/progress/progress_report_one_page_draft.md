# 권장과목 기반 학과 군집화: 입시 상담 지원을 위한 탐색적 분석

**Progress Update · NOVA50301 AI Toolkit**

## 핵심 질문과 범위

본 프로젝트의 핵심 질문은 “고등학교 권장과목 profile이 학과들을 해석 가능한 방식으로 군집화할 수 있는가?”이다. 이 연구는 완성된 학과 추천 시스템을 만드는 것이 아니라, 학과별 선택과목 profile을 벡터화하여 학과 간 준비과목 유사성을 탐색하는 Progress-stage clustering project이다.

## 데이터와 표본

분석 대상은 25개 학과이다. 이 25개 학과는 전체 학과를 통계적으로 대표하기 위한 표본이 아니라, course-profile diversity, counseling relevance, interpretability를 고려하여 선정한 purposive sample이다. 특히 조선해양공학과와 자동차공학과는 울산 지역 산업 맥락을 반영한 industry-specific engineering boundary case로 포함하였다. 원자료는 `학과 과목 선택 가이드.xlsx`이며, A열은 학과명, B-D열은 각각 일반선택, 진로선택, 융합선택 과목으로 구성되어 있다. 각 학과-과목 값은 가이드에 제시되면 `1`, 제시되지 않으면 `0`으로 코딩하였다.

## 분석 절차

분석 pipeline은 다음과 같다. 첫째, 25개 학과의 선택과목 정보를 long-form evidence로 변환하였다. 둘째, 이를 25 × 92 binary department-course matrix로 구성하였다. 셋째, metadata columns인 `department_id`, `department_name`, `broad_field`, `selected_reason`은 제외하고 course columns만 clustering feature로 사용하였다. 넷째, 흔한 과목의 영향을 줄이기 위해 각 과목을 inverse document frequency(IDF, `w=ln(N/df)`)로 가중한 뒤 cosine similarity를 계산하고 average-linkage hierarchical clustering을 적용하였다. 가중 강도는 단일 knob(`idf^alpha`)로 민감도 분석하였다.

## 예비 결과

IDF 가중(α=1, k=4) 결과, (i) 공학-자연-생명 코어 14개 학과, (ii) 의약-보건(의예·약학·간호), (iii) 사회·상경·인문 6개 학과, (iv) 국어국문·디자인의 구조가 나타났다. 특히 무가중 baseline에서는 STEM·보건이 하나의 17개 대군집으로 뭉쳐 k=7에서야 분리되던 의약-보건 군집이, IDF 가중 시 k=4에서 분리된다. 무가중 대비 학과 계열 구조와의 일치도가 향상되었고(ARI 0.32→0.47, NMI 0.57→0.64), 최대 군집 비중(68%→56%)과 singleton 수(2→0)도 개선되었다. 상위 유사도 pair에서는 화학과-화학공학과·경영학과-경제학과(cos=1.00), 기계공학과-자동차공학과(cos=0.89)가 직관과 일치하였다.

## 다음 단계와 한계

이 결과는 exploratory pattern으로 해석해야 하며, 학과 추천의 최종 판단으로 사용하지 않는다. silhouette은 IDF 가중에서 오히려 낮아지는데(0.33→0.18), 이는 무변별 대군집을 해체했기 때문이며 silhouette이 조밀한 단일 군집을 보상하는 한계를 보여준다 — 따라서 타당성의 주 기준으로 삼지 않는다. 14개 공학-자연 코어를 subset 내 IDF로 재가중하여 sub-clustering하면 modern engineering hub(기계·전기전자·컴퓨터·자동차), material-chemistry-bio(화학·신소재·조선해양·생명·화학공학·식품영양), quantitative/systems(수학·응용통계·건축·산업)로 분리되며, 자동차공학은 modern engineering hub에 안정적으로 속한다. 다음 단계에서는 k-means clustering과 cluster-number sensitivity 비교를 추가할 예정이다. 전문가 card sorting 기반 외부 검증은 현재 진행 중이며 Final Report에서 일치도(ARI/NMI)를 보고한다. admission score feasibility와 candidate generation은 future work로 남겨둔다.

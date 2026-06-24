<!--
  GitHub README 초안 (포트폴리오용). 루트 README.md는 건드리지 않음.
  검토 후 루트로 승격할지 여부는 사용자가 결정.
  주의: 전문가 개인정보·원자료(카드소팅 응답 원본, 입결 원자료)는 절대 포함하지 말 것.
-->

# 권장과목 기반 학과 군집화와 전문가 검증

고등학교 **권장과목 데이터만으로** 대학 학과들을 군집화하고, 현직 입시 컨설턴트 14명의
**카드소팅으로 외부 검증**한 탐색적 데이터 분석 프로젝트. 입시 상담에서 컨설턴트의 경험적 직관에
의존하던 "권장과목 관점에서 비슷한 학과" 판단을 데이터로 재현·보완할 수 있는지 검증한다.

> 완성된 추천 시스템이 아니라, 상담을 보조하는 신호를 찾는 탐색적 분석입니다.

## 한눈에 보는 결과

- **거시 구조(k=3)는 전문가 합의와 방향상 일치** — ARI 점추정 0.84 (14명 소패널이라 신뢰구간은 넓음, 방향성 위주 해석).
- **IDF 가중의 이점은 세분 구조에 제한적** — 쌍체 부트스트랩 기준 **k=6에서만** binary 대비 우위가 비교적 견고(차이 95% CI [0.06, 0.32]), k=5는 경향 수준.
- **내부-외부 불일치를 Type 1 / Type 2로 구조화**하여 상담 워크플로우(교차 계열 대안 / 과목 정합성 경고)로 연결.

## 방법 요약

| 단계 | 내용 |
|---|---|
| 데이터화 | 25개 학과 × 89개 권장과목 → binary matrix |
| 유사도 | IDF 가중 cosine similarity (파라미터 없는 `w = ln(N/df)`) |
| 군집화 | average linkage hierarchical clustering (+ k-means 비교) |
| 외부 검증 | 컨설턴트 14명 카드소팅 → 25×25 동시분류 → consensus clustering, ARI 비교 |
| 불확실성 | rater/feature/쌍체 부트스트랩 (B=1000, seed 고정) — Jaccard 안정성·ARI CI |

## 대표 그림

`reports/final/figures_v2/`

- `idf_dendrogram.png` — IDF 가중 군집(k=4, 군집명 표기)
- `idf_core_subdendrogram.png` — STEM-보건 코어의 하위 군집화
- `cardsort_cooccurrence_heatmap.png` — 전문가 동시분류 행렬(군집 경계 강조)
- `cardsort_agreement_bars.png` — 알고리즘 vs 전문가 ARI(부트스트랩 95% CI)
- `cardsort_cooccur_vs_idf_scatter.png` — 내부 유사도 vs 외부 합의(불일치 쌍 표시)
- `cardsort_department_ambiguity_bars.png` — 학과별 합의 강도

## 재현 방법

```bash
# 1) 권장과목 binary matrix 구성
python src/build_matrix_from_subject_guide.py

# 2) IDF 군집화 + 민감도 + 코어 하위 군집 안정성(feature bootstrap)
python src/build_idf_weighted_analysis.py

# 3) 카드소팅 집계 + consensus + ARI + rater bootstrap CI
#    (카드소팅 원자료는 개인정보 포함으로 비공개 — 집계 산출물만 생성)
python src/build_card_sorting_analysis.py

# 4) 포트폴리오용 그림 재생성(계산 불변, cosmetic만)
python src/build_portfolio_figures_v2.py
```

산출물은 `results/tables/keep_for_report/`, `results/figures/keep_for_report/`,
`reports/final/figures_v2/`에 생성됩니다.

## 보고서

- 개정본(v2): `reports/final/권장과목_학과군집화_소논문_v2.tex` (IEEEtran, 한국어)
- 변경 이력: `reports/final/REVISION_NOTES.md`
- 포트폴리오 요약: `reports/final/PORTFOLIO_SUMMARY.md`

## 한계

목적 표본(25개 학과)·소패널(14명)·성과 미검증의 한계가 있으며, 일치도의 크기는 단정하지 않고
방향성 위주로 해석합니다. 자세한 내용은 보고서 §한계 및 후속 연구 참조.

## 데이터·개인정보

카드소팅 응답 원자료와 입결 원자료는 개인정보·민감정보를 포함하므로 저장소에 포함하지 않으며
(`.gitignore` 처리), 분석에는 집계된 산출물만 사용합니다.

## 기술 스택

Python (NumPy · pandas · scipy · scikit-learn · matplotlib), LaTeX (IEEEtran), Git.

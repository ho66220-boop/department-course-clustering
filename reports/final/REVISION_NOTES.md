# REVISION NOTES — 권장과목 학과군집화 소논문 v2

제출본(`reports/latex_progress/main.tex`)은 **보존**하고, 포트폴리오/후속 연구용 개정본을
별도 파일로 작성하였다.

- 개정본 본문: `reports/final/권장과목_학과군집화_소논문_v2.tex`
- 개정본 그림: `reports/final/figures_v2/` (6종, 재생성)
- 그림 생성 코드: `src/build_portfolio_figures_v2.py` (계산 로직 재사용, cosmetic만 변경)

---

## [1] k=6 CI 해석 수정 (가장 중요)

- **문제**: 기존 본문/캡션은 k=6에서 IDF CI [0.22, 0.58]와 binary CI [-0.02, 0.34]의
  *개별* 신뢰구간만 보고 "CI 수준에서도 분리된다 / 재표집에도 견고한 차이"라고 서술했다.
  두 개별 CI는 0.22–0.34 구간에서 겹치므로 이 추론은 부적절하다.
- **수정**: 동일 부트스트랩 표본에서 계산한 **쌍체 차이**(ARI_IDF − ARI_binary)의 CI로 교체했다.
  기존 `bootstrap_expert()`는 매 resample마다 하나의 consensus를 만들어 IDF·binary ARI를 동시에
  계산하므로 두 ARI는 같은 표본 인덱스로 정렬된 쌍이다 → paired difference가 통계적으로 유효.
  - k=6: 쌍체 차이 **[0.06, 0.32]**, 0 제외 (1000회 중 99.4% 양수) → "비교적 견고" (정당화됨)
  - k=5: 쌍체 차이 **[-0.08, 0.20]**, 0 포함 → "경향은 있으나 확정 어려움"
  - k=4: 쌍체 차이 **[-0.08, -0.04]**, 0 제외(음수) → binary가 근소·견고 우위
    (점추정 0.52 vs 0.59와 일치하며, "상위 구조에서 IDF 효과 제한적"이라는 본 연구 해석과 정합)
- **일관성 점검**: 본문에서 "세분 단위(k≥5)" → "세분 단위, 특히 k=6"으로 통일.
  Fig.5 캡션의 "CI 수준에서도 분리" 문구 제거.

> 재현: seed=42, B=1000, `src/build_card_sorting_analysis.py`의 `bootstrap_expert()` 루프 순서로
> per-resample 쌍체 차이를 재집계.

## [2] k 선택 기준 문단 추가

- 방법론 §데이터와 방법에 `\subsection{k의 역할}` 신설.
- k=3(거시), k=4(전문가 consensus 주 비교), k=5·6(세분 민감도), k=7(binary 의약-보건 분리 보조)을
  **사전 선언**하여 "좋은 k만 골라 해석"으로 비치지 않도록 함.

## [3] 참고문헌 추가

- 표준 문헌 8종을 `thebibliography`로 추가(실존 문헌만):
  IDF(Spärck Jones 1972), cosine/TF-IDF(Manning et al. 2008), hierarchical(Everitt et al. 2011),
  k-means(Lloyd 1982), ARI(Hubert & Arabie 1985), card sorting(Spencer 2009),
  cluster stability/Jaccard(Hennig 2007), bootstrap(Efron 1979).
- citation은 각 방법이 **처음 등장하는 위치에만** 삽입.
- 권/호/페이지는 표준값으로 채우되, 제출 전 원문 대조용 `% TODO: 확인 필요` 주석을 남김.

## [4] 초록 개선

- 5문장 구조(문제 → 데이터·방법 → 결과 → 실무 의미 → 한계/주의)로 재작성.
- 핵심 메시지 명시: "권장과목 데이터는 학과 추천의 단독 기준은 아니지만, 전문가 상담에서 놓치기 쉬운
  준비과목 기반 대안과 과목 정합성 위험을 탐지하는 보조 신호로 활용될 수 있다."
- k=4 binary 반전은 초록에 끌어오지 않고 §내부 vs 전문가 비교 본문에서만 다룸(IDF 서사 집중).

## [5] 그림 가독성 개선 (6종, 멤버십 불변)

- `src/build_portfolio_figures_v2.py`가 기존 분석 모듈의 **계산 함수를 import**해 linkage/거리/데이터
  로딩을 그대로 재사용하고, plotting 파라미터(figsize·fontsize·rotation·annotation)만 변경.
- 재생성 후 군집 멤버십을 committed CSV와 대조: **3개 군집 그림 모두 원본과 완전 일치**
  (Fig.1 [2,2,4,17], Fig.2 [3,4,10], Fig.3 [2,3,7,13]).
- Fig.1: k=4 색 분리 + 군집명(STEM-보건/국어국문·디자인/경영·경제/사회·인문) + k=4 cut 선.
- Fig.2: 3색 분리 + 하위 군집명(의약-보건/정량·응용/공학-화학).
- Fig.3: consensus 경계선 강조(2pt) + 블록명(공학-자연(13) 라벨 정정).
- Fig.5: 제목 중립화("CI 분리" 문구 없음).
- Fig.6: 불일치 주석을 **Table III 대표 쌍**과 일치시킴(신소재공학-생명과학 Type 1,
  조선해양-자동차·국어국문-사학 Type 2; 좌표도 Table III 수치와 일치).

## [6] Type 1 / Type 2 실무 적용 강화

- §실무 적용에 2×2 사분면 표(`tab:quadrant`) 추가:
  알고리즘×전문가 일치/불일치 → 의미 → 상담 활용(우선 추천 / 교차 계열 대안 / 정합성 경고 / 후순위).

## [7] 영어 표현 정리

- 치환: top-level→상위 수준, boundary case→경계 사례, sub-clustering→하위 군집화,
  future work→후속 연구, knob→조절 모수, industry-specific…→지역 산업 맥락 기반 공학계열 경계 사례,
  profile→프로파일, feature→특징.
- 유지(표준 용어): cosine similarity, hierarchical clustering, card sorting, bootstrap, ARI, IDF,
  k-means, consensus, Jaccard.

## [8] 한계·후속 연구 정리

- §한계 및 후속 연구로 개편: 한계 4항목(표본 / 권장과목 해상도 / 전문가 패널 / 성과 검증)을
  `enumerate`로 번호화, 후속 연구 2항목(입결 Type 2 정량화 / anchor 준지도 확장)을 번호화.

---

## 검증 요약

- 정적 검증 통과: 미정의 `\ref`/`\cite` 0, 미사용 label 0, 환경·중괄호 균형, 표 열 수 정상.
- **컴파일 한계**: 로컬에 LaTeX 엔진(pdflatex/xelatex 등)이 없어 PDF 빌드는 수행하지 못함.
  Overleaf 업로드(또는 MiKTeX 설치) 시 컴파일 필요. 업로드 번들: `reports/final/v2_upload.zip`.

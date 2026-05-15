"""Create raw-data Excel templates with UTF-8 Korean text."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

GREEN = PatternFill("solid", fgColor="E2F0D9")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


DEPARTMENTS = [
    ("D01", "건축학과", "공학/예체능", 1, 1, "공학과 디자인/설계 경계"),
    ("D02", "국어국문학과", "인문", 0, 1, ""),
    ("D03", "심리학과", "사회/인문", 1, 1, "사회과학과 인문 경계"),
    ("D04", "기계공학과", "공학", 0, 1, ""),
    ("D05", "화학과", "자연", 1, 1, "화학공학/약학과 비교 중요"),
    ("D06", "산업공학과", "공학/경영", 1, 1, "공학과 경영/데이터 경계"),
    ("D07", "신소재공학과", "공학", 1, 1, "화학/물리 기반 공학"),
    ("D08", "조선해양공학과", "공학", 0, 1, "지역 산업 맥락"),
    ("D09", "의예과", "의약", 0, 1, ""),
    ("D10", "수학과", "자연", 1, 1, "통계/컴공/산공과 연결"),
    ("D11", "경영학과", "사회", 0, 1, ""),
    ("D12", "약학과", "의약/자연", 1, 1, "화학/생명 기반 의약"),
    ("D13", "사회학과", "사회", 0, 1, ""),
    ("D14", "경제학과", "사회", 1, 1, "경영/통계와 연결"),
    ("D15", "생명과학과", "자연", 1, 1, "약학/간호/식품영양과 연결"),
    ("D16", "미디어커뮤니케이션학과", "사회/인문", 1, 1, ""),
    ("D17", "화학공학과", "공학/자연", 1, 1, "화학과 비교 중요"),
    ("D18", "디자인학과", "예체능", 1, 1, "건축/미디어와 경계"),
    ("D19", "식품영양학과", "자연/보건", 1, 1, "생명/간호와 연결"),
    ("D20", "간호학과", "의약/보건", 1, 1, ""),
    ("D21", "전기전자공학과", "공학", 0, 1, ""),
    ("D22", "사학과", "인문", 0, 1, ""),
    ("D23", "응용통계학과", "자연/사회", 1, 1, "수학/경제/산공과 연결"),
    ("D24", "컴퓨터공학과", "공학", 1, 1, "수학/산공/전기전자와 연결"),
]


def style_sheet(ws, widths: dict[str, int], freeze: str = "A2") -> None:
    ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = GREEN
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            cell.border = BORDER
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    ws.row_dimensions[1].height = 34


def add_note_sheet(wb: Workbook, title: str, rows: list[tuple[str, str]]) -> None:
    ws = wb.create_sheet(title)
    ws.append(["Item", "Note"])
    for row in rows:
        ws.append(row)
    style_sheet(ws, {"A": 24, "B": 100})


def add_list_validation(ws, ranges_to_values: dict[str, str]) -> None:
    for cell_range, values in ranges_to_values.items():
        validation = DataValidation(type="list", formula1=f'"{values}"', allow_blank=True)
        ws.add_data_validation(validation)
        validation.add(cell_range)


def create_departments() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "departments"
    ws.append(
        [
            "department_id",
            "department_name_ko",
            "broad_category",
            "boundary_flag",
            "include_in_cardsort",
            "note",
        ]
    )
    for row in DEPARTMENTS:
        ws.append(row)
    style_sheet(ws, {"A": 14, "B": 24, "C": 18, "D": 13, "E": 18, "F": 44})
    add_note_sheet(
        wb,
        "guide",
        [
            ("Purpose", "24개 학과 기준표입니다. 이 목록을 기준으로 course vector, 입결 매칭, card sorting을 모두 맞춥니다."),
            ("Do not change IDs", "department_id는 분석 병합 키입니다. 학과를 추가/삭제하기 전에는 전체 설계를 먼저 확인하세요."),
        ],
    )
    wb.save(RAW_DIR / "departments_raw.xlsx")


def create_recommended_courses() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "recommended_courses"
    headers = [
        "department_id",
        "department_name_ko",
        "source_type",
        "source_name",
        "source_url_or_file",
        "course_name_original",
        "course_name_standardized",
        "subject_group",
        "recommendation_level_original",
        "assigned_weight",
        "coding_rule",
        "coding_note",
        "source_access_date",
    ]
    ws.append(headers)
    source_rows = [
        (
            "official_doc",
            "대교협 권장 이수과목",
            "파일명 또는 URL",
            "대교협 원문에서 권장/핵심 과목 확인",
        ),
        (
            "official_api",
            "CareerNet Major OpenAPI",
            "https://www.career.go.kr/cnet/front/openapi/openApiMajorCenter.do",
            "커리어넷 관련 고교 교과목 확인",
        ),
    ]
    for department_id, department_name, *_ in DEPARTMENTS:
        for source_type, source_name, source_url, memo in source_rows:
            ws.append(
                [
                    department_id,
                    department_name,
                    source_type,
                    source_name,
                    source_url,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    memo,
                    "2026-05-15",
                ]
            )
    for _ in range(100):
        ws.append([""] * len(headers))
    style_sheet(
        ws,
        {
            "A": 14,
            "B": 24,
            "C": 16,
            "D": 24,
            "E": 42,
            "F": 28,
            "G": 24,
            "H": 14,
            "I": 24,
            "J": 14,
            "K": 20,
            "L": 42,
            "M": 16,
        },
    )
    add_list_validation(
        ws,
        {
            "C2:C250": "official_doc,official_api,university_page,education_office,manual_note",
            "H2:H250": "수학,과학,사회,정보,국어,영어,예체능,생활교양,기타",
            "J2:J250": "1,0.5,0",
            "K2:K250": "핵심 권장=1.0,관련/보조=0.5,언급 없음=0",
        },
    )
    add_note_sheet(
        wb,
        "guide",
        [
            ("Purpose", "ML course vector의 핵심 raw data입니다. 원문 표현과 코딩 메모를 반드시 남겨야 합니다."),
            ("Weight 1.0", "대교협 등에서 핵심/권장 이수과목으로 명확히 제시된 경우."),
            ("Weight 0.5", "커리어넷 관련 고교 교과목 또는 보조/관련 과목으로 제시된 경우."),
            ("Weight 0.0", "언급 없음. 보통 raw에는 0 행을 만들지 않고 matrix 생성 단계에서 자동으로 0 처리합니다."),
            ("Source priority", "1순위 대교협, 2순위 커리어넷, 3순위 교육청/기타 공개자료."),
        ],
    )
    wb.save(RAW_DIR / "recommended_courses_raw.xlsx")


def create_admission_scores() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "admission_scores"
    headers = [
        "university",
        "admission_year",
        "admission_type",
        "unit_name_original",
        "department_id",
        "department_name_standardized",
        "score_value",
        "score_scale",
        "score_type",
        "source_name",
        "source_url_or_file",
        "matching_confidence",
        "matching_note",
        "source_access_date",
    ]
    ws.append(headers)
    universities = [
        "부산대",
        "경북대",
        "전남대",
        "충남대",
        "충북대",
        "전북대",
        "강원대",
        "경상국립대",
        "울산대",
        "부경대",
        "동아대",
    ]
    for university in universities:
        for department_id, department_name, *_ in DEPARTMENTS:
            ws.append(
                [
                    university,
                    2025,
                    "학생부종합",
                    "",
                    department_id,
                    department_name,
                    "",
                    "내신등급",
                    "종합 평균",
                    "대학어디가 또는 입학처",
                    "",
                    "",
                    "모집단위명 확인 후 high/medium/low 기록",
                    "2026-05-15",
                ]
            )
    for _ in range(60):
        ws.append([""] * len(headers))
    style_sheet(
        ws,
        {
            "A": 16,
            "B": 14,
            "C": 18,
            "D": 28,
            "E": 14,
            "F": 24,
            "G": 12,
            "H": 14,
            "I": 20,
            "J": 24,
            "K": 42,
            "L": 18,
            "M": 42,
            "N": 16,
        },
    )
    add_list_validation(
        ws,
        {
            "A2:A350": "부산대,경북대,전남대,충남대,충북대,전북대,강원대,경상국립대,울산대,부경대,동아대",
            "C2:C350": "학생부종합,학생부교과,지역인재,기타",
            "H2:H350": "내신등급,백분위,환산점수,기타",
            "I2:I350": "종합 70% cut,종합 평균,교과 70% cut,교과 평균,50% cut,기타",
            "L2:L350": "high,medium,low",
        },
    )
    add_note_sheet(
        wb,
        "guide",
        [
            ("Purpose", "실무 상담 가능성 해석용 성적대 참고값입니다. clustering feature로 쓰지 않습니다."),
            ("Primary target", "2025학년도 수시 학생부종합 최종등록자 70% cut 또는 평균."),
            ("Fallback order", "1 종합 70% cut, 2 종합 평균, 3 교과 70% cut, 4 교과 평균."),
            ("Interpretation", "학생부종합 내신 결과는 정량 합격선이 아니라 지원 성적대 참고값으로만 해석합니다."),
        ],
    )
    wb.save(RAW_DIR / "admission_scores_raw.xlsx")


def create_source_register() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "sources"
    headers = [
        "source_id",
        "source_type",
        "source_name",
        "source_url_or_file",
        "owner_or_publisher",
        "collection_method",
        "access_date",
        "license_or_terms_note",
        "used_for",
        "reliability_note",
    ]
    ws.append(headers)
    ws.append(
        [
            "S001",
            "official_api",
            "CareerNet Major OpenAPI",
            "https://www.career.go.kr/cnet/front/openapi/openApiMajorCenter.do",
            "커리어넷",
            "api",
            "2026-05-15",
            "",
            "course subjects and descriptions",
            "official source",
        ]
    )
    ws.append(
        [
            "S002",
            "official_portal",
            "대입정보포털 어디가",
            "https://www.adiga.kr/",
            "한국대학교육협의회",
            "manual",
            "2026-05-15",
            "",
            "admission score reference",
            "official portal; standards differ by university",
        ]
    )
    for _ in range(100):
        ws.append([""] * len(headers))
    style_sheet(
        ws,
        {
            "A": 12,
            "B": 18,
            "C": 28,
            "D": 48,
            "E": 24,
            "F": 18,
            "G": 16,
            "H": 34,
            "I": 28,
            "J": 42,
        },
    )
    add_note_sheet(
        wb,
        "guide",
        [
            ("Purpose", "사용한 모든 출처를 기록합니다. 보고서 reference와 데이터 신뢰도 설명에 사용합니다."),
            ("Rule", "웹페이지, PDF, 엑셀, 내부자료 모두 하나씩 기록하세요."),
        ],
    )
    wb.save(RAW_DIR / "raw_source_register.xlsx")


def create_collection_checklist() -> None:
    wb = Workbook()

    ws = wb.active
    ws.title = "course_collection_status"
    headers = [
        "department_id",
        "department_name_ko",
        "대교협_확인",
        "커리어넷_확인",
        "과목명_표준화",
        "가중치_검토",
        "메모",
    ]
    ws.append(headers)
    for department_id, department_name, *_ in DEPARTMENTS:
        ws.append([department_id, department_name, "", "", "", "", ""])
    style_sheet(ws, {"A": 14, "B": 24, "C": 14, "D": 14, "E": 16, "F": 14, "G": 44})
    add_list_validation(
        ws,
        {
            "C2:F30": "미수집,수집중,완료,해당없음",
        },
    )

    ws = wb.create_sheet("admission_collection_status")
    headers = [
        "university",
        "department_id",
        "department_name_ko",
        "모집단위_존재여부",
        "종합_평균_수집",
        "종합_70cut_수집",
        "대체자료_필요",
        "메모",
    ]
    ws.append(headers)
    universities = [
        "부산대",
        "경북대",
        "전남대",
        "충남대",
        "충북대",
        "전북대",
        "강원대",
        "경상국립대",
        "울산대",
        "부경대",
        "동아대",
    ]
    for university in universities:
        for department_id, department_name, *_ in DEPARTMENTS:
            ws.append([university, department_id, department_name, "", "", "", "", ""])
    style_sheet(
        ws,
        {"A": 16, "B": 14, "C": 24, "D": 18, "E": 16, "F": 16, "G": 16, "H": 44},
    )
    add_list_validation(
        ws,
        {
            "D2:G300": "미확인,있음,없음,완료,해당없음,대체필요",
        },
    )

    add_note_sheet(
        wb,
        "guide",
        [
            ("course_collection_status", "24개 학과별 대교협/커리어넷 과목 수집 진행상황을 체크합니다."),
            ("admission_collection_status", "11개 대학 x 24개 학과 = 264개 조합의 입결 수집 진행상황을 체크합니다."),
            ("모집단위 없음", "해당 대학에 정확히 대응되는 모집단위가 없으면 '없음'으로 두고 admission_scores_raw에는 행을 남기되 score_value를 비워둘 수 있습니다."),
        ],
    )
    wb.save(RAW_DIR / "collection_checklist.xlsx")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "card_sorting_responses").mkdir(exist_ok=True)
    create_departments()
    create_recommended_courses()
    create_admission_scores()
    create_source_register()
    create_collection_checklist()
    print("Raw templates recreated:")
    for path in sorted(RAW_DIR.glob("*.xlsx")):
        print(path)


if __name__ == "__main__":
    main()

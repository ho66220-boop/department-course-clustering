from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
GUIDE = BASE / "학과 과목 선택 가이드.xlsx"
D25_NAME = "자동차공학과"


def normalize_course_name(value: str) -> str:
    course = str(value).strip().replace("\n", " ")
    course = re.sub(r"\s+", " ", course).strip(" .;·")
    course = re.sub(r"\s*등$", "", course).strip()
    replacements = {
        "미적분 Ⅰ": "미적분Ⅰ",
        "미적분 I": "미적분Ⅰ",
        "미적분Ⅰ": "미적분Ⅰ",
        "미적분 Ⅱ": "미적분Ⅱ",
        "미적분 II": "미적분Ⅱ",
        "미적분Ⅱ": "미적분Ⅱ",
        "융합 과학 탐구": "융합과학 탐구",
        "창의 공학 설계": "창의공학 설계",
    }
    return replacements.get(course, course)


def split_courses(value: object) -> list[str]:
    if pd.isna(value):
        return []
    parts = re.split(r"[,，]", str(value).replace("\n", ","))
    return [course for course in (normalize_course_name(part) for part in parts) if course and course != "등"]


def sync_departments_raw() -> None:
    path = RAW / "departments_raw.xlsx"
    departments = pd.read_excel(path, sheet_name="departments")
    departments = departments[departments["department_id"].astype(str) != "D25"].copy()
    departments = pd.concat(
        [
            departments,
            pd.DataFrame(
                [
                    {
                        "department_id": "D25",
                        "department_name_ko": D25_NAME,
                        "broad_category": "산업특화공학",
                        "boundary_flag": 1,
                        "include_in_cardsort": 1,
                        "note": "울산 지역 산업 맥락을 반영한 applied engineering boundary case",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    departments.to_excel(path, sheet_name="departments", index=False)


def d25_course_rows() -> list[dict[str, object]]:
    guide = pd.read_excel(GUIDE)
    guide["학과명"] = guide["학과명"].replace({"자동차학과": D25_NAME})
    record = guide.loc[guide["학과명"].eq(D25_NAME)].iloc[0]
    selection_columns = {
        "일반선택": "general_elective",
        "진로선택": "career_elective",
        "융합선택": "convergence_elective",
    }
    rows = []
    for source_column, source_type in selection_columns.items():
        for course in split_courses(record[source_column]):
            rows.append(
                {
                    "department_id": "D25",
                    "department_name_ko": D25_NAME,
                    "source_type": "subject_guide",
                    "source_name": "학과 과목 선택 가이드",
                    "source_url_or_file": GUIDE.name,
                    "course_name_original": course,
                    "course_name_standardized": course,
                    "subject_group": source_type,
                    "recommendation_level_original": "listed_subject",
                    "assigned_weight": 1.0,
                    "coding_rule": "subject guide binary coding: listed=1, not listed=0",
                    "coding_note": "Added for 25-department current scope; alias 자동차학과 -> 자동차공학과",
                    "source_access_date": "2026-05-25",
                }
            )
    return rows


def sync_recommended_courses_raw(rows: list[dict[str, object]]) -> None:
    path = RAW / "recommended_courses_raw.xlsx"
    courses = pd.read_excel(path, sheet_name="recommended_courses")
    courses = courses[courses["department_id"].astype(str) != "D25"].copy()
    courses = pd.concat([courses, pd.DataFrame(rows)], ignore_index=True)
    courses.to_excel(path, sheet_name="recommended_courses", index=False)


def sync_collection_checklist(d25_rows: int) -> list[str]:
    path = RAW / "collection_checklist.xlsx"
    course_status = pd.read_excel(path, sheet_name="course_collection_status")
    admission_status = pd.read_excel(path, sheet_name="admission_collection_status")

    course_status = course_status[course_status["department_id"].astype(str) != "D25"].copy()
    course_status = pd.concat(
        [
            course_status,
            pd.DataFrame(
                [
                    {
                        "department_id": "D25",
                        "department_name_ko": D25_NAME,
                        "대교협_확인": "가이드 반영",
                        "커리어넷_확인": "미수집",
                        "과목명_표준화": "완료",
                        "가중치_검토": "binary coding",
                        "메모": f"학과 과목 선택 가이드 기반 rows={d25_rows}",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    universities = list(pd.unique(admission_status["university"].dropna()))
    admission_status = admission_status[admission_status["department_id"].astype(str) != "D25"].copy()
    admission_status = pd.concat(
        [
            admission_status,
            pd.DataFrame(
                [
                    {
                        "university": university,
                        "department_id": "D25",
                        "department_name_ko": D25_NAME,
                        "모집단위_존재여부": "미확인/없음",
                        "종합_평균_수집": "미수집",
                        "종합_70cut_수집": "미수집",
                        "대체자료_필요": "필요",
                        "메모": "25개 학과 scope 추가 행; admission feasibility는 future work",
                    }
                    for university in universities
                ]
            ),
        ],
        ignore_index=True,
    )

    guide = pd.DataFrame(
        {
            "Item": ["course_collection_status", "admission_collection_status", "모집단위 없음"],
            "Note": [
                "25개 학과별 과목 수집 진행상황을 체크합니다.",
                f"{len(universities)}개 대학 x 25개 학과 = {len(universities) * 25}개 조합의 입결 수집 진행상황을 체크합니다.",
                "해당 대학에 정확히 대응되는 모집단위가 없으면 '없음'으로 두고 admission_scores_raw에는 행을 남기되 score_value를 비워둘 수 있습니다.",
            ],
        }
    )
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        course_status.to_excel(writer, sheet_name="course_collection_status", index=False)
        admission_status.to_excel(writer, sheet_name="admission_collection_status", index=False)
        guide.to_excel(writer, sheet_name="guide", index=False)
    return universities


def sync_admission_scores_raw(universities: list[str]) -> None:
    path = RAW / "admission_scores_raw.xlsx"
    scores = pd.read_excel(path, sheet_name="admission_scores")
    scores = scores[scores["department_id"].astype(str) != "D25"].copy()
    placeholders = pd.DataFrame(
        [
            {
                "university": university,
                "admission_year": 2025,
                "admission_type": "future_work_placeholder",
                "unit_name_original": pd.NA,
                "department_id": "D25",
                "department_name_standardized": D25_NAME,
                "score_value": pd.NA,
                "score_scale": "내신등급",
                "score_type": "미수집",
                "source_name": "placeholder for 25-department scope",
                "source_url_or_file": pd.NA,
                "matching_confidence": "none",
                "matching_note": "Admission score feasibility is future work for D25 자동차공학과.",
                "source_access_date": "2026-05-25",
            }
            for university in universities
        ]
    )
    scores = pd.concat([scores, placeholders], ignore_index=True)
    scores.to_excel(path, sheet_name="admission_scores", index=False)


def main() -> None:
    sync_departments_raw()
    rows = d25_course_rows()
    sync_recommended_courses_raw(rows)
    universities = sync_collection_checklist(len(rows))
    sync_admission_scores_raw(universities)
    print(f"d25_course_rows={len(rows)}")
    print(f"universities={len(universities)}")


if __name__ == "__main__":
    main()

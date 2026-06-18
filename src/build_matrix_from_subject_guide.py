"""Build binary department-course matrices from the subject selection guide.

Input workbook columns:
- 학과명
- 일반선택
- 진로선택
- 융합선택

The output matrix is binary:
- 1 = the course is listed for the department in the guide
- 0 = the course is not listed for the department
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
INPUT_GUIDE = BASE / "학과 과목 선택 가이드.xlsx"
PROCESSED = BASE / "data" / "processed"

SELECTION_COLUMNS = {
    "일반선택": "general_elective",
    "진로선택": "career_elective",
    "융합선택": "convergence_elective",
}

DEPARTMENT_META = {
    "건축학과": ("D01", "engineering_design_boundary", "Boundary case between engineering and design/planning"),
    "국어국문학과": ("D02", "humanities", "Humanities reference field with language/literature course profile"),
    "심리학과": ("D03", "social_science_humanities_boundary", "Boundary case between social science and humanities"),
    "기계공학과": ("D04", "engineering", "Math/physics-oriented engineering reference field"),
    "화학과": ("D05", "natural_science", "Chemistry-centered natural science field"),
    "산업공학과": ("D06", "engineering_management_boundary", "Boundary case linking engineering data and management"),
    "신소재공학과": ("D07", "engineering", "Chemistry/materials-related engineering field"),
    "조선해양공학과": ("D08", "industry_specific_engineering_boundary", "Ulsan-related applied engineering boundary case"),
    "의예과": ("D09", "medical_health", "High-stakes biology/chemistry health-related field"),
    "수학과": ("D10", "natural_science_quantitative", "Quantitative field linked to statistics/computing/engineering"),
    "경영학과": ("D11", "social_science", "Social science reference field relevant to counseling comparisons"),
    "약학과": ("D12", "medical_health_natural_science", "Biology/chemistry health-related boundary field"),
    "사회학과": ("D13", "social_science", "Social science reference field with counseling relevance"),
    "경제학과": ("D14", "social_science_quantitative", "Social science field linked to mathematics/statistics"),
    "생명과학과": ("D15", "natural_science", "Biology-centered natural science field linked to health fields"),
    "미디어커뮤니케이션학과": ("D16", "social_science_humanities_boundary", "Boundary case between humanities social science and media fields"),
    "화학공학과": ("D17", "engineering_natural_science", "Chemistry/materials-related engineering field"),
    "디자인학과": ("D18", "arts_design", "Boundary case linked to architecture and media fields"),
    "식품영양학과": ("D19", "natural_science_health", "Biology/health-related field linked to life science and nursing"),
    "간호학과": ("D20", "medical_health", "Biology/health-related counseling-relevant field"),
    "전기전자공학과": ("D21", "engineering", "Math/physics/information-oriented engineering field"),
    "사학과": ("D22", "humanities", "Humanities reference field with social/historical course profile"),
    "응용통계학과": ("D23", "natural_science_social_science_boundary", "Quantitative field linked to mathematics economics and data analysis"),
    "컴퓨터공학과": ("D24", "engineering_information", "Information/math-related engineering field"),
    "자동차공학과": ("D25", "industry_specific_engineering_boundary", "Ulsan-related applied engineering boundary case"),
}

DEPARTMENT_ALIASES = {
    "신문방송학과": "미디어커뮤니케이션학과",
    "자동차학과": "자동차공학과",
}

COURSE_REPLACEMENTS = {
    "미적분 Ⅰ": "미적분Ⅰ",
    "미적분 I": "미적분Ⅰ",
    "미적분Ⅰ": "미적분Ⅰ",
    "미적분 Ⅱ": "미적분Ⅱ",
    "미적분 II": "미적분Ⅱ",
    "미적분Ⅱ": "미적분Ⅱ",
    "융합 과학 탐구": "융합과학 탐구",
    "창의 공학 설계": "창의공학 설계",
    "정보등": "정보",
    "인묵학과 윤리": "인문학과 윤리",
    # Whitespace variants of the same official course name (unify to the spaced form)
    "영어독해와 작문": "영어 독해와 작문",
    "인공지능기초": "인공지능 기초",
    "한국지리탐구": "한국지리 탐구",
}


def normalize_course_name(value: str) -> str:
    course = str(value).strip()
    course = course.replace("\n", " ")
    course = re.sub(r"\s+", " ", course)
    course = course.strip(" .;·")
    course = re.sub(r"\s*등$", "", course).strip()
    return COURSE_REPLACEMENTS.get(course, course)


def split_courses(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).replace("\n", ",")
    parts = re.split(r"[,，]", text)
    courses = [normalize_course_name(part) for part in parts]
    return [course for course in courses if course and course != "등"]


def load_guide() -> pd.DataFrame:
    if not INPUT_GUIDE.exists():
        raise FileNotFoundError(f"Subject guide not found: {INPUT_GUIDE}")

    guide = pd.read_excel(INPUT_GUIDE, sheet_name=0)
    required = {"학과명", *SELECTION_COLUMNS.keys()}
    missing = required - set(guide.columns)
    if missing:
        raise ValueError(f"Missing required columns in subject guide: {sorted(missing)}")

    guide["학과명"] = guide["학과명"].astype(str).str.strip().replace(DEPARTMENT_ALIASES)
    unknown = sorted(set(guide["학과명"]) - set(DEPARTMENT_META))
    if unknown:
        raise ValueError(f"Departments missing from metadata mapping: {unknown}")

    if len(guide) != 25:
        raise ValueError(f"Expected 25 departments in guide, found {len(guide)}.")
    if guide["학과명"].duplicated().any():
        duplicated = guide.loc[guide["학과명"].duplicated(), "학과명"].tolist()
        raise ValueError(f"Duplicated departments in guide: {duplicated}")

    return guide


def build_evidence(guide: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for record in guide.to_dict("records"):
        department_name = record["학과명"]
        department_id, broad_field, selected_reason = DEPARTMENT_META[department_name]

        for source_column, selection_type in SELECTION_COLUMNS.items():
            for course in split_courses(record[source_column]):
                rows.append(
                    {
                        "department_id": department_id,
                        "department_name_ko": department_name,
                        "broad_field": broad_field,
                        "selected_reason": selected_reason,
                        "selection_type": selection_type,
                        "course_name_original": course,
                        "course_name_standardized": course,
                        "binary_value": 1,
                        "source_name": INPUT_GUIDE.name,
                    }
                )

    evidence = pd.DataFrame(rows).drop_duplicates(
        subset=["department_id", "course_name_standardized", "selection_type"]
    )
    evidence = evidence.sort_values(["department_id", "selection_type", "course_name_standardized"])
    return evidence


def build_matrix(evidence: pd.DataFrame) -> pd.DataFrame:
    ids = []
    for department_name, (department_id, broad_field, selected_reason) in DEPARTMENT_META.items():
        ids.append(
            {
                "department_id": department_id,
                "department_name_ko": department_name,
                "broad_field": broad_field,
                "selected_reason": selected_reason,
            }
        )
    metadata = pd.DataFrame(ids).sort_values("department_id")

    matrix = evidence.pivot_table(
        index="department_id",
        columns="course_name_standardized",
        values="binary_value",
        aggfunc="max",
        fill_value=0,
    )
    matrix = matrix.reindex(metadata["department_id"]).fillna(0).astype(int)
    matrix = matrix.reindex(sorted(matrix.columns), axis=1)

    return metadata.merge(matrix.reset_index(), on="department_id", how="left").fillna(0)


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    guide = load_guide()
    evidence = build_evidence(guide)
    matrix = build_matrix(evidence)

    evidence.to_csv(PROCESSED / "course_coding_evidence.csv", index=False, encoding="utf-8-sig")
    matrix.to_csv(PROCESSED / "department_course_matrix_binary.csv", index=False, encoding="utf-8-sig")
    matrix.to_csv(PROCESSED / "department_course_matrix_refined_binary.csv", index=False, encoding="utf-8-sig")

    print(f"input={INPUT_GUIDE}")
    print(f"departments={len(matrix)}")
    print(f"course_features={len([c for c in matrix.columns if c not in {'department_id', 'department_name_ko', 'broad_field', 'selected_reason'}])}")
    print(f"evidence_rows={len(evidence)}")
    print("outputs=data/processed/course_coding_evidence.csv, department_course_matrix_binary.csv, department_course_matrix_refined_binary.csv")


if __name__ == "__main__":
    main()

"""Collect CareerNet major information for the 25 project departments.

This script uses the CareerNet Major OpenAPI. Set CAREERNET_API_KEY before
running. The output should be treated as raw data and saved under data/raw/.

Example:
    $env:CAREERNET_API_KEY="..."
    python src/collect_careernet_majors.py --out data/raw/careernet_major_raw.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


DEPARTMENTS = [
    "건축학과",
    "국어국문학과",
    "심리학과",
    "기계공학과",
    "화학과",
    "산업공학과",
    "신소재공학과",
    "조선해양공학과",
    "의예과",
    "수학과",
    "경영학과",
    "약학과",
    "사회학과",
    "경제학과",
    "생명과학과",
    "미디어커뮤니케이션학과",
    "화학공학과",
    "디자인학과",
    "식품영양학과",
    "간호학과",
    "전기전자공학과",
    "사학과",
    "응용통계학과",
    "컴퓨터공학과",
    "자동차공학과",
]

BASE_URL = "https://www.career.go.kr/cnet/openapi/getOpenApi"


def fetch_json(params: dict[str, str]) -> dict:
    url = BASE_URL + "?" + urlencode(params)
    with urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def find_major(api_key: str, keyword: str) -> dict:
    params = {
        "apiKey": api_key,
        "svcType": "api",
        "svcCode": "MAJOR",
        "contentType": "json",
        "gubun": "univ_list",
        "univSe": "univ",
        "thisPage": "1",
        "perPage": "20",
        "searchTitle": keyword,
    }
    return fetch_json(params)


def fetch_major_detail(api_key: str, major_seq: str) -> dict:
    params = {
        "apiKey": api_key,
        "svcType": "api",
        "svcCode": "MAJOR_VIEW",
        "contentType": "json",
        "gubun": "univ_list",
        "majorSeq": major_seq,
    }
    return fetch_json(params)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/raw/careernet_major_raw.json")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    api_key = os.environ.get("CAREERNET_API_KEY")
    if not api_key:
        raise SystemExit("Set CAREERNET_API_KEY before running this script.")

    rows = []
    for department in DEPARTMENTS:
        search_result = find_major(api_key, department)
        contents = search_result.get("dataSearch", {}).get("content", [])
        if isinstance(contents, dict):
            contents = [contents]

        best = contents[0] if contents else {}
        major_seq = str(best.get("majorSeq", "")) if best else ""
        detail = fetch_major_detail(api_key, major_seq) if major_seq else {}

        rows.append(
            {
                "query_department": department,
                "matched_major_seq": major_seq,
                "matched_major_name": best.get("mClass"),
                "matched_lclass": best.get("lClass"),
                "search_result": search_result,
                "detail": detail,
            }
        )
        time.sleep(args.sleep)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

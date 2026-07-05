#!/usr/bin/env python3
"""Create one demo resume and process it through the public API."""

import argparse
import json
import sys
import time
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


def request_json(method: str, url: str, payload: Optional[dict] = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body else {},
    )
    with urlopen(request, timeout=180) as response:
        return json.load(response)


def wait_for_api(base_url: str) -> None:
    for _ in range(30):
        try:
            request_json("GET", f"{base_url}/health")
            return
        except (URLError, HTTPError, TimeoutError):
            time.sleep(1)
    raise RuntimeError(f"API가 준비되지 않았습니다: {base_url}")


def main() -> int:
    parser = argparse.ArgumentParser(description="KHU:DArchive 데모 데이터를 생성합니다.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--user-id", default=DEFAULT_USER_ID)
    parser.add_argument("--force", action="store_true", help="기존 데이터가 있어도 추가합니다.")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    try:
        wait_for_api(base_url)
        existing = request_json(
            "GET", f"{base_url}/api/experiences?user_id={args.user_id}"
        )["data"]["experiences"]
        if existing and not args.force:
            print(f"이미 경험 데이터가 {len(existing)}개 있어 생성을 건너뜁니다. (--force로 추가 가능)")
            return 0

        created = request_json(
            "POST",
            f"{base_url}/api/documents/text",
            {
                "user_id": args.user_id,
                "source_type": "resume",
                "title": "KHU:DArchive 데모 이력서",
                "text": (
                    "FastAPI와 PostgreSQL로 경험 추천 API를 개발했습니다. "
                    "쿼리와 검색 파이프라인을 개선해 응답 시간을 1.8초에서 0.9초로 줄였고, "
                    "프론트엔드 담당자와 OpenAPI 계약을 맞춰 통합 오류를 해결했습니다."
                ),
                "metadata": {"demo": True},
            },
        )
        document_id = created["data"]["document_id"]
        result = request_json("POST", f"{base_url}/api/documents/{document_id}/process")
        print(
            f"데모 데이터 생성 완료: document_id={document_id}, "
            f"experiences={result['data']['experience_count']}"
        )
        return 0
    except (KeyError, HTTPError, URLError, RuntimeError, TimeoutError) as exc:
        print(f"데모 데이터 생성 실패: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

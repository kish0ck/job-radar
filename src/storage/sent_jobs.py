"""이미 알림 보낸 공고 ID를 기록해서 중복 알림을 막는 저장소.

data/sent_jobs.json에 {공고ID: 발송일자} 형태로 기록한다.
"""

import datetime
import json
import pathlib

DEFAULT_STORE_PATH = pathlib.Path(__file__).resolve().parents[2] / "data" / "sent_jobs.json"


def load_sent_ids(path: pathlib.Path = DEFAULT_STORE_PATH) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_sent_ids(sent_ids: dict, path: pathlib.Path = DEFAULT_STORE_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sent_ids, f, ensure_ascii=False, indent=2, sort_keys=True)


def filter_new_jobs(jobs: list[dict], sent_ids: dict) -> list[dict]:
    return [job for job in jobs if job["id"] not in sent_ids]


def mark_as_sent(jobs: list[dict], sent_ids: dict) -> dict:
    today = datetime.date.today().isoformat()
    updated = dict(sent_ids)
    for job in jobs:
        updated[job["id"]] = today
    return updated


if __name__ == "__main__":
    sample_jobs = [
        {"id": "hyundai-2026-156", "title": "예시 공고 1"},
        {"id": "hyundai-2026-173", "title": "예시 공고 2"},
    ]

    already_sent = {"hyundai-2026-156": "2026-08-14"}
    new_jobs = filter_new_jobs(sample_jobs, already_sent)
    print(f"전체 {len(sample_jobs)}건 중 신규 {len(new_jobs)}건: {[j['id'] for j in new_jobs]}")
    assert [j["id"] for j in new_jobs] == ["hyundai-2026-173"], "중복 제거 실패"
    print("중복 방지 로직 테스트 통과")

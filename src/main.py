"""job-radar 파이프라인 진입점: 수집 -> 필터링 -> 중복 제거 -> 알림 발송 -> 발송 기록 -> 대시보드."""

import datetime

from collectors import hyundai, samsung, saramin, shinsegae
from dashboard.generate import generate_dashboard
from filters.keyword_filter import filter_jobs, load_keywords
from notifiers.email_notifier import send_notification
from storage.sent_jobs import filter_new_jobs, load_sent_ids, mark_as_sent, save_sent_ids


def _collect(name: str, fetch_fn, run_log: dict) -> list[dict]:
    """수집원 하나가 실패해도 전체 파이프라인은 계속 진행되도록 개별적으로 감싼다."""
    try:
        jobs = fetch_fn()
        run_log["sources"][name] = {"count": len(jobs), "error": None}
        return jobs
    except Exception as exc:
        print(f"[수집 실패] {name}: {exc}")
        run_log["sources"][name] = {"count": 0, "error": str(exc)}
        return []


def run() -> None:
    keywords_config = load_keywords()
    run_log = {"timestamp": datetime.datetime.now().isoformat(timespec="seconds"), "sources": {}}

    saramin_jobs = _collect(
        "saramin", lambda: saramin.fetch_jobs(keywords=keywords_config["include_keywords"]), run_log
    )
    hyundai_jobs = _collect("hyundai", hyundai.fetch_jobs, run_log)
    samsung_jobs = _collect("samsung", samsung.fetch_jobs, run_log)
    shinsegae_jobs = _collect("shinsegae", shinsegae.fetch_jobs, run_log)

    all_jobs = saramin_jobs + hyundai_jobs + samsung_jobs + shinsegae_jobs
    print(f"[수집] {run_log['sources']}")

    matched_jobs = filter_jobs(all_jobs, keywords_config)
    print(f"[필터링] {len(all_jobs)}건 중 {len(matched_jobs)}건 매칭")

    sent_ids = load_sent_ids()
    new_jobs = filter_new_jobs(matched_jobs, sent_ids)
    print(f"[중복 제거] 신규 {len(new_jobs)}건")

    send_notification(new_jobs)
    print("[알림] 발송 완료" if new_jobs else "[알림] 신규 공고 없음 - 발송 생략")

    updated_sent_ids = mark_as_sent(new_jobs, sent_ids)
    save_sent_ids(updated_sent_ids)
    print("[기록] sent_jobs.json 갱신 완료")

    generate_dashboard(new_jobs, updated_sent_ids, run_log)
    print("[대시보드] docs/index.html 갱신 완료")


if __name__ == "__main__":
    run()

"""job-radar 파이프라인 진입점: 수집 -> 필터링 -> 중복 제거 -> 알림 발송 -> 발송 기록."""

from collectors import hyundai, samsung, saramin
from filters.keyword_filter import filter_jobs, load_keywords
from notifiers.email_notifier import send_notification
from storage.sent_jobs import filter_new_jobs, load_sent_ids, mark_as_sent, save_sent_ids


def run() -> None:
    keywords_config = load_keywords()

    saramin_jobs = saramin.fetch_jobs(keywords=keywords_config["include_keywords"])
    hyundai_jobs = hyundai.fetch_jobs()
    samsung_jobs = samsung.fetch_jobs()
    all_jobs = saramin_jobs + hyundai_jobs + samsung_jobs
    print(
        f"[수집] 사람인 {len(saramin_jobs)}건, 현대차 {len(hyundai_jobs)}건, "
        f"삼성 {len(samsung_jobs)}건 (총 {len(all_jobs)}건)"
    )

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


if __name__ == "__main__":
    run()

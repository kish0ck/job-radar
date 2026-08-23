"""매칭된 신규 공고를 이메일로 발송하는 모듈."""

from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from notifiers.email_template import render_html

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_notification(
    jobs: list[dict],
    run_log: dict | None = None,
    sent_ids: dict | None = None,
) -> None:
    """신규 매칭 공고가 있을 때만 이메일을 보낸다. 0건이면 발송하지 않는다."""
    if not jobs:
        return

    sender = os.environ["EMAIL_ADDRESS"]
    app_password = os.environ["EMAIL_APP_PASSWORD"]
    receiver = os.environ["RECEIVER_EMAIL"]

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[job-radar] 오늘의 추천 공고 {len(jobs)}건"
    message["From"] = sender
    message["To"] = receiver
    # 텍스트 파트를 먼저 붙여야 이메일 클라이언트가 HTML을 우선 렌더링한다 (MIME 규칙상 마지막 파트 우선)
    message.attach(MIMEText(_build_text_body(jobs), "plain"))
    message.attach(MIMEText(render_html(jobs, run_log, sent_ids), "html"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender, app_password)
        server.sendmail(sender, [receiver], message.as_string())


def _build_text_body(jobs: list[dict]) -> str:
    lines = []
    for job in jobs:
        lines.append(f"- [{job['company']}] {job['title']}")
        lines.append(f"  {job['url']}")
    return "\n".join(lines)


if __name__ == "__main__":
    test_jobs = [
        {
            "id": "test-1",
            "title": "job-radar 테스트 발송입니다",
            "company": "job-radar",
            "url": "https://github.com/",
        }
    ]
    test_run_log = {
        "sources": {
            "saramin": {"count": 5, "error": None},
            "hyundai": {"count": 57, "error": None},
            "samsung": {"count": 6, "error": None},
            "shinsegae": {"count": 11, "error": None},
        }
    }
    test_sent_ids = {
        "test-1": {
            "sent_at": "2026-08-16",
            "title": "job-radar 테스트 발송입니다",
            "company": "job-radar",
            "url": "https://github.com/",
        },
        "test-2": {
            "sent_at": "2026-08-15",
            "title": "과거에 보냈던 공고 예시",
            "company": "예시기업",
            "url": "https://github.com/",
        },
    }
    send_notification(test_jobs, test_run_log, test_sent_ids)
    print("발송 완료 — 받은편지함을 확인해주세요.")

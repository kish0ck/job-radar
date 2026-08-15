"""매칭된 신규 공고를 이메일로 발송하는 모듈."""

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_notification(jobs: list[dict]) -> None:
    """신규 매칭 공고가 있을 때만 이메일을 보낸다. 0건이면 발송하지 않는다."""
    if not jobs:
        return

    sender = os.environ["EMAIL_ADDRESS"]
    app_password = os.environ["EMAIL_APP_PASSWORD"]
    receiver = os.environ["RECEIVER_EMAIL"]

    message = MIMEText(_build_body(jobs))
    message["Subject"] = f"[job-radar] 오늘의 추천 공고 {len(jobs)}건"
    message["From"] = sender
    message["To"] = receiver

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender, app_password)
        server.sendmail(sender, [receiver], message.as_string())


def _build_body(jobs: list[dict]) -> str:
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
    send_notification(test_jobs)
    print("발송 완료 — 받은편지함을 확인해주세요.")

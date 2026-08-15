"""삼성 채용정보 수집 모듈.

samsungcareers.com이 목록을 그릴 때 내부적으로 호출하는 비공개 엔드포인트를
그대로 재현한다(브라우저 네트워크 탭에서 실제 요청 폼 데이터를 확인해서 구성).
응답은 JSON이 아니라 HTML 조각이라 BeautifulSoup으로 파싱한다.
"""

import requests
from bs4 import BeautifulSoup

LIST_DATA_URL = "https://www.samsungcareers.com/hr/list.data"
LIST_PAGE_URL = "https://www.samsungcareers.com/hr/"


def fetch_jobs() -> list[dict]:
    data = {
        "currentPageNo": "1",
        "intNo": "0",
        "strVal": "",
        "strTxt": "",
        "strKey": "",
        "strCompany": "",
        "strType": "",
        "strOrderBy": "BB",  # 최신순
        "strEntity": "",
    }
    response = requests.post(
        LIST_DATA_URL,
        data=data,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": LIST_PAGE_URL,
        },
        timeout=10,
    )
    response.raise_for_status()
    return _parse(response.text)


def _parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for li in soup.select("li"):
        title_tag = li.select_one(".title")
        company_tag = li.select_one(".company")
        link_tag = li.select_one("a[data-value]")
        if not (title_tag and company_tag and link_tag):
            continue

        job_id = link_tag["data-value"].replace(",", "")
        category_tags = [flag.get_text(strip=True) for flag in li.select(".flag.grey")]
        period_tag = li.select_one(".period")

        jobs.append(
            {
                "id": f"samsung-{job_id}",
                "title": title_tag.get_text(strip=True),
                "company": company_tag.get_text(strip=True),
                "keyword": " ".join(category_tags),
                "experience": "",
                # 개별 공고 상세링크는 세션 기반 팝업 방식이라 목록 페이지로 연결
                "url": LIST_PAGE_URL,
                "posted_at": period_tag.get_text(strip=True) if period_tag else "",
                "source": "samsung",
            }
        )
    return jobs


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"{len(jobs)}건 수집")
    for job in jobs:
        print(f"  - [{job['company']}] {job['title']} ({job['keyword']})")

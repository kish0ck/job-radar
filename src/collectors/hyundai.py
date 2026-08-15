"""현대자동차그룹 채용정보 수집 모듈.

talent.hyundai.com 페이지가 내부적으로 호출하는 공개 JSON API를 직접 호출한다.
인증이 필요 없는 공개 API이며, 개인용 1일 1회 조회로는 부담 없는 수준이다.
"""

import requests

API_URL = "https://talent.hyundai.com/api/rec/AP-HM-FO-02700"
LIST_PAGE_URL = "https://talent.hyundai.com/apply/applyList.hc"


def fetch_jobs(pageblock: int = 100) -> list[dict]:
    params = {
        "hgrCd": 1,
        "lang": "ko",
        "page": 1,
        "pageblock": pageblock,
        "searchFieldList": "",
        "searchOccupList": "",
        "searchPlaceList": "",
        "searchSectorList": "",
        "searchText": "",
        "jdSec": "",
        "srcOrd": "",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    raw_jobs = response.json()["data"]["list"]
    return [_normalize(job) for job in raw_jobs]


def _normalize(job: dict) -> dict:
    return {
        "id": f"hyundai-{job['recuYy']}-{job['recuCls']}",
        "title": job["recuNoticeNm"],
        "company": "현대자동차",
        "keyword": f"{job.get('fldCodeNm', '')} {job.get('channelCodeNm', '')}",
        "experience": job.get("channelCodeNm", ""),
        # 개별 공고 상세링크는 세션 토큰 기반이라 안정적으로 재현 불가 -> 목록 페이지로 연결
        "url": LIST_PAGE_URL,
        "posted_at": job.get("regDm", ""),
        "source": "hyundai",
    }


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"{len(jobs)}건 수집")
    for job in jobs[:5]:
        print(f"  - [{job['company']}] {job['title']} ({job['keyword']})")

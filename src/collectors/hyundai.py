"""현대자동차그룹 채용정보 수집 모듈.

talent.hyundai.com 페이지가 내부적으로 호출하는 공개 JSON API를 직접 호출한다.
인증이 필요 없는 공개 API이며, 개인용 1일 1회 조회로는 부담 없는 수준이다.
"""

from collectors._http import polite_request

API_URL = "https://talent.hyundai.com/api/rec/AP-HM-FO-02700"
DETAIL_PAGE_URL = "https://talent.hyundai.com/apply/applyView.hc"


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
    response = polite_request("GET", API_URL, params=params)
    response.raise_for_status()
    raw_jobs = response.json()["data"]["list"]
    return [_normalize(job) for job in raw_jobs]


def _normalize(job: dict) -> dict:
    detail_url = (
        f"{DETAIL_PAGE_URL}?recuYy={job['recuYy']}"
        f"&recuType={job['recuType']}&recuCls={job['recuCls']}"
    )
    return {
        "id": f"hyundai-{job['recuYy']}-{job['recuCls']}",
        "title": job["recuNoticeNm"],
        "company": "현대자동차",
        "keyword": f"{job.get('fldCodeNm', '')} {job.get('channelCodeNm', '')}",
        "experience": job.get("channelCodeNm", ""),
        "url": detail_url,
        "posted_at": job.get("regDm", ""),
        "source": "hyundai",
    }


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"{len(jobs)}건 수집")
    for job in jobs[:5]:
        print(f"  - [{job['company']}] {job['title']} ({job['keyword']})")

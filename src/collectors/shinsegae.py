"""신세계그룹 채용정보 수집 모듈.

job.shinsegae.com이 내부적으로 호출하는 공개 JSON API를 직접 호출한다.
인증이 필요 없는 공개 API. 경력(rcrutSeCd=11) + IT/디지털(dutySeCd=AA00) 공고만
API 요청 단계에서 걸러서 가져온다 (다른 직군은 이 프로젝트 관심사가 아니므로).
"""

from collectors._http import polite_request

API_URL = "https://job.shinsegae.com/api/rcrut"
DETAIL_PAGE_URL = "https://job.shinsegae.com/rcrut/detail"

# rcrutSeCd: 10=신입, 11=경력 / dutySeCd: AA00=IT/디지털
PARAMS = {"sort": 1, "rcrutSeCd": 11, "dutySeCd": "AA00"}


def fetch_jobs() -> list[dict]:
    response = polite_request("GET", API_URL, params=PARAMS)
    response.raise_for_status()
    raw_jobs = response.json()["body"]
    return [_normalize(job) for job in raw_jobs]


def _normalize(job: dict) -> dict:
    duty_names = " ".join(d["dutyNm"] for d in job.get("dutySeCd", []))
    return {
        "id": f"shinsegae-{job['pbancBscNo']}",
        "title": job["pbancNm"],
        "company": job["coNm"],
        "keyword": f"{duty_names} {job['rcrutSeNm']}",
        "experience": job["rcrutSeNm"],
        "url": f"{DETAIL_PAGE_URL}/{job['pbancBscNo']}",
        "posted_at": job.get("pbancBgngDt", ""),
        "source": "shinsegae",
    }


if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"{len(jobs)}건 수집")
    for job in jobs:
        print(f"  - [{job['company']}] {job['title']} ({job['keyword']})")

"""사람인 채용정보 API 연동 모듈.

SARAMIN_API_KEY 환경변수가 있으면 실제 API를 호출하고,
없으면(API 미승인 상태) 동일한 응답 스키마의 mock 데이터를 반환한다.
승인 후에는 환경변수만 채우면 별도 코드 수정 없이 실제 데이터로 전환된다.
"""

import os

import requests

API_URL = "https://oapi.saramin.co.kr/job-search"


def fetch_jobs(keywords: list[str], count: int = 50) -> list[dict]:
    """키워드로 채용공고를 조회해 정규화된 리스트로 반환한다."""
    api_key = os.environ.get("SARAMIN_API_KEY")
    if api_key:
        raw_jobs = _fetch_from_api(api_key, keywords, count)
    else:
        raw_jobs = _mock_jobs()
    return [_normalize(job) for job in raw_jobs]


def _fetch_from_api(api_key: str, keywords: list[str], count: int) -> list[dict]:
    params = {
        "access-key": api_key,
        "keywords": ",".join(keywords),
        "count": count,
        "fields": "posting-date,expiration-date,keyword-code",
    }
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["jobs"]["job"]


def _normalize(job: dict) -> dict:
    """사람인 API 응답 스키마를 파이프라인 공통 포맷으로 변환한다."""
    experience = job.get("experience-level", {})
    return {
        "id": f"saramin-{job['id']}",
        "title": job["position"]["title"],
        "company": job["company"]["name"],
        "keyword": job.get("keyword", ""),
        "experience": experience.get("name", ""),
        "url": job["url"],
        "posted_at": job.get("posting-date", ""),
        "source": "saramin",
    }


def _mock_jobs() -> list[dict]:
    """SARAMIN_API_KEY 미설정 시 사용하는 mock 데이터.

    사람인 API 실제 응답 스키마(jobs.job 배열)를 그대로 따른다.
    필터링 로직 테스트를 위해 포함/제외 키워드 케이스를 섞어 둔다.
    """
    return [
        {
            "id": 45671001,
            "position": {"title": "[NHN] IT서비스기획 PM 채용"},
            "company": {"name": "NHN"},
            "job-mid-code": {"code": "2", "name": "기획·전략"},
            "job-code": {"code": "104", "name": "서비스기획"},
            "experience-level": {"code": 2, "min": 3, "max": 7, "name": "경력 3~7년"},
            "keyword": "PM,서비스기획,IT",
            "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=45671001",
            "active": 1,
            "posting-date": "2026-08-14 09:00:00",
        },
        {
            "id": 45671002,
            "position": {"title": "PMO 사무국 운영 담당자 모집"},
            "company": {"name": "쿠팡"},
            "job-mid-code": {"code": "2", "name": "기획·전략"},
            "job-code": {"code": "108", "name": "PMO"},
            "experience-level": {"code": 2, "min": 5, "max": 10, "name": "경력 5~10년"},
            "keyword": "PMO,프로젝트관리",
            "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=45671002",
            "active": 1,
            "posting-date": "2026-08-14 10:30:00",
        },
        {
            "id": 45671003,
            "position": {"title": "사업개발(BR) 담당자 채용"},
            "company": {"name": "당근마켓"},
            "job-mid-code": {"code": "2", "name": "기획·전략"},
            "job-code": {"code": "112", "name": "사업개발"},
            "experience-level": {"code": 2, "min": 4, "max": 8, "name": "경력 4~8년"},
            "keyword": "BR,사업개발,파트너십",
            "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=45671003",
            "active": 1,
            "posting-date": "2026-08-13 15:00:00",
        },
        {
            "id": 45671004,
            "position": {"title": "IT 인턴 (서비스기획 보조)"},
            "company": {"name": "토스"},
            "job-mid-code": {"code": "2", "name": "기획·전략"},
            "job-code": {"code": "104", "name": "서비스기획"},
            "experience-level": {"code": 1, "min": 0, "max": 0, "name": "신입"},
            "keyword": "인턴,IT,서비스기획",
            "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=45671004",
            "active": 1,
            "posting-date": "2026-08-13 11:00:00",
        },
        {
            "id": 45671005,
            "position": {"title": "백엔드 개발자 채용(경력)"},
            "company": {"name": "라인"},
            "job-mid-code": {"code": "1", "name": "개발"},
            "job-code": {"code": "301", "name": "백엔드개발"},
            "experience-level": {"code": 2, "min": 3, "max": 6, "name": "경력 3~6년"},
            "keyword": "백엔드,Java,Kotlin",
            "url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=45671005",
            "active": 1,
            "posting-date": "2026-08-12 09:00:00",
        },
    ]


if __name__ == "__main__":
    for job in fetch_jobs(keywords=["PM", "PMO", "BR", "IT"]):
        print(job)

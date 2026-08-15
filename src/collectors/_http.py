"""크롤링 대상 사이트에 예의를 지키기 위한 공용 HTTP 유틸리티.

- 요청 전 robots.txt를 확인해서 허용 여부를 지킨다.
- 사이트가 Crawl-delay를 명시하지 않아도 기본 지연을 둬서 부하를 주지 않는다.
- 사람인 API처럼 공식 계약된 API 연동에는 쓰지 않는다(별도 호출 한도가 이미 있음).
"""

import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "job-radar-bot/1.0 (personal job alert tool; runs once daily)"
DEFAULT_DELAY_SECONDS = 2.0  # robots.txt에 Crawl-delay가 없을 때 적용하는 기본 지연

_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _get_robots_parser(url: str) -> urllib.robotparser.RobotFileParser:
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    if origin not in _robots_cache:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"{origin}/robots.txt")
        try:
            parser.read()
        except Exception:
            pass  # robots.txt가 없거나 읽기 실패 시 제한 없는 것으로 간주
        _robots_cache[origin] = parser
    return _robots_cache[origin]


def _crawl_delay(url: str) -> float:
    parser = _get_robots_parser(url)
    delay = parser.crawl_delay(USER_AGENT)
    return float(delay) if delay else DEFAULT_DELAY_SECONDS


def check_allowed(url: str) -> bool:
    return _get_robots_parser(url).can_fetch(USER_AGENT, url)


def polite_request(method: str, url: str, **kwargs) -> requests.Response:
    """robots.txt 허용 여부를 확인하고, 최소 지연 후 요청을 보낸다."""
    if not check_allowed(url):
        raise PermissionError(f"robots.txt에서 이 경로의 크롤링을 허용하지 않습니다: {url}")

    time.sleep(_crawl_delay(url))
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    return requests.request(method, url, headers=headers, timeout=10, **kwargs)

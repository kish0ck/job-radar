"""config/keywords.yaml 기반 공고 필터링 로직."""

import pathlib

import yaml

DEFAULT_CONFIG_PATH = pathlib.Path(__file__).resolve().parents[2] / "config" / "keywords.yaml"


def load_keywords(config_path: pathlib.Path = DEFAULT_CONFIG_PATH) -> dict:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_match(job: dict, config: dict) -> bool:
    """포함 키워드 1개 이상 매칭 AND 제외 키워드 미매칭이면 True."""
    searchable_text = f"{job['title']} {job.get('keyword', '')}".lower()

    include_keywords = config.get("include_keywords", [])
    exclude_keywords = config.get("exclude_keywords", [])

    included = any(kw.lower() in searchable_text for kw in include_keywords)
    excluded = any(kw.lower() in searchable_text for kw in exclude_keywords)

    return included and not excluded


def filter_jobs(jobs: list[dict], config: dict) -> list[dict]:
    return [job for job in jobs if is_match(job, config)]


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from collectors.saramin import fetch_jobs

    keywords_config = load_keywords()
    all_jobs = fetch_jobs(keywords=keywords_config["include_keywords"])
    matched = filter_jobs(all_jobs, keywords_config)

    print(f"전체 {len(all_jobs)}건 중 {len(matched)}건 매칭:")
    for job in matched:
        print(f"  - [{job['company']}] {job['title']}")

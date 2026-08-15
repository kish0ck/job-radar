"""수집 결과를 GitHub Pages용 정적 대시보드(docs/index.html)로 만드는 모듈."""

import pathlib

OUTPUT_PATH = pathlib.Path(__file__).resolve().parents[2] / "docs" / "index.html"


def generate_dashboard(
    new_jobs: list[dict],
    sent_ids: dict,
    run_log: dict,
    output_path: pathlib.Path = OUTPUT_PATH,
) -> None:
    html = _render(new_jobs, sent_ids, run_log)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def _render(new_jobs: list[dict], sent_ids: dict, run_log: dict) -> str:
    history = sorted(
        ({"id": job_id, **details} for job_id, details in sent_ids.items() if isinstance(details, dict)),
        key=lambda item: item["sent_at"],
        reverse=True,
    )

    source_rows = "".join(
        f"<tr><td>{name}</td><td>{info['count']}건</td>"
        f'<td class="{"error" if info["error"] else "ok"}">{info["error"] or "정상"}</td></tr>'
        for name, info in run_log["sources"].items()
    )

    new_job_items = "".join(
        f'<li><a href="{job["url"]}" target="_blank">[{job["company"]}] {job["title"]}</a></li>'
        for job in new_jobs
    ) or "<li>오늘은 신규 매칭 공고가 없습니다.</li>"

    history_items = "".join(
        f'<li>{item["sent_at"]} — <a href="{item["url"]}" target="_blank">'
        f'[{item["company"]}] {item["title"]}</a></li>'
        for item in history
    ) or "<li>아직 발송 이력이 없습니다.</li>"

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>job-radar 대시보드</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; color: #222; background: #fff; }}
  h1 {{ font-size: 1.4rem; }}
  h2 {{ font-size: 1.1rem; margin-top: 32px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid #eee; }}
  .ok {{ color: #2a7a2a; }}
  .error {{ color: #c0392b; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 6px 0; }}
  .meta {{ color: #888; font-size: 0.9rem; }}
</style>
</head>
<body>
  <h1>job-radar 대시보드</h1>
  <p class="meta">마지막 실행: {run_log["timestamp"]}</p>

  <h2>실행 상태</h2>
  <table>
    <tr><th>소스</th><th>수집 건수</th><th>상태</th></tr>
    {source_rows}
  </table>

  <h2>오늘의 추천 공고 ({len(new_jobs)}건)</h2>
  <ul>{new_job_items}</ul>

  <h2>발송 이력 ({len(history)}건 누적)</h2>
  <ul>{history_items}</ul>
</body>
</html>
"""

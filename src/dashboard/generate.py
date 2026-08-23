"""수집 결과를 GitHub Pages용 정적 대시보드(docs/index.html)로 만드는 모듈.

디자인은 Google Stitch로 만든 job-radar 대시보드 시안(DESIGN.md 컬러/타이포 토큰)을
그대로 이식했다. 실제 페이지가 아닌 정적 목업이었던 사이드바 네비게이션, 알림 버튼,
아바타, "Refresh Sync" 버튼 등 동작하지 않는 UI는 걷어내고, 실제 데이터가 들어가는
수집 현황 / 오늘의 추천 공고 / 발송 이력 섹션만 살렸다.
"""

import datetime
import pathlib

OUTPUT_PATH = pathlib.Path(__file__).resolve().parents[2] / "docs" / "index.html"

SOURCE_LABELS = {
    "saramin": "사람인",
    "hyundai": "현대차",
    "samsung": "삼성",
    "shinsegae": "신세계",
}

TAILWIND_CONFIG = """
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                background: "#131313", surface: "#131313",
                "surface-container-lowest": "#0e0e0e",
                "surface-container-low": "#1c1b1b",
                "surface-container": "#201f1f",
                "surface-container-high": "#2a2a2a",
                "on-background": "#e5e2e1", "on-surface-variant": "#c4c7c8",
                primary: "#ffffff", "on-primary": "#2f3131",
                "outline-variant": "#444748", outline: "#8e9192",
                error: "#ffb4ab",
            },
            borderRadius: { DEFAULT: "0.25rem", lg: "0.5rem", xl: "0.75rem", full: "9999px" },
            spacing: { xs: "4px", sm: "8px", md: "16px", lg: "24px", xl: "48px",
                       "container-max": "1440px", gutter: "20px" },
            fontFamily: { sans: ["Inter", "sans-serif"], mono: ["JetBrains Mono", "monospace"] },
        }
    }
}
"""

PAGE_HEAD = """<!doctype html>
<html lang="ko" class="dark">
<head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>job-radar 대시보드</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<script>""" + TAILWIND_CONFIG + """</script>
<style>
  body { background-color: #131313; color: #e5e2e1; font-family: 'Inter', sans-serif; }
  .material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-size: 20px;
    vertical-align: middle; }
  .glass-card { background-color: #1c1b1b; border: 1px solid #444748; }
  .status-normal { border-left: 4px solid #ffffff; }
  .status-error { border-left: 4px solid #ffb4ab; }
  .mono { font-family: 'JetBrains Mono', monospace; }
</style>
</head>
"""


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

    body = f"""
<body class="min-h-screen antialiased">
<header class="flex justify-between items-center w-full px-lg h-16 border-b border-outline-variant
               bg-surface sticky top-0 z-40 max-w-container-max mx-auto">
  <div class="flex items-center gap-sm">
    <span class="material-symbols-outlined text-primary">radar</span>
    <div>
      <h1 class="text-xl font-bold text-primary leading-tight">job-radar</h1>
      <p class="text-xs text-on-surface-variant">Recruitment Monitor</p>
    </div>
  </div>
  <div class="flex items-center text-on-surface-variant text-xs mono bg-surface-container
              py-xs px-sm rounded border border-outline-variant">
    <span class="material-symbols-outlined text-[16px] mr-xs">update</span>
    마지막 실행: {run_log["timestamp"]}
  </div>
</header>
<main class="p-lg max-w-container-max mx-auto space-y-xl">
  <section>
    <h2 class="text-xs text-on-surface-variant mb-md uppercase tracking-widest">수집 현황</h2>
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-md">
      {_render_source_cards(run_log)}
    </div>
  </section>
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-xl">
    <section class="lg:col-span-8 space-y-sm">
      <h2 class="text-lg font-bold text-primary border-b border-outline-variant pb-sm mb-md">
        오늘의 추천 공고 ({len(new_jobs)}건)
      </h2>
      {_render_job_cards(new_jobs)}
    </section>
    <section class="lg:col-span-4 space-y-md">
      <h2 class="text-lg font-bold text-primary border-b border-outline-variant pb-sm mb-md">
        발송 이력 ({len(history)}건 누적)
      </h2>
      <div class="glass-card rounded-lg p-md">
        {_render_history_timeline(history)}
      </div>
    </section>
  </div>
</main>
</body>
</html>
"""
    return PAGE_HEAD + body


def _render_source_cards(run_log: dict) -> str:
    cards = []
    for name, info in run_log["sources"].items():
        label = SOURCE_LABELS.get(name, name)
        is_error = bool(info["error"])
        status_class = "status-error" if is_error else "status-normal"
        icon = "error" if is_error else "check_circle"
        icon_color = "text-error" if is_error else "text-primary"
        status_text = "오류" if is_error else "정상"
        status_color = "text-error" if is_error else "text-primary"
        cards.append(f"""
        <div class="glass-card rounded-lg p-md {status_class} flex flex-col justify-between h-24">
          <div class="flex justify-between items-start">
            <span class="text-base font-bold text-primary">{label}</span>
            <span class="material-symbols-outlined {icon_color} text-[20px]">{icon}</span>
          </div>
          <div class="flex justify-between items-end mt-auto">
            <span class="text-sm text-on-surface-variant">{info["count"]}건</span>
            <span class="text-xs mono {status_color}">{status_text}</span>
          </div>
        </div>""")
    return "".join(cards)


def _render_job_cards(jobs: list[dict]) -> str:
    if not jobs:
        return """
        <div class="glass-card rounded-lg p-md text-on-surface-variant text-sm">
          오늘은 신규 매칭 공고가 없습니다.
        </div>"""

    cards = []
    for job in jobs:
        cards.append(f"""
        <a href="{job["url"]}" target="_blank" rel="noopener"
           class="glass-card rounded-lg p-md flex items-center gap-md hover:bg-surface-container-high
                  transition-colors group">
          <div class="w-12 h-12 rounded bg-surface-container flex items-center justify-center
                      border border-outline-variant shrink-0">
            <span class="material-symbols-outlined text-on-surface-variant">apartment</span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-base text-primary font-semibold truncate">{job["title"]}</h3>
            <p class="text-xs text-on-surface-variant truncate">{job["company"]}</p>
          </div>
          <span class="material-symbols-outlined text-on-surface-variant
                       group-hover:text-primary transition-colors shrink-0">open_in_new</span>
        </a>""")
    return f'<div class="space-y-sm">{"".join(cards)}</div>'


def _render_history_timeline(history: list[dict]) -> str:
    if not history:
        return '<p class="text-sm text-on-surface-variant">아직 발송 이력이 없습니다.</p>'

    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    groups: dict[str, list[dict]] = {}
    for item in history:
        groups.setdefault(item["sent_at"], []).append(item)

    sections = []
    for date, items in groups.items():
        label = "오늘" if date == today else "어제" if date == yesterday else date
        rows = "".join(f"""
          <div class="flex gap-sm py-xs relative">
            <div class="absolute w-2 h-2 rounded-full bg-background border border-outline-variant
                        -left-[5px] top-2"></div>
            <div class="flex-1 pl-sm">
              <a href="{item["url"]}" target="_blank" rel="noopener"
                 class="text-sm text-primary font-medium hover:underline">{item["company"]}</a>
              <p class="text-xs text-on-surface-variant truncate">{item["title"]}</p>
            </div>
          </div>""" for item in items)
        sections.append(f"""
        <div class="mb-md">
          <h4 class="text-xs text-on-surface-variant uppercase tracking-widest mb-sm
                     flex items-center gap-xs">
            <span class="w-2 h-2 rounded-full bg-primary inline-block"></span> {label}
          </h4>
          <div class="space-y-xs pl-sm border-l border-outline-variant ml-[3px]">
            {rows}
          </div>
        </div>""")
    return "".join(sections)

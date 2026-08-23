"""Stitch로 디자인한 job-radar 대시보드 스타일을 이메일용으로 이식한 템플릿.

이메일 클라이언트는 <script>를 제거하고 외부 스타일시트/아이콘 폰트를 신뢰할 수 없게
불러오기 때문에, Tailwind/Material Symbols 기반 원본 대신 인라인 스타일만으로
같은 색상·타이포 톤을 재현한다. 사이드바/아바타 등 웹앱 전용 요소는 제외.
"""

from __future__ import annotations

# DESIGN.md의 컬러 토큰 중 이메일에 필요한 것만 가져옴
COLOR_BG = "#131313"
COLOR_CARD = "#1c1b1b"
COLOR_BORDER = "#444748"
COLOR_TEXT = "#e5e2e1"
COLOR_TEXT_MUTED = "#c4c7c8"
COLOR_ACCENT = "#ffffff"
COLOR_ERROR = "#ffb4ab"

FONT_STACK = "'Inter','Segoe UI',-apple-system,Roboto,sans-serif"
MONO_STACK = "'JetBrains Mono',Consolas,monospace"

SOURCE_LABELS = {
    "saramin": "사람인",
    "hyundai": "현대차",
    "samsung": "삼성",
    "shinsegae": "신세계",
}

DASHBOARD_URL = "https://kish0ck.github.io/job-radar/"
HISTORY_LIMIT = 20  # 메일이 무한정 길어지지 않도록 최근 N건만 표시, 전체는 대시보드에서


def render_html(
    jobs: list[dict],
    run_log: dict | None = None,
    sent_ids: dict | None = None,
) -> str:
    source_section = _render_source_status(run_log) if run_log else ""
    job_cards = "".join(_render_job_card(job) for job in jobs)
    history_section = _render_history(sent_ids) if sent_ids else ""

    return f"""\
<div style="background:{COLOR_BG};padding:24px 16px;font-family:{FONT_STACK};">
  <div style="max-width:600px;margin:0 auto;">
    <div style="font-size:20px;font-weight:700;color:{COLOR_ACCENT};margin-bottom:16px;">
      \U0001F4E1 job-radar
    </div>
    {source_section}
    <div style="font-size:17px;font-weight:700;color:{COLOR_ACCENT};
                border-bottom:1px solid {COLOR_BORDER};padding-bottom:8px;margin-bottom:12px;">
      오늘의 추천 공고 ({len(jobs)}건)
    </div>
    {job_cards}
    {history_section}
    <div style="font-size:12px;color:{COLOR_TEXT_MUTED};margin-top:24px;">
      job-radar가 매일 자동으로 보내는 개인용 채용 알림입니다.
    </div>
  </div>
</div>
"""


def _render_source_status(run_log: dict) -> str:
    cells = []
    for name, info in run_log.get("sources", {}).items():
        label = SOURCE_LABELS.get(name, name)
        is_error = bool(info.get("error"))
        status_color = COLOR_ERROR if is_error else COLOR_TEXT
        status_text = "오류" if is_error else "정상"
        cells.append(f"""
          <td style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                     border-left:3px solid {status_color};border-radius:8px;
                     padding:10px 12px;width:25%;">
            <div style="font-size:13px;font-weight:700;color:{COLOR_ACCENT};">{label}</div>
            <div style="font-size:11px;color:{COLOR_TEXT_MUTED};margin-top:2px;">
              {info.get('count', 0)}건 · <span style="color:{status_color};">{status_text}</span>
            </div>
          </td>""")

    rows = "".join(cells)
    return f"""
    <table role="presentation" width="100%" cellpadding="4" cellspacing="0" style="margin-bottom:20px;">
      <tr>{rows}</tr>
    </table>"""


def _render_history(sent_ids: dict) -> str:
    history = sorted(
        (details for details in sent_ids.values() if isinstance(details, dict)),
        key=lambda item: item["sent_at"],
        reverse=True,
    )
    if not history:
        return ""

    rows = "".join(_render_history_row(item) for item in history[:HISTORY_LIMIT])
    more_note = ""
    if len(history) > HISTORY_LIMIT:
        more_note = f"""
        <div style="font-size:12px;color:{COLOR_TEXT_MUTED};margin-top:8px;">
          최근 {HISTORY_LIMIT}건만 표시 중입니다.
          <a href="{DASHBOARD_URL}" style="color:{COLOR_ACCENT};">전체 이력은 대시보드에서 보기 &rarr;</a>
        </div>"""

    return f"""
    <div style="font-size:17px;font-weight:700;color:{COLOR_ACCENT};
                border-bottom:1px solid {COLOR_BORDER};padding-bottom:8px;
                margin:24px 0 12px;">
      발송 이력 ({len(history)}건 누적)
    </div>
    <div style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};border-radius:12px;
                padding:4px 16px;">
      {rows}
    </div>
    {more_note}"""


def _render_history_row(item: dict) -> str:
    return f"""
    <a href="{item['url']}" style="display:block;padding:10px 0;
              border-bottom:1px solid {COLOR_BORDER};text-decoration:none;">
      <span style="font-family:{MONO_STACK};font-size:11px;color:{COLOR_TEXT_MUTED};">
        {item['sent_at']}
      </span>
      <div style="font-size:13px;color:{COLOR_TEXT};margin-top:2px;">
        <span style="color:{COLOR_TEXT_MUTED};">[{item['company']}]</span> {item['title']}
      </div>
    </a>"""


def _render_job_card(job: dict) -> str:
    # 카드 전체를 <a>로 감싸서 어디를 눌러도 공고 링크로 이동하게 한다
    # (제목 텍스트만 링크면 카드 여백을 눌렀을 때 아무 반응이 없어 헷갈림)
    return f"""
    <a href="{job['url']}" style="display:block;background:{COLOR_CARD};
              border:1px solid {COLOR_BORDER};border-radius:12px;padding:14px 16px;
              margin-bottom:8px;text-decoration:none;">
      <div style="font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;
                  color:{COLOR_TEXT_MUTED};margin-bottom:4px;font-family:{MONO_STACK};">
        {job['company']}
      </div>
      <div style="font-size:15px;font-weight:600;color:{COLOR_ACCENT};">
        {job['title']} &rarr;
      </div>
    </a>"""

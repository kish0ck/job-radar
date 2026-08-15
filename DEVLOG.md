# DEVLOG — AI 협업 및 의사결정 기록

Phase 0 체크리스트에 따라, 포트폴리오화(Phase 7) 때 쓸 수 있도록
주요 프롬프트 / 의사결정 근거 / AI로 단축된 작업 / 트러블슈팅을 여기에 쌓아갑니다.

## 2026-08-15 — 기획 단계 (Phase 0~3)

- **의사결정**: 알림 수단을 카카오톡이 아닌 이메일(SMTP)로 최종 결정
  - 근거: 카카오 "나에게 보내기" API는 Access Token 6시간, Refresh Token도 1개월마다
    갱신이 필요한데, GitHub Actions는 무상태 실행 환경이라 자동 갱신 로직을 별도로
    만들어야 함. 개인용 무료 프로젝트 스코프에는 오버스펙으로 판단.
- **의사결정**: 관심 기업(삼성/LG/현대) 채용 페이지는 모두 JS 렌더링 SPA로 확인됨
  → requests+BeautifulSoup 대신 Playwright(headless Chromium) 채택
- **의사결정**: 대시보드는 별도 서버/DB 없이 GitHub Pages 정적 페이지로 구현
  (기존 GitHub Actions 워크플로우에 발행 단계만 추가)

## 2026-08-15 — 스프린트 #2: 사람인 API 연동 모듈

- **AI 활용**: 사람인 API가 미승인 상태라, AI로 공식 API 문서(oapi.saramin.co.kr)를
  직접 조회해서 request 파라미터와 response 필드(스키마: `jobs.job[]`, 각 항목의
  `position.title`, `company.name`, `experience-level` 등)를 먼저 확인한 뒤 모듈을 작성.
  덕분에 "일단 대충 mock 만들기"가 아니라 실제 스키마와 동일한 mock 데이터로 개발 →
  API 승인 후에는 `SARAMIN_API_KEY` 환경변수만 채우면 코드 수정 없이 실제 연동으로 전환됨.
- **결과**: `src/collectors/saramin.py` — mock 모드로 정상 동작 확인 완료

## 2026-08-15 — 스프린트 #4: 관심기업 크롤링 (현대차/삼성)

- **AI 활용**: Phase 3에서는 "삼성/LG/현대 모두 JS 렌더링 SPA라 Playwright 필요"로
  예상했으나, AI가 브라우저로 실제 사이트를 열어 네트워크 요청을 직접 조사한 결과
  뒤집힘. 현대차는 인증 없는 공개 JSON API(`/api/rec/AP-HM-FO-02700`)를 그대로
  호출하면 되고, 삼성은 화면이 호출하는 내부 엔드포인트(`/hr/list.data`)에 실제
  브라우저가 보내는 form 파라미터를 그대로 재현하면 됨 — 둘 다 **Playwright 불필요**.
  (JS로 `fetch`/`XMLHttpRequest`를 몽키패치해서 실제 요청 폼 데이터를 잡아낸 뒤
  Python `requests`로 그대로 재현하는 방식으로 조사)
- **의사결정**: 두 곳 다 공고 상세페이지 링크가 세션/토큰 기반이라 개별 딥링크를
  안정적으로 재현할 수 없음 → 목록 페이지 URL로 연결하는 것으로 절충
  (잘못된 링크를 보내는 것보다 안전한 선택)
- **의사결정**: LG는 렌더링된 화면엔 전체 공고가 다 보이지만 숨은 API를 못 찾음
  → Playwright가 실제로 필요한 유일한 케이스. 이번 스프린트에서는 보류하고
  현대차/삼성만 우선 구현
- **결과**: `src/collectors/hyundai.py`(실제 API, 61건 수집 확인),
  `src/collectors/samsung.py`(실제 HTML 파싱, 6건 수집 확인) — 둘 다 mock이 아닌
  실제 데이터로 검증 완료

## 2026-08-15 — 스프린트 #5: 중복 방지 저장소

- **결과**: `src/storage/sent_jobs.py` 작성 — `data/sent_jobs.json`에 `{공고ID: 발송일자}`
  기록. 이미 발송된 ID는 다음 실행에서 걸러지는 로직을 샘플 데이터로 검증 완료

## 2026-08-16 — 스프린트 #6~#7: 이메일 발송 + 메인 파이프라인

- **결과**: `src/notifiers/email_notifier.py`(Gmail SMTP, 앱 비밀번호는 `.env`로 관리)로
  테스트 발송 성공 확인. 이후 수신 주소를 `kistone3@naver.com`으로 변경.
- **결과**: `src/main.py` 작성 — 사람인(mock)+현대차+삼성 수집 → 키워드 필터링 →
  중복 제거 → 이메일 발송 → 발송 기록까지 전체 파이프라인 연결.
  실제 실행 결과: 총 72건 수집 → 11건 매칭 → 11건 신규 발송.
  같은 파이프라인을 재실행해서 **중복 방지가 실제로 동작**하는 것도 확인
  (2차 실행 시 신규 0건, 발송 생략).

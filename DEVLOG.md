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

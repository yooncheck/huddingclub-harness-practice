# default-design.md

비주얼 기본값. 사용자가 값을 정하지 않으면 이 파일의 값을 쓴다.
원본: [docs/design.md](../docs/design.md) — 충돌 시 design.md의 Do's and Don'ts가 우선한다.

표기: 🅳 = design.md에 있는 값 · 🔸 = 임의 추가(사용자 확인 필요)

## Colors 🅳

| 토큰 | 값 | 용도 |
|---|---|---|
| primary / ink | #141414 | CTA 필, 제목·본문, 푸터 |
| ink-soft | #262626 | 보조 락업 |
| canvas | #ffffff | 기본 배경 |
| canvas-soft | #f3f3f3 | 내비 필, 강조 카드, FAQ 행, 세그먼트 트랙 |
| field | #f0f0f0 | 입력창 채움 |
| hairline-soft | #f0f0f0 | 휴지 상태 카드 1px 외곽선 |
| hairline | #e0e0e0 | 아웃라인 버튼 1px 테두리 |
| text-muted | #707070 | 보조 문구 |
| text-faint | #adadad | placeholder, 약한 링크 |
| accent | #0066ff | 상업 신호 전용 (페이지당 1~2개) |
| badge-overlay | rgba(115,115,115,0.56) | 사진 위 태그 |
| on-primary | #ffffff 🔸 | ink 채움 위 글자 (design.md에 값 없음) |

## Typography 🅳

Pretendard 단독. 폴백: `-apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif`. letter-spacing 0, 대문자 변환 없음.

| 토큰 | 크기 | 굵기 | 행간 |
|---|---|---|---|
| display | 32 | 700 | 1.3 |
| heading-1 | 28 | 700 | 1.3 |
| heading-2 | 24 | 700 | 1.35 |
| heading-3 | 20 | 700 | 1.35 |
| heading-4 | 18 | 700 | 1.35 |
| title | 17 | 600 | 1.4 |
| body-lg | 17 | 300 | 1.5 |
| body | 15 | 400 | 1.5 |
| body-sm | 13 | 400 | 1.5 |
| link | 15 | 600 | 1.5 |
| label | 12 | 600 | 1.4 |
| caption | 12 | 400 | 1.4 |

## Layout 🅳

- 기준 프레임 390×844, 최소 폭 360 (가로 스크롤 금지). 태블릿/데스크톱은 MVP 밖.
- 간격 토큰: 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 (기본 단위 8, 반 단위 4)
- 화면 좌우 패딩 16, 섹션 간격 48, 큰 구간 간격 64
- 터치 타깃 최소 44px
- 기본 단일 컬럼, 그리드는 최소 폭에서 1컬럼으로 접힘

## Shape 🅳

| 토큰 | 값 | 용도 |
|---|---|---|
| rounded.none | 0px | 풀블리드 미디어 스트립 |
| rounded.full | 9999px | 버튼, 내비, 배지, 토글 등 모든 인터랙션 요소 |
| rounded.md | 24px | 콘텐츠 카드, 기기 목업, 푸터 상단 |
| rounded.sm | 16px | 입력창, 영상 타일, FAQ 행 |
| app-icon | 반지름 30% | 앱 아이콘 스쿼클 |

## Elevation 🅳

그림자 없음. 깊이는 채움 차이와 1px 헤어라인으로만 표현. 유일한 예외는 세그먼트 컨트롤의 활성 칸.

## Components 🅳

- **button-primary**: ink 채움, on-primary 글자, full 필, 고정 높이. 모든 주요 CTA.
- **button-outline**: canvas 채움, 1px hairline, full 필.
- **button-pill-soft**: canvas-soft 채움, 테두리 없음.
- **text-input**: field 채움, 테두리 없음, rounded.sm, 패딩 12 16. 포커스 시 2px ink 링.
- **nav-pill**: canvas-soft 채움의 떠 있는 필. 모바일은 로고 + CTA로 축소.
- **footer**: ink 채움, 상단 rounded.md.
- 포트레이트: 항상 흑백.

## 정해지지 않은 값 (design.md에 없음 → 🔸 기본값)

| 항목 | 기본값 | 근거 |
|---|---|---|
| 버튼 고정 높이 | 44px 🔸 | design.md의 터치 타깃 최소값을 그대로 사용 |
| 상태 배지 (작성 중 / 제출 완료 / 검수 대기 / 수정 요청 / 승인됨 / 반려) | 모노크롬 사다리만 사용: canvas-soft 채움 + ink 글자 + full 필. 상태는 글자로 구분하고 색으로 구분하지 않는다 🔸 | design.md가 "상태 전달은 모노크롬 사다리 안에서"라고 함. 상태별 색은 정의돼 있지 않음 |
| 성공/경고/오류 색 | 없음 🔸 | 위와 같음. 필요하면 사용자가 정해야 함 |

# 허들링 화면 디자인 하네스

## 목적
화면 1개 세트를 입력받아 레퍼런스 수집부터 가이드 검토까지 진행한다.
완료 기준: 대상 화면 세트의 Figma 시안이 390×844이고, gates.md의 D1~D13과 C1~C8을
위반 0건으로 통과했고, 내부 관계자 승인을 1회 받았다. (harness/purpose.md)

## 두 기준을 섞지 않는다
- docs/story-service.md = 무엇을 위한 일인가 (판정 기준, "어기면 안 되는 것")
- docs/story-work.md = 내가 어떻게 했는가 (작업 방식)

## 파이프라인 (harness/pipeline.md)
| 단계 | 하는 일 | 출력 |
|---|---|---|
| S1 | 수집·분석 | s1-references.md, s1-analysis.md |
| S2 | 화면 설계 문서 | s2-spec.md |
| S3 | 키스크린 2~3개 + 사람 승인 | s3-keyscreens.md, s3-approval.md |
| S4 | 토큰·컴포넌트·화면 | s4-tokens.json, s4-components.md, s4-screens.md |
| S5 | 가이드 검토 | s5-report.json |
되돌림: D 위반 → S4, C 위반 → S2, 승인 반려 → S3. 같은 단계 3회까지, 4회째에 멈춘다.

## 파일 위치
- 산출물: runs/<slug>/ (slug는 영문 소문자와 하이픈). 상세는 harness/artifacts.md
- 되돌아가면 덮어쓰지 않고 -v숫자를 붙인다.
- 규칙의 유일한 원본: harness/gates.md. 값은 harness/default-design.md, default-content.md
- 판정 명세: harness/verdict-spec.md. 역할: harness/roles.md. 검증: harness/verification.md
- 참조 문서: docs/prd.md, docs/design.md

## 역할 (harness/roles.md)
- researcher: S1, S2 / designer: S3, S4 / orchestrator: 단계 이동 / verdict: 읽기 전용 판정

## 트리거
- "<화면 이름> 하네스 돌려줘" → 시작
- "이어서 해줘" → runs/<slug>/state.json을 읽고 재개
- "<화면 이름> 승인했어" → 승인자 이름을 확인한 뒤 s3-approval.md 기록, S4로 이동

## 단계 시작 전 재확인
1. state.json 읽기
2. purpose.md의 완료 기준 다시 읽기
3. gates.md에서 이 단계에 걸리는 게이트 ID 출력
4. 되돌아간 횟수 확인

## 금지 (모두 0회)
1. gates.md, default-*.md 수정
2. 판정 없이 "통과했다"고 말하기
3. 사용자의 이름 없이 s3-approval.md 작성
4. 자기 역할의 편집 폴더 밖 파일 수정
5. 사용자 확인 없이 Figma 파일·프레임 삭제

## 멈추고 사람에게 묻는 조건
1. 종료 코드 2 (되돌림 4회째)
2. PRD나 design.md에 없는 값이 필요할 때 (지어내지 않는다)
3. 입력 파일이 없을 때
4. 판정자와 작업 에이전트 결과가 다를 때 (판정자 결과를 따르고 보고)

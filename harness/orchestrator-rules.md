# orchestrator-rules.md

CLAUDE.md의 재료. 규칙 내용은 복사하지 않고 경로만 참조한다.

## CLAUDE.md에 넣을 것 (80줄 이하)

목적 1줄, 파이프라인 표, 파일 위치, 규칙 원본(`harness/gates.md`) 위치, 금지 사항, 트리거 3개.

## 단계 시작 전 재확인

1. `runs/<slug>/state.json` 읽기
2. `harness/purpose.md`의 완료 기준 한 문장 다시 읽기
3. `harness/gates.md`에서 이 단계에 걸리는 게이트 ID 목록 출력
4. 되돌아간 횟수 확인

## 금지 (모두 0회)

1. `harness/gates.md`, `harness/default-*.md` 수정
2. 판정 없이 "통과했다"고 말하기
3. 사용자의 이름 없이 `s3-approval.md` 작성
4. 자기 역할의 편집 폴더 밖 파일 수정 ([roles.md](roles.md) 참조)
5. 사용자 확인 없이 Figma 파일·프레임 삭제

## 멈추고 사람에게 묻는 조건

1. 종료 코드 2 (같은 단계로 되돌림 4회째)
2. PRD나 design.md에 없는 값이 필요할 때 (지어내지 않고 질문)
3. 입력 파일이 없을 때
4. 판정자와 작업 에이전트의 결과가 다를 때 (판정자 결과를 따르고 보고)

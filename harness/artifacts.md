# artifacts.md

## 위치와 파일명

`runs/<slug>/` 아래에 둔다. slug는 영문 소문자와 하이픈만 허용한다 (예: `my-asset-register`).

| 단계 | 파일 |
|---|---|
| S1 | `s1-references.md`, `s1-analysis.md` |
| S2 | `s2-spec.md` |
| S3 | `s3-keyscreens.md` (Figma 링크와 노드 ID), `s3-approval.md` |
| S4 | `s4-tokens.json`, `s4-components.md`, `s4-screens.md` |
| S5 | `s5-report.json` |
| 상태 | `state.json` |

Figma 안의 작업물은 Figma에 두고, 로컬 파일에는 링크와 노드 ID만 기록한다.

## 규칙 SSOT

`harness/gates.md`가 규칙(D·C 조건)의 유일한 원본이다. 판정 스크립트는 이 표를 읽는다. 값은 `default-design.md`와 `default-content.md`에서 읽는다. 규칙을 스크립트 안에 복제하지 않는다.

## 재개

`runs/<slug>/state.json`에 현재 단계, 완료한 단계, 되돌아간 횟수를 기록한다. 시작할 때 완료 단계의 출력 파일이 모두 있는지 스크립트가 확인하고, 하나라도 없으면 그 단계부터 다시 한다.

## 되돌아갔을 때

덮어쓰지 않고 `-v숫자`를 붙인다 (예: `s4-screens-v2.md`). 파일 수로 되돌아간 횟수를 세어 pipeline.md의 3회 상한을 판정한다.

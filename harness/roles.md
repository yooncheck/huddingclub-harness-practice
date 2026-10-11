# roles.md

## 에이전트와 편집 폴더

| 역할 | 담당 단계 | 편집 가능 | 비고 |
|---|---|---|---|
| researcher | S1, S2 | `runs/<slug>/s1*`, `runs/<slug>/s2*` | |
| designer | S3, S4 | `runs/<slug>/s3*`(승인 파일 제외), `runs/<slug>/s4*`, Figma | |
| orchestrator | 단계 이동 | `runs/<slug>/state.json`, `runs/<slug>/s3-approval.md`(사용자가 이름을 말한 경우만) | |
| verdict | S5 및 단계별 판정 | `runs/<slug>/s5-report.json`만 출력 | 읽기 전용 판정자. 다른 파일은 수정하지 않는다 |

`harness/gates.md`와 `harness/default-*.md`는 모든 역할이 읽기 전용이다.

## 자연어 트리거

| 말 | 동작 |
|---|---|
| "<화면 이름> 하네스 돌려줘" | orchestrator가 slug를 만들고 S1부터 시작 |
| "이어서 해줘" | `state.json`을 읽고 중단된 단계에서 재개 |
| "<화면 이름> 승인했어" | 승인자 이름을 확인한 뒤 `s3-approval.md`에 기록하고 S4로 이동 |

## 사람 승인 기록

승인은 사용자가 이름을 말할 때만 기록한다. 이름 없이 "승인했어"만 오면 이름을 되묻는다. 에이전트가 이름을 지어내지 않는다.

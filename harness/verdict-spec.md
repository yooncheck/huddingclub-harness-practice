# verdict-spec.md

판정 스크립트의 입출력 명세. 규칙 자체는 [gates.md](gates.md)에만 있고, 이 파일은 복제하지 않는다.

## 입력

- `runs/<slug>/` 안의 단계 산출물 ([artifacts.md](artifacts.md))
- `harness/gates.md` (D1~D13, C1~C8, P1~P5)
- `harness/default-design.md`, `harness/default-content.md` (값)

## 출력: `runs/<slug>/s5-report.json`

```json
{
  "slug": "",
  "stage": "S1|S2|S3|S4|S5",
  "violations": [{"id": "D3", "file": "", "location": "", "detail": ""}],
  "passed": true,
  "return_to": null
}
```

- `passed`는 `violations`가 비었을 때만 true.
- `return_to`는 [pipeline.md](pipeline.md)의 되돌아가는 지점을 따른다 (D → S4, C → S2).
- 종료 코드: 0 = 통과, 1 = 위반 있음, 2 = 되돌림 상한 초과(멈춤).

## 판정 방식

| 대상 | 방식 |
|---|---|
| 색상값, 반지름, 폰트 (D1, D4, D5, P5) | `s4-tokens.json`을 읽어 허용 집합과 비교 |
| 이메일·전화번호 (C4) | `s2-spec.md`, `s4-screens.md`의 텍스트에 정규식 매치 개수 세기 |
| 체크리스트 문항, 기본 선택값, 승인 버튼 조건 (C2, C3, C4) | `s2-spec.md`, `s4-screens.md`에서 지정 문자열 존재 여부 확인 |
| 개수 (P1, P3) | 링크·노드 개수 세기 |
| 사람 승인 (P4) | `s3-approval.md` 존재와 필수 항목 확인 |
| 되돌림 상한 | `-v숫자` 파일 수와 `state.json`의 횟수 비교 |

## 스크립트가 판정하지 못하는 것

Figma 안의 시각 요소(그림자, 그라디언트 등 D2, D3, D8, D9 일부)는 에이전트가 기록한 속성 목록으로만 판정한다. 스크립트는 Figma를 직접 보지 못한다. 대신 **속성이 기록되지 않으면 통과가 아니라 위반("속성 미기록")으로 처리한다.** 해당 사항이 없어도 빈 리스트(`[]`)로 기록해야 한다.

## 사용법

```
python3 harness/verdict.py <slug> --stage S1|S2|S3|S4|S5
python3 -m unittest discover -s harness/tests -v     # 스크립트 자체 검증
```

- 단계별로 어떤 게이트를 돌리는지는 gates.md의 "걸리는 단계" 열을 읽어 정한다 (S1={1,2}, S2={3}, S3={4,5}, S4={6-a,6-b,6-c}, S5={7}). P 게이트는 자기 단계에서만 돈다.
- 쓰는 파일은 `runs/<slug>/s5-report.json` 하나뿐이다. 보고서에는 `checked`(이번에 돌린 게이트 ID)가 추가로 들어간다.
- 같은 단계로의 되돌림 횟수는 `state.json`의 `returns`와 `-vN` 파일 중 큰 값으로 센다. 위반이 있고 횟수가 3 이상이면 종료 코드 2.
- 각 `.md` 파일의 첫 번째 ```json 블록이 속성이다. 파일들의 블록은 합쳐지고(리스트는 이어 붙임), `s4-tokens.json`은 따로 읽는다.

## 속성 기록 형식

| 파일 | 키 | 형식 | 판정 |
|---|---|---|---|
| s3-keyscreens.md, s4-screens.md | `frames` | `[{name, width, height}]` | D10, P3 |
| 〃 | `horizontal_scroll_360` | bool | D10 |
| 〃 | `side_padding` | 숫자 | D10 |
| s4-screens.md | `accent_uses` | `[{page, kind}]` kind=`cta`/`commercial` | D2 |
| 〃 | `uppercase_text`, `gradients_chrome`, `colored_bands`, `extra_accent_hues` | 리스트 | D6, D8 |
| 〃 | `portraits` | `[{name, grayscale}]` | D9 |
| 〃 | `status_badges` | `[{label, color_only}]` | D13 |
| 〃 | `colors`, `spacings` | 리스트 | D1, D12 |
| s4-components.md | `shadows` | 리스트 (예외: `segmented-control-active`) | D3 |
| 〃 | `interactive` | `[{name, radius, height}]` | D4, D11 |
| 〃 | `inputs` | `[{name, rest_border}]` | D7 |
| s2-spec.md | `sale_requested_roles` | 리스트 | C1 |
| 〃 | `asset_default_visibility` | 문자열 | C2 |
| 〃 | `approve_button_enabled_when` | 문자열 ("8/8" 포함) | C3 |
| 〃 | `review_checklist` | 문자열 8개 (6번에 "개인정보", 7번에 "저작권") | C4 |
| 〃 | `review_flow` | `[[상태, ...]]` | C5 |
| 〃 | `statuses` | `{submission, visibility, review}` 리스트 | C6 |
| 〃 | `paid_content_exposure` | `{free, guest}` = `preview`/`none`/`full` | C8 |
| s4-tokens.json | `colors`, `radius`, `font.family`, `typography`, `letterSpacing`, `spacing` | 토큰 이름 → 값 | D1, D4~D6, D12, P5 |

C4(이메일·전화번호)와 C7(범위 밖 키워드)은 속성이 아니라 `.md` 본문 텍스트를 직접 센다. C7은 제목에 "범위 밖"이 들어간 섹션을 제외한다.

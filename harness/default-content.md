# default-content.md

권한·상태·검수 기본값. 사용자가 값을 정하지 않으면 이 파일의 값을 쓴다.
원본: [docs/prd.md](../docs/prd.md) (MVP 1차 기준). 이 파일에는 🔸 임의 추가 값이 없다.

## 역할 🅿 §7, §8

`guest` / `free` / `paid` / `seller` / `admin`
- `seller` = 유료 회원 중 운영진이 수동 승인한 회원 (앱 밖에서 요청받고 운영자가 역할 변경)
- `admin`은 여러 명에게 부여 가능

## 기본 공개 범위 🅿 §14

멤버가 만든 자산은 기본 `private`. 본인이 선택할 때만 `member_only` 또는 `sale_requested`.
`sale_requested`는 `seller`만 선택 가능.

## 허용 상태값 (MVP 1차) 🅿 §6-4, §6-5, §9

| 대상 | 허용값 | MVP에서 쓰지 않는 값 |
|---|---|---|
| Submission.status | `draft`, `submitted` | feedback_pending, revision_requested, approved |
| Asset.visibility | `private`, `member_only`, `sale_requested` | for_sale (Phase 2) |
| Asset.review_status | `draft`, `pending`, `revision_requested`, `approved`, `rejected` | suspended (Phase 2) |

판매 신청 자산의 MVP 최종 상태는 `approved`.

## 판매 검수 체크리스트 🅿 §6-7 (검수 시 필수, 8개 모두 충족해야 승인)

1. 실제 업무에 써본 것
2. 결과 예시가 있는 것
3. 사용 방법이 명확한 것
4. 초보자가 따라할 수 있는 것
5. 특정 툴/버전/환경 조건이 적혀 있는 것
6. 개인정보/고객정보/회사기밀이 없는 것
7. 저작권 문제가 없는 것
8. 구매자가 바로 써볼 수 있는 것

## 판매 자산에 포함될 수 없는 것 🅿 §14

개인정보, 고객정보, 회사기밀, 타인의 저작물

## 범위 밖 (만들지 않는다) 🅿 §9

허들링 픽 노출, 구매자 흐름, 결제·정산, 수익 내역, 미션 피드백, AI 1차 검수, 실시간 채팅, 앱 내 커뮤니티 피드, 리뷰/평점, 자동 추천

검출 키워드 🔸 (판정 스크립트가 설계 문서·시안 텍스트에서 센다. 본문의 "범위 밖 항목" 섹션은 제외):
- 허들링 픽
- 구매하기
- 구매 버튼
- 결제하기
- 정산 내역
- 수익 내역
- 미션 피드백
- 피드백 도착
- AI 1차 검수
- 리뷰
- 평점

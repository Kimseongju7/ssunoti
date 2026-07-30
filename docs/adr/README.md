# Architecture Decision Records

이 프로젝트의 아키텍처 결정 기록. **한 번 쓰면 고치지 않는다** — 결정이 바뀌면
새 ADR 을 쓰고 기존 것의 Status 를 `superseded by ADR-NNNN` 으로 바꾼다.

`CLAUDE.md` 는 "지금 어떻게 되어 있는가"를 담고 갱신된다.
ADR 은 "왜 그렇게 정했는가"를 담고 갱신되지 않는다.

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-no-derived-state-in-firestore.md) | Firestore 문서에 파생 상태를 저장하지 않는다 | accepted | 2026-07-28 |
| [0002](0002-send-before-persist-at-least-once.md) | 신규 공고는 FCM 발송 성공 후에만 Firestore 에 기록한다 | accepted | 2026-07-28 |
| [0003](0003-capacity-nullable-counts-zero.md) | `capacity` 만 nullable, 신청자·대기자는 0 고정 | accepted | 2026-07-28 |

## 새 ADR 쓰기

`template.md` 복사 → 번호는 위 표의 마지막 +1 → 표에 한 줄 추가.

## Status

- `proposed` — 논의 중, 아직 적용 안 됨
- `accepted` — 적용 중
- `deprecated` — 더 이상 해당 없음 (기능 제거 등)
- `superseded by ADR-NNNN` — 새 결정으로 대체됨. 반드시 링크할 것

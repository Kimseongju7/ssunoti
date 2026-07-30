# ADR-0001: Firestore 문서에 파생 상태를 저장하지 않는다

**Date**: 2026-07-28
**Status**: accepted
**Deciders**: Kimseongju7

## Context

초기 설계(`ssunoti_server/docs/firestroe_design.md`)는 `is_closing_soon`,
`notified_deadline` 같은 계산된 플래그를 `notices` 문서에 저장하려 했다.

그러나 SSUPath 도메인 조사 결과 세 가지 사실이 확인됐다.

- 신청 **취소 기능이 없다** — 신청자 수는 줄지 않는다
- **정원은 증원될 수 있다** — `capacity` 가 커지면 "정원 임박"이 풀린다
- **마감은 연장될 수 있다** — `deadline` 이 밀리면 "마감 임박"이 풀린다

한 번 계산해 기록한 플래그는 원본 값이 바뀌어도 갱신 트리거가 없으면
영구히 어긋난다. 사용자는 이미 여유가 생긴 공고를 "임박"으로 계속 보게 된다.

## Decision

원시값(`deadline`, `capacity`, `applicant_count`, `waitlist_count`)만 저장한다.
임박 여부는 읽는 쪽(Flutter 앱)이 조회 시점에 계산한다.

## Alternatives Considered

### 대안 1: 래치 플래그를 문서에 저장

- **Pros**: 앱 쿼리가 단순해짐. `where("is_closing_soon", "==", true)` 로 서버 필터 가능
- **Cons**: 정원 증원·마감 연장 시 값이 상함
- **Why not**: 갱신 잡을 추가하면 그 잡이 다시 상할 조건(실행 실패, 주기 사이 변경)을
  만든다. 상하는 데이터를 상하지 않게 만드는 잡을 또 상할 수 있게 만드는 순환

### 대안 2: TTL 을 붙인 캐시 필드

- **Pros**: 만료 후 재계산하므로 무한정 상하지는 않음
- **Cons**: Firestore 에 TTL 기반 재계산 트리거가 없음
- **Why not**: 결국 주기 잡을 만들어야 하고, 대안 1 과 같은 문제에 복잡도만 추가

## Consequences

### Positive

- `capacity` 증원, `deadline` 연장에도 저장된 데이터가 상하지 않는다
- 임박 기준(정원 90%? 마감 3일 전?)을 **서버 배포 없이 앱에서 변경**할 수 있다
- 저장 필드가 9개로 줄어 스키마가 단순해진다

### Negative

- 앱이 매 조회마다 계산한다. 목록이 수십 건 규모라 실질 부담은 없다
- "임박한 공고만" 서버 쿼리가 불가능하다. 앱이 전체를 받아 클라이언트에서 필터한다

### Risks

- `capacity == null` 인 경우 임박 판단 자체를 하지 않아야 한다.
  0으로 취급하면 0/0 이 되어 마감으로 오인된다 → [ADR-0003](0003-capacity-nullable-counts-zero.md)
- 신규 판별 근거가 "문서 존재 여부" 하나만 남는다. 이 결과가
  발송·저장 순서를 강제한다 → [ADR-0002](0002-send-before-persist-at-least-once.md)

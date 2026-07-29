# ADR-0003: `capacity` 만 nullable, 신청자·대기자는 0 고정

**Date**: 2026-07-28
**Status**: accepted
**Deciders**: Kimseongju7

## Context

크롤러가 목록에서 파싱하는 세 카운트 필드는 숫자가 아닌 값(`"-"` 등)을
반환할 수 있다. `crawler.py` 에 미해결 TODO 로 남아 있던 문제다.

```python
applicant_count = int(cnt_map.get('신청자', 0))   # "-" 이면 ValueError
waitlist_count  = int(cnt_map.get('대기자', 0))
capacity        = int(cnt_map.get('모집정원', 0))
```

세 필드를 일괄 처리할지, 필드별로 다르게 할지 정해야 했다.
[ADR-0001](0001-no-derived-state-in-firestore.md) 로 임박 판단을 앱이 하게 되면서,
앱이 이 값들을 어떻게 해석하는지가 정규화 규칙을 좌우하게 됐다.

## Decision

- `applicant_count`, `waitlist_count` → **`0`** (사람 수는 `"-"` 여도 실질 0명)
- `capacity` → **`null`** (무제한 또는 미정. 정원 0명과 구별된다)

## Alternatives Considered

### 대안 1: 세 필드 전부 `0`

- **Pros**: 스키마가 단순. 앱에 null 가드가 전혀 필요 없음
- **Cons**: "정원 0명"과 "정원 미정"이 구별되지 않음
- **Why not**: 앱이 `applicant_count/capacity` 로 임박률을 계산할 때
  `0/0` 을 만나 마감으로 오인한다. 상시모집 공고가 마감으로 표시된다

### 대안 2: 세 필드 전부 `int | null`

- **Pros**: 데이터에 없는 값을 없다고 정직하게 표현
- **Cons**: 앱의 모든 산술에 null 가드가 필요
- **Why not**: 사람 수는 `"-"` 여도 의미가 명확히 "0명"이다.
  없는 정보가 아니라 0을 다르게 표기한 것뿐인데 null 로 만들면 과하다

## Consequences

### Positive

- "정원 미정·무제한"과 "정원 0명"이 데이터 수준에서 구별된다
- 신청자·대기자 산술에는 null 가드가 필요 없다
- `int()` 변환 실패로 인한 예외가 사라진다

### Negative

- 앱은 `capacity` 에만 null 분기를 넣어야 한다
- 필드마다 규칙이 달라 "왜 이건 0이고 저건 null인가"를 알아야 한다.
  이 ADR 이 그 답이다

### Risks

- **실데이터로 검증되지 않았다.** 2026-07-28 실적재 33건 표본에
  `"-"` 정원이 0건이었다. `capacity → null` 경로는 단위 테스트로만 확인됐고
  실제로는 아직 한 번도 실행되지 않았다
- `capacity` 가 `null` 이면 앱은 정원 임박 판단 **자체를 하지 않아야** 한다.
  0으로 대체하면 대안 1 과 같은 오인이 발생한다

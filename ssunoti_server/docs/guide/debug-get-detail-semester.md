# get_detail 디버깅 기록: semester 파싱 실패

**발생일**: 2026-04-01  
**관련 파일**: `src/ssunoti/crawler.py`, `tests/test_notices.py`

---

## 문제 증상

`pytest tests/test_notices.py::TestGetDetail::test_semester_structure` 실패.

```
AssertionError: assert isinstance(0, int) is True
```

`semester['year']` 가 0으로 반환됨 — `_parse_semester` 내부에서 정규식 매칭 실패 시 `{"year": 0, "term": 0}` 을 반환하는 기본값이 그대로 노출된 상태.

---

## 원인 분석

### 디버깅 방법

`_build_field_map` 의 실제 키 목록을 확인하기 위해 `get_detail` 내부에 임시 출력을 추가했다.

```python
field_map = self._build_field_map(tbody)
print(f"[DEBUG] field_map keys: {list(field_map.keys())}")
```

`pytest -s` 로 실행하면 캡처 없이 표준 출력이 보인다.

```
[DEBUG] field_map keys: ['프로그램명', '운영조직', '담당자 이메일', '담당자 연락처',
  '프로그램 유형', '운영년도/학기', '카테고리', '프로그램 형식', '모집상태',
  '운영방법', '신청 방법', '신청 기간', '선발방법', '신청대상', '신청신분',
  '신청대상 상세', '모집정원', '대기정원', '첨부파일', '수료증 발급', '마일리지']
```

실제 키와 코드에서 사용한 키를 비교하니 두 가지 불일치가 발견되었다.

---

## 버그 1 — 필드 키 공백 불일치

### 원인

HTML `<th scope="row">` 안의 텍스트가 `"신청 기간"` (중간에 공백 포함) 인데, 코드에서는 `"신청기간"` (공백 없음) 으로 조회하고 있었다.

```python
# 잘못된 코드
application_period = self._parse_period(self._td_text(field_map, '신청기간'))
```

`_td_text` 는 키가 없으면 `""` 를 반환하므로 조용히 빈 값이 됐고, semester 파싱에 빈 문자열이 들어가 `{"year": 0, "term": 0}` 을 반환했다.

### HTML 원문

```html
<th scope="row">신청 기간</th>
<td>2026.03.27 00:00 ~ 2026.04.03 00:00</td>
```

### 수정

```python
# 수정된 코드
application_period = self._parse_period(self._td_text(field_map, '신청 기간'))
```

---

## 버그 2 — _parse_semester 정규식 공백 미처리

### 원인

HTML의 학기 문자열이 `"2026년 1학기"` 처럼 `년` 뒤에 공백이 있는데, 정규식에 `\s*` 가 없어서 매칭 실패했다.

```python
# 잘못된 코드
match = re.search(r'(\d{4})[년/](\d+)', semester_str)
```

`[년/]` 는 단일 문자 클래스이므로 `년` 다음에 오는 공백을 소비하지 않는다. `(\d+)` 가 공백 바로 다음 숫자와 붙지 않아 매칭 실패 → `match` 가 `None` → `{"year": 0, "term": 0}` 반환.

### HTML 원문

```html
<th scope="row">운영년도/학기</th>
<td>2026년 1학기</td>
```

### 수정

```python
# 수정된 코드 — \s* 추가로 '년 1학기' 형태도 매칭
match = re.search(r'(\d{4})[년/]\s*(\d+)', semester_str)
```

---

## 교훈

| 항목 | 내용 |
|---|---|
| `_td_text` 의 빈 문자열 반환 | 키 오탈자를 조용히 감춰서 디버깅을 어렵게 만든다. 실제 키를 출력해 비교하는 것이 가장 빠른 진단 방법이다. |
| HTML 텍스트의 공백 | `th` 텍스트에 포함된 공백은 눈으로 구분하기 어렵다. `_build_field_map` 에서 `strip()` 은 하지만 내부 공백은 그대로 유지되므로, HTML 원문과 정확히 일치시켜야 한다. |
| 정규식 문자 클래스 | `[년/]` 는 `년` 또는 `/` 한 글자만 매칭한다. 뒤따르는 공백을 처리하려면 `\s*` 를 추가해야 한다. |
| 디버그 프린트 위치 | `field_map.keys()` 출력은 `get_detail` 내부가 아닌 테스트 픽스처나 별도 스크립트에서 하는 것이 좋다. 크롤러 본체에 디버그 코드를 남기지 말 것. |

---

## 최종 수정일

2026-04-01

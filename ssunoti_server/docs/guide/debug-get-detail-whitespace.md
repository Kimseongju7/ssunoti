# get_detail 디버깅 기록: 공백/이상 문자 정규화

**발생일**: 2026-04-01  
**관련 파일**: `src/ssunoti/crawler.py`

---

## 발견 경위

PTKOREA 채용설명회 공고 상세를 `pprint` 로 출력하여 다음 이상 사항 발견:

```python
'program_type': '진로취업지원\n\t\t\t\t\t/\n\t\t\t\t\tSCLP+UP'
'application_period': {'start': '', 'end': ''}
'target_detail': {'학적': '전체', '구분': '전체', '학 년': '전체', '학위': '전체'}
'summary': 'PT코리아 채용설명회를 통해 기업에 대한 이해와 취업준비 역량을  강화시킴'
```

---

## 버그 1 — `program_type` 에 `\n\t` 노이즈

### 원인

HTML `<td>` 에 멀티라인 텍스트가 들어있는 경우:

```html
<td colspan="3">
    진로취업지원
    /
    SCLP+UP
</td>
```

`get_text(separator='\n', strip=True)` 는 각 NavigableString 의 **앞뒤만** `strip()` 합니다.  
단일 텍스트 노드 내부의 `\n\t\t\t\t\t` 는 leading/trailing 이 아니므로 그대로 남습니다.

```python
'\n\t\t\t\t\t진로취업지원\n\t\t\t\t\t/\n\t\t\t\t\tSCLP+UP'.strip()
# → '진로취업지원\n\t\t\t\t\t/\n\t\t\t\t\tSCLP+UP'  ← 내부 탭 유지
```

### 수정

`_td_text` 에서 줄 단위 정규화 추가:

```python
# 수정 전
return td.get_text(separator='\n', strip=True) if td else ''

# 수정 후
text = td.get_text(separator='\n', strip=True).replace('\xa0', ' ')
lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
return ' '.join(lines)
```

결과: `'진로취업지원 / SCLP+UP'`

---

## 버그 2 — `application_period` 빈값

### 원인

`_build_field_map` 은 `<th scope="row">` 텍스트를 그대로 키로 사용했습니다.  
공고마다 HTML 작성 방식이 다릅니다:

| 공고 | `<th>` 텍스트 | 코드의 조회 키 | 결과 |
|---|---|---|---|
| 문예창작전공 강연회 | `'신청 기간'` | `'신청 기간'` | 매칭 ✓ |
| PTKOREA 채용설명회 | `'신청기간'` | `'신청 기간'` | **미매칭 → 빈값** |

```python
# 코드가 '신청 기간' 으로 조회하지만 HTML 키는 '신청기간'
application_period = self._parse_period(self._td_text(field_map, '신청 기간'))
# → _td_text 반환 '' → _parse_period('') → {'start': '', 'end': ''}
```

### 수정

`_build_field_map` 에서 키의 내부 공백을 모두 제거하여 정규화:

```python
# 수정 전
field_map[th.get_text(strip=True)] = td

# 수정 후
key = ''.join(th.get_text(strip=True).split())  # 내부 공백 전부 제거
field_map[key] = td
```

그 후 모든 키 조회를 정규화된 버전으로 일괄 업데이트:

| 수정 전 | 수정 후 |
|---|---|
| `'담당자 이메일'` | `'담당자이메일'` |
| `'담당자 번호'` | `'담당자번호'` |
| `'프로그램 유형'` | `'프로그램유형'` |
| `'프로그램 분류'` | `'프로그램분류'` |
| `'프로그램 형식'` | `'프로그램형식'` |
| `'프로그램 목표'` | `'프로그램목표'` |
| `'프로그램 한줄 소개'` | `'프로그램한줄소개'` |
| `'신청 기간'` | `'신청기간'` |
| `'학생 신청대상 상세정보'` | `'학생신청대상상세정보'` |
| `'이수 인증서'` | `'이수인증서'` |
| `'지급 마일리지'` | `'지급마일리지'` |
| `'핵심역량 비중도'` | `'핵심역량비중도'` |
| `'프로그램 주요내용'` | `'프로그램주요내용'` |

---

## 버그 3 — `target_detail` 키 공백

### 원인

`target_detail` 은 `_build_field_map` 을 거치지 않고 `<dt>` 텍스트를 직접 키로 사용합니다.  
HTML 작성 방식에 따라 `'학년:'` 이 아닌 `'학 년:'` 처럼 공백이 섞일 수 있습니다.

```python
# 수정 전
key = dt.get_text(strip=True).rstrip(':')

# 수정 후 — 공백 제거 + 콜론 제거
key = ''.join(dt.get_text(strip=True).split()).rstrip(':')
```

dd 값도 `\xa0` 를 포함할 수 있어 동일하게 정규화:

```python
target_detail[key] = ' '.join(dd.get_text(strip=True).replace('\xa0', ' ').split())
```

---

## 버그 4 — `summary` 이중 공백 / `application_period` 의 `&nbsp;`

### 원인

HTML `&nbsp;` 엔티티는 BeautifulSoup 에서 `\xa0`(유니코드 U+00A0, non-breaking space) 로 변환됩니다.  
Python `str.strip()` 은 ASCII 공백만 제거하므로 `\xa0` 는 그대로 남습니다.

```python
'역량을\xa0강화시킴'.strip()  # → '역량을\xa0강화시킴'  (제거 안 됨)
```

기간 문자열에서는 `&nbsp;~&nbsp;` 패턴이 `\xa0~\xa0` 이 되어 `.strip()` 후에도 `\xa0` 가 남습니다.

### 수정

**`_td_text`**: 텍스트 추출 직후 `\xa0 → ' '` 변환 추가 (이중 공백도 `' '.join(line.split())` 으로 정규화됨)

**`_parse_period`**: `_td_text` 를 거치지 않는 경로(list page, session 파싱)를 위해 직접 처리:

```python
# 수정 전
if '~' in period_str:
    start, end = period_str.split('~', 1)
    return {'start': start.strip(), 'end': end.strip()}

# 수정 후
clean = period_str.replace('\xa0', ' ').strip()
if '~' in clean:
    start, end = clean.split('~', 1)
    return {'start': start.strip(), 'end': end.strip()}
```

---

## 교훈

| 항목 | 내용 |
|---|---|
| `str.strip()` 의 한계 | ASCII 공백만 제거. `\xa0`(`&nbsp;`) 는 반드시 `replace('\xa0', ' ')` 로 따로 처리해야 한다. |
| 줄 내부 공백 제거 | `get_text(strip=True)` 는 각 노드의 앞뒤만 정리한다. 노드 내부 `\n\t` 제거는 줄 단위 재처리가 필요하다. |
| HTML 키 불일치 | 같은 의미의 필드라도 HTML 작성자마다 공백 유무가 다를 수 있다. `''.join(text.split())` 으로 정규화하면 방어할 수 있다. |
| 정규화 계층 | `_td_text` 에서 정규화하면 하위 파싱 메서드가 깨끗한 입력을 받는다. 단, `_td_text` 를 거치지 않는 경로(list page, session)는 별도 처리가 필요하다. |

---

## 최종 수정일

2026-04-01

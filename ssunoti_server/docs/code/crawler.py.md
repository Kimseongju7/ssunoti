# crawler.py

## 목적

SSUPath(숭실대 비교과 포털) 웹사이트에 SSO 로그인 후 공고 목록과 상세 정보를 크롤링하는 핵심 모듈.
HTTP 세션을 유지한 채 데이터를 수집하고, 파싱 결과를 딕셔너리 리스트로 반환하여 Firebase 저장 레이어와 분리된 책임을 가진다.

---

## 개요

`SsupathCrawler` 클래스 하나와 `NoDataError` 예외 클래스로 구성되며, 아래 흐름으로 동작한다:

```
login() → get_all_notices(year, status, semester)
               └─ get_current_page_notices(url) × N페이지
                       └─ _parse_notice(li)
                                                  ↓
          [get_notice_url()] → get_detail()   dict 리스트 반환
```

크롤러는 **데이터 수집과 파싱만** 담당한다. Firestore 저장, 날짜 변환, 알림 발송은 별도 모듈에서 처리한다.

---

## 주요 구성요소

### 클래스 상수

| 상수 | 값 | 설명 |
|---|---|---|
| `SSO_LOGIN_PAGE` | `smartid.ssu.ac.kr/smln.asp` | SSO 로그인 페이지 |
| `SSO_LOGIN_PROCESS` | `smartid.ssu.ac.kr/smln_pcs.asp` | SSO 로그인 처리 엔드포인트 |
| `API_RETURN_URL` | `path.ssu.ac.kr/loginProc.do?...` | SSO 인증 후 리다이렉트 URL |
| `SSUPATH_URL` | `path.ssu.ac.kr/.../findIcmpNsbjtPgmList.do` | 공고 목록 페이지 |
| `DETAIL_URL` | `path.ssu.ac.kr/.../findIcmpNsbjtPgmInfo.do` | 공고 상세 페이지 |
| `BASE_URL` | `https://path.ssu.ac.kr` | 상대 URL → 절대 URL 변환용 |

---

### `NoDataError(Exception)`

공고 목록 페이지에 조회된 데이터가 없을 때 발생하는 예외 클래스.

`get_current_page_notices()` 가 `li.NO_RESULT` 를 감지하면 이 예외를 발생시킨다.  
`get_all_notices()` 는 이 예외를 포착하여 페이지 순회를 종료하는 종료 신호로 사용한다.

```python
# 직접 사용 시
from ssunoti.crawler import NoDataError

try:
    notices = crawler.get_current_page_notices(url)
except NoDataError:
    print("더 이상 데이터가 없습니다")
```

---

### `login() → bool`

SSU 통합 로그인(SSO) 3단계를 수행한다.

**로그인 플로우:**

```
1. GET smln.asp?apiReturnUrl=...
   → ASPSESSIONID 쿠키 발급 (smartid.ssu.ac.kr 세션 시작)

2. POST smln_pcs.asp  (userid, pwd)
   → sToken 쿠키 발급
   → 응답 body의 JS에서 리다이렉트 URL 파싱
     예: parent.location.href = 'https://path.ssu.ac.kr/loginProc.do?...'

3. GET loginProc.do (sToken 포함)
   → JSESSIONID 쿠키 발급 (path.ssu.ac.kr 세션 완성)
```

**반환값**: `True` (JSESSIONID 발급 성공) / `False` (리다이렉트 URL 파싱 실패)

> `requests.Session`이 쿠키를 자동 관리하므로 3단계 이후 별도 쿠키 처리가 필요 없다.

---

### `get_current_page_notices(url=None) → list[dict]`

공고 목록 페이지 한 장을 요청하고 각 공고를 딕셔너리로 파싱하여 반환한다.

**파라미터:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `url` | `str \| None` | `None` | 요청할 목록 URL. `None` 이면 `SSUPATH_URL` 사용 |

**예외:**

- `NoDataError`: 페이지에 `li.NO_RESULT` 가 있으면 발생 (데이터 없음)

> 직접 사용: 특정 필터 URL의 단일 페이지 내용만 필요할 때  
> 간접 사용: `get_all_notices()` 가 내부에서 페이지별 URL을 넘기며 호출

**반환 딕셔너리 구조:**

| 키 | 타입 | 예시 |
|---|---|---|
| `notice_id` | `str` | `"63c64f19a5f1916fe434bc109041961f"` |
| `status` | `str` | `"모집중"` / `"모집대기"` / `"종료"` |
| `organizer` | `str` | `"교수학습혁신팀"` |
| `program_format` | `str` | `"비교과 (비학점)"` |
| `title` | `str` | `"2026-1학기 자기주도학습챌린지 <러닝러닝>"` |
| `summary` | `str` | `"내가 직접 짠 학습(Learning) 코스로..."` |
| `application_period` | `dict` | `{"start": "2026.03.27 00:00", "end": "2026.04.03 00:00"}` |
| `education_period` | `dict` | `{"start": "2026.04.06 00:00", "end": "2026.06.30 23:59"}` |
| `target` | `str` | `"숭실대학교"` |
| `target_status` | `str` | `"학생"` / `"학생, 일반인"` / `"전체"` |
| `mileage` | `int` | `160` |
| `applicant_count` | `int` | `52` |
| `waitlist_count` | `int` | `0` |
| `capacity` | `int` | `100` |
| `competency_tags` | `list[str]` | `["리더십", "창의", "융합"]` |
| `poster_url` | `str` | `"https://path.ssu.ac.kr/common/cmnFile/..."` |
| `source_url` | `str` | `"https://path.ssu.ac.kr/.../findIcmpNsbjtPgmList.do"` |

> HTML 구조 상세는 `docs/code/notice_list_html_structure.md` 참고

---

### `_parse_notice(li) → dict` *(private)*

`get_current_page_notices()`에서 호출하는 내부 메서드. BeautifulSoup `Tag` 하나를 받아 딕셔너리로 변환한다.

---

### `_parse_period(period_str) → dict` *(private)*

기간 문자열을 `{"start": ..., "end": ...}` 딕셔너리로 변환한다.

```python
_parse_period("2026.03.27 00:00~2026.04.03 00:00")
# → {"start": "2026.03.27 00:00", "end": "2026.04.03 00:00"}

_parse_period("")
# → {"start": "", "end": ""}
```

---

### `get_notice_url(notice) → str`

공고 딕셔너리의 `notice_id`를 이용해 상세 페이지 URL을 생성한다.

```python
url = crawler.get_notice_url(notices[0])
# → "https://path.ssu.ac.kr/.../findIcmpNsbjtPgmInfo.do?encSddpbSeq=63c64f..."
```

---

### `get_all_notices(year=None, status='0000', semester='0000') → list[dict]`

페이지를 순회하면서 조건에 맞는 모든 공고를 수집하여 반환한다.

내부에서 `get_current_page_notices(url)` 를 반복 호출하며, `NoDataError` 가 발생하면 순회를 종료한다.

**파라미터:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `year` | `int \| None` | `None` | 운영년도. `None` 이면 현재 연도(`datetime.now().year`) 사용 |
| `status` | `str` | `'0000'` | 모집 상태 코드 (아래 표 참고) |
| `semester` | `str` | `'0000'` | 학기 코드 (아래 표 참고) |

**status 코드:**

| 코드 | 설명 |
|---|---|
| `'0000'` | 전체 (기본값) |
| `'RS01'` | 모집대기 |
| `'RS02'` | 모집중 |
| `'RS03'` | 종료 |

**semester 코드:**

| 코드 | 설명 |
|---|---|
| `'0000'` | 전체 (기본값) |
| `'0001'` | 1학기 |
| `'0003'` | 2학기 |

**사용 예:**

```python
# 2026년 모집중 공고 전체 수집
notices = crawler.get_all_notices(year=2026, status='RS02')

# 2025년 전체 공고 수집
notices = crawler.get_all_notices(year=2025)

# 현재 연도 1학기 공고 수집
notices = crawler.get_all_notices(semester='0001')
```

---

### `get_detail(url) → dict`

공고 상세 페이지를 파싱하여 상세 정보 딕셔너리를 반환한다.

**반환 딕셔너리 구조:**

| 키 | 타입 | 예시 |
|---|---|---|
| `title` | `str` | `"2026-1학기 자기주도학습챌린지 <러닝러닝>"` |
| `organizer` | `str` | `"교수학습혁신팀"` |
| `manager_email` | `str` | `"gjshim@ssu.ac.kr"` |
| `manager_phone` | `str` | `"02-828-7132"` |
| `program_type` | `str` | `"학습역량강화 / 학습지원프로그램"` |
| `semester` | `dict` | `{"year": 2026, "term": 1}` |
| `category` | `str` | `"기타"` / `"특강/워크숍"` |
| `program_format` | `str` | `"비교과 (비학점)"` |
| `goal` | `str` | 긴 텍스트 |
| `summary` | `str` | `"내가 직접 짠 학습(Learning) 코스로..."` |
| `operation_method` | `str` | `"대면/비대면 혼합"` |
| `application_method` | `str` | `"내부"` |
| `application_period` | `dict` | `{"start": "2026.03.27 00:00", "end": "2026.04.03 00:00"}` |
| `selection_method` | `str` | `"직접선발"` / `"선착순선발"` |
| `target` | `str` | `"숭실대학교"` |
| `target_status` | `str` | `"학생"` |
| `target_detail` | `dict` | `{"학적": "재학", "구분": "대학", "학년": "1학년, 2학년..."}` |
| `capacity` | `int` | `100` |
| `waitlist_capacity` | `int` | `100` |
| `attachments` | `list[dict]` | `[{"name": "안내문.hwp", "url": "https://..."}]` |
| `has_certificate` | `bool` | `True` |
| `mileage` | `int` | `160` |
| `core_competencies` | `list[dict]` | `[{"keyword": "리더십역량", "ratio": 50}, ...]` |
| `main_content` | `str` | plain text (CKEditor 내용) |
| `course_info` | `dict` | `{"semester": "2026/1학기", "has_attendance": True, "progress_type": "일정기간 참여"}` |
| `sessions` | `list[dict]` | 회차별 정보 리스트 (아래 참고) |
| `source_url` | `str` | 상세 페이지 URL |

**`sessions` 항목 구조:**

| 키 | 타입 | 예시 |
|---|---|---|
| `session_no` | `int` | `1` |
| `class_name` | `str` | `"2026-1 러닝러닝 4월 학습..."` |
| `education_period` | `dict` | `{"start": "2026.04.06 00:00", "end": "2026.04.30 23:59"}` |
| `location` | `str` | `""` (비어있을 수 있음) |
| `instructor` | `str` | `""` (비어있을 수 있음) |
| `attachments` | `list[dict]` | 파일 목록 |
| `has_assignment` | `bool` | `True` |
| `assignment_period` | `dict` | `{"start": "2026.04.27 00:00", "end": "2026.05.04 00:00"}` |

> HTML 구조 상세는 `docs/code/notice_detail_html_structure.md` 참고

---

### 내부 헬퍼 메서드 *(private)*

| 메서드 | 역할 |
|---|---|
| `_build_field_map(tbody)` | `th[scope=row]` → 다음 `td` 매핑 딕셔너리 생성 |
| `_td_text(field_map, key)` | field_map에서 텍스트 추출, 없으면 `""` |
| `_parse_semester(str)` | `"2026년 1학기"` → `{"year": 2026, "term": 1}` |
| `_parse_attachments(td)` | `ul.cmnFileLst li a` → `[{"name", "url"}]` |
| `_parse_course_info(block)` | 강좌 기본정보 블록 파싱 |
| `_parse_session(block)` | 회차 블록 파싱 |

---

## 의존성

### 이 파일이 의존하는 것

| 모듈 | 용도 |
|---|---|
| `requests` | HTTP 세션 관리 및 요청 |
| `bs4 (BeautifulSoup)` | HTML 파싱 |
| `dotenv` | `.env` 파일에서 환경변수 로드 |
| `ssunoti.utils.build_url` | URL + query params 조합 |

### 환경변수 (`.env`)

| 변수명 | 설명 |
|---|---|
| `student_no` | SSU 학번 |
| `ssu_pw` | SSU 비밀번호 |
| `user_agent` | HTTP 요청에 사용할 User-Agent 문자열 |

### 이 파일에 의존하는 것

- `tests/test_login.py` — `login()` 단위 테스트
- `tests/test_notices.py` — `get_current_page_notices()`, `get_notice_url()` 테스트
- `tests/test_request.py` — 요청 관련 테스트
- `firebase_util.py` (예정) — 반환된 dict를 Firestore에 저장

---

## 사용 예시

```python
from ssunoti.crawler import SsupathCrawler

crawler = SsupathCrawler()

# 1. 로그인
success = crawler.login()
if not success:
    raise RuntimeError("로그인 실패")

# 2. 공고 목록 수집
notices = crawler.get_current_page_notices()

# 3. 각 공고의 상세 URL 생성
for notice in notices:
    print(notice['title'], notice['status'])
    detail_url = crawler.get_notice_url(notice)
    detail = crawler.get_detail(detail_url)
```

---

## 주의사항

- **세션 유지**: `requests.Session` 인스턴스를 재사용하므로, 인스턴스 하나당 하나의 로그인 세션만 유지된다. 병렬 크롤링 시 인스턴스를 분리해야 한다.
- **세션 만료**: 장시간 실행 시 JSESSIONID가 만료될 수 있다. 만료 시 목록 페이지 대신 로그인 페이지 HTML이 반환되며, `a.detailBtn`이 없어 빈 리스트가 반환된다. (TODO: 자동 재로그인 처리 필요)
- **날짜 형식**: 기간 필드는 `"2026.03.27 00:00"` 형태의 문자열로 반환된다. Firestore `Timestamp` 변환은 `firebase_util.py`에서 처리한다.
- **숫자 필드**: `mileage`, `applicant_count` 등은 `int()`로 변환하므로, 사이트 구조 변경으로 숫자가 아닌 값이 오면 예외가 발생한다. (TODO: 방어 처리 필요)
- **HTML 구조 변경**: SSUPath 사이트 업데이트 시 CSS 선택자가 깨질 수 있다. `div[class='lica_wrap']`은 정확한 클래스 일치 선택자이므로 클래스 추가 시 매칭 실패한다.

---

## 최종 수정일

2026-04-01 (get_all_notices 구현, NoDataError 추가)

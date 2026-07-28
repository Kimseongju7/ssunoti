# SSUNoti: 숭실대학교 비교과 공고 알리미

## 프로젝트 개요

SSUPath(숭실대 비교과 포털)의 공고를 주기적으로 크롤링하여 Firebase에 저장하고, Flutter 앱으로 알림을 제공하는 서비스.

---

## 전체 구조 (Monorepo)

```
ssunoti/                          # 프로젝트 루트 (git repo)
├── ssunoti_server/               # Python 백엔드 (현재 디렉토리)
└── ssunoti_flutter/              # Flutter 앱 (예정)
```

Firebase CLI 설정 파일(`firebase.json`, `.firebaserc`)은 **아직 존재하지 않는다.**
서버는 Firebase CLI 를 쓰지 않고 Admin SDK 만 사용하며, 인증은 환경변수
`GOOGLE_APPLICATION_CREDENTIALS` 가 가리키는 서비스 계정 키 파일로 한다
(`main.py` 의 `_init_firebase()`). 키 파일은 저장소에 커밋하지 않는다.
나중에 Firebase CLI 를 도입하면 그 설정 파일은 루트(`ssunoti/`)에서 관리한다.

---

## 시스템 아키텍처

```
[Python 크롤러] → [Cloud Firestore] ← [Flutter 앱]
                         ↓
                  [FCM 푸시 알림] → [Flutter 앱]
```

- **Python 백엔드**: SSUPath에서 공고 크롤링 → Firestore에 저장, 스케줄링
- **Firebase**: Firestore(데이터 저장), FCM(푸시 알림)
- **Flutter**: Firestore 실시간 리스닝, 푸시 알림 수신

---

## 현재 파일 구조 (ssunoti_server/)

```
ssunoti_server/
├── src/
│   └── ssunoti/
│       ├── __init__.py
│       ├── crawler.py              # SsupathCrawler (SSO 로그인, 목록/상세 크롤링)
│       ├── store.py                # NoticeStore — Firestore upsert 계층
│       ├── notifier.py             # NoticeNotifier — FCM 발송 + 신규 공고 사이클
│       ├── scheduler.py            # NoticeScheduler — 주기 잡 2종 + 초기 적재
│       └── utils.py                # build_url() URL 빌더 유틸
├── tests/
│   ├── conftest.py                 # pytest 터미널 요약 훅
│   ├── test_login.py               # 로그인 테스트 (실제 SSUPath 접속)
│   ├── test_notices.py             # 단일 페이지 공고 목록·상세 파싱 테스트 (실제 접속)
│   ├── test_all_notices.py         # 전체 공고 수집(페이지 순회) 테스트 (실제 접속)
│   ├── test_request.py             # 요청 관련 테스트 (실제 접속)
│   ├── test_notice_id_stability.py # encSddpbSeq 세션 간 안정성 (기본은 무부하·오프라인)
│   ├── test_store.py               # NoticeStore 단위 테스트 (fake Firestore)
│   ├── test_backfill.py            # 초기 적재 모드 테스트 (fake Firestore + FCM mock)
│   ├── test_notifier.py            # FCM 발송·at-least-once 테스트 (FCM mock)
│   └── test_scheduler.py           # 잡 등록·트리거 설정 테스트
├── docs/
│   ├── code/
│   │   ├── crawler.py.md           # SsupathCrawler 코드 문서
│   │   ├── notice_list_html_structure.md   # 공고 목록 HTML 구조
│   │   └── notice_detail_html_structure.md # 공고 상세 HTML 구조
│   └── guide/
│       ├── beautifulsoup.md
│       ├── requests-guide.md
│       ├── pytest_guide.md
│       ├── ssu-sso-login-with-requests.md
│       ├── ssu-path-request-headers.md
│       ├── debug-get-detail-semester.md    # 학기 파싱 버그 디버깅 기록
│       └── debug-get-detail-whitespace.md  # 공백/\xa0 정규화 디버깅 기록
├── html/                           # 파싱 개발용 오프라인 HTML 샘플
│   ├── notice_list.html
│   ├── notice_detail.html
│   ├── notice_detail2.html
│   ├── end_page_html.html
│   └── ptkorea.html
├── main.py                         # 진입점 — --backfill 1회 적재 / 기본은 상주 실행
├── pyproject.toml                  # 패키지 빌드 설정 · 의존성 선언(의도)
├── uv.lock                         # uv 잠금 파일 · 정확한 버전 고정(확정) - 커밋 대상
├── .env                            # 환경변수 (student_no, ssu_pw, user_agent) - git 제외
└── .gitignore
```

---

## 구현 현황

### 완료 — 크롤러
- `SsupathCrawler.login()` — SSU SSO 3단계 로그인 (ASPSESSIONID → sToken → JSESSIONID)
- `SsupathCrawler.is_session_valid()` — 세션 유효성 확인 (div.lica_wrap 감지)
- `SsupathCrawler.get_all_notices(year, status, semester)` — 페이지 순회 전체 공고 수집
- `SsupathCrawler.get_current_page_notices(url)` — 단일 페이지 공고 목록 파싱, NoDataError
- `SsupathCrawler.get_notice_url(notice)` — 공고 상세 URL 생성
- `SsupathCrawler.get_detail(url)` — 공고 상세 페이지 파싱 (27개 필드)
- `build_url()` — URL + query params 조합 유틸

### 완료 — 서버 파이프라인
- `NoticeStore.upsert() / upsert_many()` (`store.py`) — `set(merge=True)` upsert,
  docId=`notice_id`, `created_at` 최초 1회만 기록, 비숫자 값 정규화
- `NoticeNotifier.process_new_notices()` (`notifier.py`) — 신규 판정 → FCM topic
  브로드캐스트 → Firestore 쓰기. `backfill=True` 시 발송 없이 저장만
- `NoticeScheduler.setup()` (`scheduler.py`) — apscheduler 잡 2종 등록, `max_instances=1`
- `NoticeScheduler.run_backfill()` — 초기 적재 1회 (주기 잡 아님, 예외 전파)
- `main.py` — Firebase 초기화 + `--backfill` 1회 적재 / 기본은 스케줄러 상주 실행

### 검증 완료
- `encSddpbSeq` 가 로그인 세션 간에 동일함을 실측 확인 (불일치 0건).
  `notice_id` 를 Firestore docId 로 쓰는 전략이 유효하다.
  근거: `docs/ac1_notice_id_stability.md`

### 해결된 문제 (기록)

- **backfill 진입점 부재** → `main.py --backfill` 과 `NoticeScheduler.run_backfill()` 추가.
  초기 적재는 주기 잡이 아니며, 실패 시 예외를 삼키지 않고 전파한다
  (부분 적재 상태로 상주 실행에 들어가면 남은 공고가 전량 푸시되므로).
- **`update_capacity` / `update_deadline` 중복** → 마감 전용 cron 잡을 제거하고
  15분 잡을 `update_notices` 로 통합. 잡 3개 → 2개, 시간당 크롤링 5회 유지.

### 남은 부하 이슈 (판단 보류)

15분 잡이 전수 페이지를 순회하므로 시간당 전수 크롤링이 5회 발생한다.
"신규 수집 주기 1시간 이상" 이라는 부하 배려 제약과 긴장 관계에 있다.
현재 15분 신선도를 실제로 쓰는 소비자는 없다 — 정원 임박 알림이 찜 기능 종속으로
범위 밖이기 때문이다. 찜 기능을 설계할 때 이 주기를 함께 재검토한다.

### 미구현
- Flutter 앱 일체
- 찜(favorites) 기능 및 그에 종속된 알림 (정원 임박 / 마감 임박)
- 오라클 클라우드 VM 배포 · 재부팅 시 자동 기동

---

## Firestore 데이터 설계

- **Collection**: `notices`
- **Document ID**: `{notice_id}` — 상세 URL 쿼리 `encSddpbSeq` (32자 hex).
  세션 간 안정성은 실측으로 검증됨.

### 필드 (9개, 이게 전부다)

| 필드 | 타입 | 비고 |
|---|---|---|
| `notice_id` | string | docId 와 동일 값 |
| `title` | string | |
| `url` | string | 상세 URL |
| `content` | string | 크롤러 `summary` |
| `deadline` | timestamp \| null | `application_period.end` 원시값. 파싱 형식 `%Y.%m.%d %H:%M` / `%Y.%m.%d` |
| `applicant_count` | int | 비숫자 입력(`"-"` 등) → `0` |
| `waitlist_count` | int | 비숫자 입력 → `0` |
| `capacity` | int \| null | 비숫자 입력 → `null` (무제한·미정). **0명 정원과 구별된다** |
| `created_at` | timestamp | 문서 최초 생성 시에만 기록. 재수집 시 보존 |

### 확정된 설계 결정 (되돌리지 말 것)

- **파생 상태를 저장하지 않는다.** `is_closing_soon`, `notified_deadline`,
  `current_capacity`, `total_capacity` 같은 필드는 **의도적으로 없앴다.**
  SSUPath 에는 취소 기능이 없고 정원은 증원될 수 있으며 마감은 연장될 수 있다.
  그래서 한 번 계산해 박아둔(래치된) 플래그는 반드시 상한다.
  임박 여부는 원시값을 읽는 쪽(Flutter 앱)이 조회 시점에 계산한다.
- **`capacity` 가 `null` 이면 정원 임박 판단 자체를 하지 않는다.**
- **문서의 존재 = 이미 관측되고 알림 처리된 공고.**
  별도의 seen/notified 상태를 두지 않으므로 존재 여부가 유일한 신규 판별 근거다.
  따라서 **문서 쓰기는 FCM 발송 성공 이후에만 일어난다** (`notifier.py`).
  중간에 죽으면 다음 사이클에서 재발송된다 — 중복은 허용, 유실은 불허(at-least-once).

> `docs/firestroe_design.md` 는 위 결정 이전에 작성된 옛 설계 문서다.
> 필드명이 어긋나 있으므로 이 섹션을 정본으로 본다.

---

## 주요 기술 스택

| 구분 | 기술 |
|---|---|
| 언어 | Python (`requires-python >= 3.10`) |
| 패키지·환경 관리 | `uv` (`uv.lock` 으로 버전 고정) |
| 크롤링 | `requests`, `BeautifulSoup4` |
| Firebase | `firebase-admin` |
| 스케줄링 | `APScheduler` (`>=3.6.0,<4.0.0`) |
| 테스트 | `pytest` (`dev` extra) |
| 환경변수 | `python-dotenv` |

---

## 환경변수 (.env)

```
student_no=학번
ssu_pw=비밀번호
user_agent=브라우저 User-Agent
```

Firebase 인증은 `.env` 가 아니라 프로세스 환경변수로 주입한다:

```
GOOGLE_APPLICATION_CREDENTIALS=<서비스 계정 키 JSON 파일의 절대 경로>
```

키 파일은 저장소에 커밋하지 않는다(`config/serviceAccountKey.json` 은 `.gitignore` 대상).

---

## 주기적 작업 (`scheduler.py`, 구현 완료)

수집 범위는 모든 잡에서 **현재 연도 + `status='RS02'`(모집중)** 로 한정한다.
잡 실행 전 `is_session_valid()` 로 세션을 확인하고, 만료 시 재로그인한다.

| 잡 ID | 트리거 | 하는 일 |
|---|---|---|
| `collect_new_notices` | interval 60분 | 신규 판정 → **FCM 발송 → Firestore 쓰기** |
| `update_notices` | interval 15분 | 전체 재수집 후 `upsert_many()` — 신청자·대기자·정원·**마감** 원시값 갱신 |

모든 잡은 `max_instances=1` — 이전 실행이 안 끝났으면 다음 트리거를 건너뛴다.
학교 서버 부하는 시간당 전수 페이지 순회 5회(15분×4 + 60분×1)이다.

> 마감 전용 잡(cron 매일 09:00)은 **제거했다.** 15분 잡이 같은 크롤링 결과로
> `deadline` 까지 이미 갱신하므로, 코드가 한 글자도 다르지 않은 중복이었다.

초기 적재는 주기 잡이 아니다. `NoticeScheduler.run_backfill()` 을 CLI 로 1회 호출한다:

```bash
uv run python main.py --backfill   # 저장만, FCM 0건, 실행 후 종료
uv run python main.py              # 상주 실행
```

**빈 Firestore 로 처음 시작할 때는 반드시 `--backfill` 을 먼저 1회 실행한다.**
신규 판정 기준이 "문서가 존재하지 않음" 이므로, 건너뛰면 모집중 공고 전량이
신규로 판정되어 전부 푸시가 나간다.

> 알림은 **신규 공고 1종만** 발송한다. 정원 임박·마감 임박 알림은 찜 기능에
> 종속되므로 Flutter 앱 구현 이후로 미뤘다. 옛 계획의 "90% 도달 시 알림" 은
> 현재 범위 밖이다.

FCM 은 **topic 브로드캐스트만** 사용한다 (`notifier.py`):

- topic 이름: `new_notices` — Flutter 앱이 이 topic 을 구독해야 한다.
- 기기 토큰을 수집하지도, payload 에 포함하지도 않는다. 사용자별 발송 경로가 없다.


---

## 개발 환경

- IDE: PyCharm
- 패키지·가상환경: **`uv` 로 통일**. `.venv/` 는 `uv` 가 관리하므로 직접 만들거나
  `pip install` 하지 않는다. `uv.lock` 이 정본이며 커밋한다.

```bash
cd ssunoti_server

uv sync --extra dev          # .venv 생성·동기화 (개발 의존성 포함)
uv run pytest tests/         # 테스트 실행 (activate 불필요)
uv add <패키지>              # 의존성 추가 (pyproject.toml + uv.lock 동시 갱신)
uv lock --upgrade            # 잠긴 버전 갱신
```

- `activate` 는 필요 없다. `uv run` 이 알아서 프로젝트 환경에서 실행한다.
- **`python -m pytest` 로 적지 않는다.** 이 개발 환경에는 `python` 이 없고 `python3` 만
  있으며(PEP 394), 게다가 어느 인터프리터인지 activate 여부에 따라 달라진다.
  자동화된 검증 명령에는 해석이 하나뿐인 `uv run pytest` 를 쓴다.

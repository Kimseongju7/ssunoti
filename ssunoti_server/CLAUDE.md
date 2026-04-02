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

Firebase 설정(`firebase.json`, `.firebaserc`)은 루트(`ssunoti/`)에서 관리.

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
│       └── utils.py                # build_url() URL 빌더 유틸
├── tests/
│   ├── test_login.py               # 로그인 테스트
│   ├── test_notices.py             # 단일 페이지 공고 목록·상세 파싱 테스트
│   ├── test_all_notices.py         # 전체 공고 수집(페이지 순회) 테스트
│   └── test_request.py             # 요청 관련 테스트
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
├── main.py                         # 진입점 (미구현)
├── pyproject.toml                  # 패키지 빌드 설정
├── .env                            # 환경변수 (student_no, ssu_pw, user_agent) - git 제외
└── .gitignore
```

---

## 구현 현황

### 완료
- `SsupathCrawler.login()` — SSU SSO 3단계 로그인 (ASPSESSIONID → sToken → JSESSIONID)
- `SsupathCrawler.is_session_valid()` — 세션 유효성 확인 (div.lica_wrap 감지)
- `SsupathCrawler.get_all_notices(year, status, semester)` — 페이지 순회 전체 공고 수집
- `SsupathCrawler.get_current_page_notices(url)` — 단일 페이지 공고 목록 파싱, NoDataError
- `SsupathCrawler.get_notice_url(notice)` — 공고 상세 URL 생성
- `SsupathCrawler.get_detail(url)` — 공고 상세 페이지 파싱 (27개 필드)
- `build_url()` — URL + query params 조합 유틸

### 미구현
- Firebase Admin SDK 연동 (`firebase-admin`)
- 스케줄러 (`apscheduler`)
- FCM 푸시 알림 발송
- `main.py` 진입점

---

## Firestore 데이터 설계

- **Collection**: `notices`
- **Document ID**: `{notice_id}` (SSUPath 게시글 번호, 중복 방지)
- **Fields**: `title`, `url`, `content`, `deadline` (Timestamp), `current_capacity`, `total_capacity`, `is_closing_soon`, `notified_deadline`, `created_at`

자세한 설계: `docs/firestroe_design.md`

---

## 주요 기술 스택

| 구분 | 기술 |
|---|---|
| 언어 | Python 3.x |
| 크롤링 | `requests`, `BeautifulSoup4` |
| Firebase | `firebase-admin` (예정) |
| 스케줄링 | `apscheduler` (예정) |
| 테스트 | `pytest` |
| 환경변수 | `python-dotenv` |

---

## 환경변수 (.env)

```
student_no=학번
ssu_pw=비밀번호
user_agent=브라우저 User-Agent
```

---

## 주기적 작업 계획 (스케줄러 미구현)

1. **신규 공고 수집** (1시간 주기): 신규 ID 확인 → Firestore 저장 → FCM 알림
2. **인원 수 모니터링** (15분 주기): 접수 중 공고 순회 → 인원 업데이트 → 90% 도달 시 알림
3. **마감 기한 체크** (매일 오전): DB 조회 → 마감 임박 건 알림

---

## 개발 환경

- IDE: PyCharm
- 가상환경: `.venv/` (프로젝트 내 관리)
- 테스트 실행: `pytest tests/`

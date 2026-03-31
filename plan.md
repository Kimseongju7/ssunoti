🔔 SSUNoti: 숭실대학교 비교과 공고 알리미 프로젝트 기획서

🏗️ 1. 시스템 전체 구조 (System Architecture)
본 프로젝트는 로컬 서버(Python) + Firebase + Flutter의 하이브리드 구조를 채택합니다.

A. 로컬 서버 (Python & Crawler)

• 주요 기술: Python 3.10+, `requests`, `BeautifulSoup4`, `lxml`, `apscheduler`, `firebase-admin`

• 역할: SSU SSO 인증을 통해 세션을 유지한 채 SSUPath 데이터를 수집하고 Firebase로 전송

• 크롤링 전략: `undetected-chromedriver` 대신 `requests` 라이브러리로 HTTP 요청을 직접 처리.
  SSO 3단계 쿠키 흐름(ASPSESSIONID → sToken → JSESSIONID)을 구현하여 세션 인증 완성.

B. 클라우드 인프라 (Firebase)

• Cloud Firestore: NoSQL 데이터베이스. 공고 정보 및 실시간 인원 수 저장

• Firebase Cloud Messaging (FCM): 푸시 알림 전송 엔진

C. 프론트엔드 (Flutter)

• 주요 기술: Flutter, `cloud_firestore`, `firebase_messaging`

• 역할: 데이터 실시간 리스닝 및 UI 제공, 푸시 수신

📂 2. 상세 파일 구조
```
ssunoti-project/
├── ssunoti_app/              # Flutter Frontend
└── ssunoti_server/           # Local Python Server
    ├── .env                  # 환경 변수 (학번, 비밀번호, User-Agent)
    ├── pyproject.toml        # 패키지 빌드 설정
    ├── main.py               # 진입점 (미구현)
    ├── config/
    │   └── serviceAccountKey.json  # Firebase 관리자 키 (gitignore)
    ├── src/
    │   ├── utils.py                # URL 빌더 유틸
    │   ├── crawling/
    │   │   ├── __init__.py
    │   │   └── ssupath_crawling.py # SsupathCrawler 핵심 크롤러
    │   ├── firebase_util.py        # Firebase 연동 유틸 (예정)
    │   ├── main_scheduler.py       # 전체 작업 스케줄러 (예정)
    │   └── deadline_checker.py     # 마감 알림 로직 (예정)
    ├── tests/
    │   ├── test_login.py           # SSO 로그인 단위 테스트
    │   ├── test_request.py         # 요청/URL 통합 테스트
    │   └── test_notices.py         # 공고 파싱 단위 테스트
    └── docs/                       # 개발 참고 문서
```

🔐 3. SSO 로그인 플로우
requests.Session을 통해 쿠키를 자동 관리하며, 3단계로 SSU 통합 인증을 처리합니다.

1. GET smartid.ssu.ac.kr/smln.asp → ASPSESSIONID 쿠키 발급
2. POST smartid.ssu.ac.kr/smln_pcs.asp (학번/비밀번호) → sToken 발급 + JS 리다이렉트 URL 파싱
3. GET path.ssu.ac.kr/loginProc.do (sToken 포함) → JSESSIONID 발급 (세션 완성)

성공 여부는 JSESSIONID 쿠키 발급 여부로 판단합니다.

🔄 4. 핵심 주기적 작업 (Scheduled Tasks)
1. 신규 공고 수집 (1시간 주기): 신규 ID 확인 시 전체 파싱 후 저장 & 알림 발송

2. 인원 수 모니터링 (15분 주기): 접수 중인 공고 순회 → 인원 업데이트 → 90% 도달 시 알림

3. 마감 기한 체크 (매일 오전): DB 조회 후 마감 임박 건 알림 발송

💾 5. 데이터베이스 설계 (Firestore)
• Collection: `notices`

• Document ID: `{notice_id}` (SSUPath 게시글 번호 → encSddpbSeq 파라미터)

• Fields: title, url, content, deadline(Timestamp), current_capacity, total_capacity, is_closing_soon, notified_deadline, created_at

🚩 6. 핵심 로직
• 중복 방지: 문서 ID를 게시글 번호로 지정하여 `doc.exists`로 체크

• 인원 체크 최적화: requests.Session을 유지한 채 URL만 변경하여 속도 향상
  (build_url 유틸로 DETAIL_URL + encSddpbSeq 파라미터 조합)

• 푸시 타겟팅: 전체 알림용 Topic(`all_notices`) 구독 방식 사용

• URL 파싱 전략: 공고 li 태그의 a[data-params] JSON을 파싱하여 상세 URL 동적 생성

📌 7. 구현 현황
| 기능 | 상태 |
|---|---|
| SSU SSO 로그인 (requests 기반) | ✅ 완료 |
| 공고 목록 파싱 (BeautifulSoup) | ✅ 완료 |
| 공고 상세 URL 생성 | ✅ 완료 |
| 공고 상세 내용 파싱 (get_detail) | 🔲 미구현 |
| Firebase Firestore 연동 | 🔲 미구현 |
| APScheduler 스케줄러 | 🔲 미구현 |
| 마감 알림 로직 | 🔲 미구현 |
| Flutter 앱 | 🔲 미구현 |

🔔 SSUNoti: 숭실대학교 비교과 공고 알리미 프로젝트 기획서
🏗️ 1. 시스템 전체 구조 (System Architecture)
본 프로젝트는 로컬 서버(Python) + Firebase + Flutter의 하이브리드 구조를 채택합니다.

A. 로컬 서버 (Python & Crawler)

• 주요 기술: Python 3.x, `undetected-chromedriver`, `BeautifulSoup4`, `apscheduler`, `firebase-admin`

• 역할: 봇 감지를 우회하여 SSUPath 데이터를 수집하고 Firebase로 전송

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

├── ssunoti_server/           # Local Python Server

│   ├── config/

│   │   └── serviceAccountKey.json # Firebase 관리자 키

│   ├── src/

│   │   ├── main_scheduler.py # 전체 작업 스케줄러

│   │   ├── crawler_core.py   # 크롤링 핵심 로직

│   │   ├── firebase_util.py  # Firebase 연동 유틸

│   │   └── deadline_checker.py # 마감 알림 로직

│   └── requirements.txt

```

🔄 3. 핵심 주기적 작업 (Scheduled Tasks)
1. 신규 공고 수집 (1시간 주기): 신규 ID 확인 시 전체 파싱 후 저장 & 알림 발송

2. 인원 수 모니터링 (15분 주기): 접수 중인 공고 순회 → 인원 업데이트 → 90% 도달 시 알림

3. 마감 기한 체크 (매일 오전): DB 조회 후 마감 임박 건 알림 발송

💾 4. 데이터베이스 설계 (Firestore)
• Collection: `notices`

• Document ID: `{notice_id}` (SSUPath 게시글 번호)

• Fields: title, url, content, deadline(Timestamp), current_capacity, total_capacity, is_closing_soon, notified_deadline, created_at

🚩 5. 핵심 로직
• 중복 방지: 문서 ID를 게시글 번호로 지정하여 `doc.exists`로 체크

• 인원 체크 최적화: 브라우저 세션을 유지한 채 URL만 변경하여 속도 향상

• 푸시 타겟팅: 전체 알림용 Topic(`all_notices`) 구독 방식 사용

# Firestore 데이터 구조 설계 인수인계 문서

## 프로젝트 개요

대학교 비교과 프로그램(공지) 웹 크롤링 데이터를 Firebase Firestore에 저장하는 프로젝트.
공지 목록 페이지와 각 공지의 세부 페이지를 크롤링하여 저장하며, 두 데이터는 동일한 ID로 연결됨.

---

## Firestore 컬렉션 구조

### 설계 원칙

- **목록 조회 (notices)** 와 **상세 조회 (noticeDetails)** 를 별도 컬렉션으로 분리
    - 이유: 목록 페이지에서는 상세 데이터가 불필요 → 불필요한 읽기 비용 방지
- **동일한 noticeId** 를 양쪽에서 키로 사용하여 JOIN 없이 연결
- **noticeId** 는 원본 사이트의 고유 ID 또는 URL 해시 사용 → 재크롤링 시 중복 방지 (`set` 덮어쓰기 활용)
- **회차별 정보 (sessions)** 는 공지마다 구조가 다르므로 subcollection 으로 분리

---

## 컬렉션 1: `notices` (목록용)

각 공지의 요약 정보. 목록 페이지 렌더링에 사용.
*출처: notice_list.html 실제 크롤링 결과 기반*

```
notices/
  {noticeId}/
    status              : string       // 모집 상태 ("모집중" | "모집대기" | "종료")
    title               : string       // 프로그램명
    summary             : string       // 프로그램 간단설명
    organizer           : string       // 운영조직 (예: "스파르탄 SW교육원")
    programFormat       : string       // 프로그램 형식 (예: "전공교과연계 비교과 (학점인정)")
    applicationPeriod   : { start: Timestamp, end: Timestamp }   // 신청기간
    educationPeriod     : { start: Timestamp, end: Timestamp }   // 교육기간
    target              : string       // 신청대상 (예: "숭실대학교")
    targetStatus        : string       // 신청신분 (예: "학생")
    mileage             : number       // 지급 마일리지
    applicantCount      : number       // 신청자 수
    waitlistCount       : number       // 대기자 수
    capacity            : number       // 모집 정원
    competencyTags      : string[]     // 역량 태그 (예: ["융합", "창의", "리더십"])
    posterUrl           : string       // 썸네일/포스터 이미지 URL

    // 메타 필드 (크롤러가 자동 기록)
    crawledAt           : Timestamp    // 마지막 크롤링 시각
    sourceUrl           : string       // 원본 목록 페이지 URL
```

---

## 컬렉션 2: `noticeDetails` (상세용)

세부 공지 페이지 크롤링 결과. 공지 클릭 시 조회.
*출처: notice_detail.html, notice_detail2.html 실제 크롤링 결과 기반*

```
noticeDetails/
  {noticeId}/                          ← notices와 동일한 ID 사용
    title               : string       // 프로그램명
    organizer           : string       // 운영조직
    managerEmail        : string       // 담당자 이메일 (예: "gjshim@ssu.ac.kr")
    managerPhone        : string       // 담당자 번호 (예: "02-828-7132")
    programType         : string       // 프로그램 유형 (예: "학습역량강화 / 학습지원프로그램")
    semester            : { year: number, term: number }   // 운영년도/학기 (예: {year: 2026, term: 1})
    category            : string       // 프로그램 분류 (예: "기타", "특강/워크숍")
    programFormat       : string       // 프로그램 형식 (예: "비교과 (비학점)")
    goal                : string       // 프로그램 목표
    summary             : string       // 프로그램 한줄 소개
    operationMethod     : string       // 운영방식 (예: "대면", "대면/비대면 혼합")
    applicationMethod   : string       // 신청방법 (예: "내부")
    applicationPeriod   : { start: Timestamp, end: Timestamp }   // 신청기간
    selectionMethod     : string       // 선정방법 (예: "직접선발", "선착순선발")
    target              : string       // 신청대상 (예: "숭실대학교")
    targetStatus        : string       // 신청신분 (예: "학생")
    targetDetail        : {            // 학생 신청대상 상세정보
                            academicStatus : string    // 학적 (예: "재학")
                            division       : string    // 구분 (예: "대학")
                            gradeYears     : string[]  // 학년 (예: ["1학년","2학년"] 또는 ["전체"])
                          }
    capacity            : number       // 정원
    waitlistCapacity    : number       // 대기자 정원
    attachments         : [            // 첨부파일
                            { name: string, url: string }
                          ]
    hasCertificate      : boolean      // 이수 인증서 여부
    mileage             : number       // 지급 마일리지
    coreCompetencies    : [            // 핵심역량 비중도
                            { keyword: string, ratio: number }
                          ]
                          // 예: [{"keyword": "리더십역량", "ratio": 50}, {"keyword": "창의역량", "ratio": 25}]
    mainContent         : string       // 프로그램 주요내용 (HTML 또는 plain text)
    courseInfo          : {
                            semester       : { year: number, term: number }
                            hasAttendance  : boolean    // 출석관리 여부
                            progressType   : string     // 진행속성 (예: "일정기간 참여", "1회")
                          }

    // 메타 필드
    crawledAt           : Timestamp
    sourceUrl           : string       // 세부 페이지 URL

    // Subcollection → sessions/ (아래 참고)
```

### Subcollection: `noticeDetails/{noticeId}/sessions/`

회차별 정보. 공지마다 회차 수와 구조가 다를 수 있어 subcollection으로 분리.

```
sessions/
  session_1/
    sessionNo          : number      // 회차 번호
    className          : string      // 강좌명 (예: "2026-1 러닝러닝 4월 학습...")
    educationPeriod    : { start: Timestamp, end: Timestamp }   // 교육기간
    location           : string      // 교육장소
    instructor         : string      // 강사
    attachments        : [           // 첨부파일
                           { name: string, url: string }
                         ]
    hasAssignment      : boolean     // 과제 제출 여부
    assignmentPeriod   : { start: Timestamp, end: Timestamp } | null
    // 공지마다 추가 필드 자유롭게 포함 가능 (NoSQL의 장점)
  session_2/
    ...
```

---

## 크롤러 저장 코드 패턴 (Python / firebase-admin SDK)

```python
from firebase_admin import firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from datetime import datetime

db = firestore.client()
notice_id = f"notice_{원본사이트고유ID}"

# 1. 목록 데이터 저장 (재크롤링 시 자동 덮어쓰기)
db.collection("notices").document(notice_id).set({
    "status": "모집중",
    "title": "ICT 학점연계 프로젝트 인턴십(글로벌 과정)",
    "summary": "학점 인정을 조건으로 ICT 관련 직무 중심 인턴십...",
    "organizer": "스파르탄 SW교육원",
    "programFormat": "전공교과연계 비교과 (학점인정)",
    "applicationPeriod": {
        "start": datetime(2026, 3, 19, 17, 0),
        "end":   datetime(2026, 4, 2, 17, 0),
    },
    "educationPeriod": {
        "start": datetime(2026, 7, 1),
        "end":   datetime(2026, 12, 31),
    },
    "target": "숭실대학교",
    "targetStatus": "학생",
    "mileage": 160,
    "applicantCount": 8,
    "waitlistCount": 0,
    "capacity": 10,
    "competencyTags": ["융합", "창의", "리더십"],
    "posterUrl": "https://...",
    "crawledAt": SERVER_TIMESTAMP,
    "sourceUrl": "https://path.ssu.ac.kr/...",
})

# 2. 상세 데이터 저장
db.collection("noticeDetails").document(notice_id).set({
    "title": "ICT 학점연계 프로젝트 인턴십(글로벌 과정)",
    "organizer": "스파르탄 SW교육원",
    "managerEmail": "gjshim@ssu.ac.kr",
    "managerPhone": "02-828-7132",
    "programType": "학습역량강화 / 학습지원프로그램",
    "semester": {"year": 2026, "term": 1},
    "category": "기타",
    "programFormat": "비교과 (비학점)",
    "goal": "스스로 학습 목표를 설정하고...",
    "summary": "내가 직접 짠 학습(Learning) 코스로...",
    "operationMethod": "대면/비대면 혼합",
    "applicationMethod": "내부",
    "applicationPeriod": {
        "start": datetime(2026, 3, 27),
        "end":   datetime(2026, 4, 3),
    },
    "selectionMethod": "직접선발",
    "target": "숭실대학교",
    "targetStatus": "학생",
    "targetDetail": {
        "academicStatus": "재학",
        "division": "대학",
        "gradeYears": ["1학년", "2학년", "3학년", "4학년"],
    },
    "capacity": 100,
    "waitlistCapacity": 100,
    "attachments": [{"name": "안내문.pdf", "url": "https://..."}],
    "hasCertificate": True,
    "mileage": 160,
    "coreCompetencies": [
        {"keyword": "리더십역량", "ratio": 50},
        {"keyword": "창의역량",   "ratio": 25},
        {"keyword": "융합역량",   "ratio": 25},
    ],
    "mainContent": "...",
    "courseInfo": {
        "semester": {"year": 2026, "term": 1},
        "hasAttendance": True,
        "progressType": "일정기간 참여",
    },
    "crawledAt": SERVER_TIMESTAMP,
    "sourceUrl": "https://path.ssu.ac.kr/...",
})

# 3. 회차별 정보 저장
sessions = [
    {
        "sessionNo": 1,
        "className": "2026-1 러닝러닝 4월 학습...",
        "educationPeriod": {
            "start": datetime(2026, 4, 6),
            "end":   datetime(2026, 4, 30, 23, 59),
        },
        "location": "",
        "instructor": "",
        "attachments": [],
        "hasAssignment": True,
        "assignmentPeriod": {
            "start": datetime(2026, 4, 1),
            "end":   datetime(2026, 4, 30),
        },
    },
]
for session in sessions:
    db.collection("noticeDetails").document(notice_id) \
      .collection("sessions").document(f"session_{session['sessionNo']}") \
      .set(session)
```

---

## 조회 코드 패턴 (Python)

```python
from firebase_admin import firestore

db = firestore.client()

# 목록 조회 - 모집 중인 공지만
notices_ref = db.collection("notices")
query = notices_ref.where("status", "==", "모집중").order_by("applicationPeriod.end")
docs = query.stream()

# 상세 조회
detail = db.collection("noticeDetails").document(notice_id).get()

# 회차 정보 조회
sessions = db.collection("noticeDetails").document(notice_id) \
             .collection("sessions").order_by("sessionNo").stream()
```

---

## 색인(Index) 고려사항

Firestore는 단일 필드 색인은 자동 생성되지만, **복합 쿼리**는 복합 색인이 필요함.
아래 쿼리 조합에 대해 Firebase 콘솔에서 복합 색인 생성 필요:

| 컬렉션 | 필드 1 | 필드 2 | 용도 |
|--------|--------|--------|------|
| notices | status | applicationPeriod.end | 모집중 + 마감일 정렬 |
| notices | competencyTags (array-contains) | crawledAt | 역량 태그 필터 + 최신순 |
| notices | organizer | status | 운영조직별 모집중 필터 |

---

## 주의 사항

- **Timestamp**: 날짜/시간 필드는 Python `datetime` 객체로 전달 (firebase-admin이 자동으로 Timestamp 변환)
- **재크롤링**: `set()`은 덮어쓰기이므로 중복 저장 없이 항상 최신 데이터 유지 가능
- **sessions 삭제**: 회차 정보가 바뀐 경우 기존 sessions subcollection을 먼저 삭제 후 재저장 필요 (Firestore는 subcollection을 자동으로 덮어쓰지 않음)
- **대용량 문자열**: `mainContent`, `goal` 등 긴 텍스트 필드는 문서당 1MB 제한 내에서 관리
- **보안 규칙**: 크롤러는 서버 측(Admin SDK)에서 실행하므로 Security Rules 우회됨. 클라이언트(Flutter)는 읽기만 허용하도록 Firestore Security Rules 설정 권장
- **status 동기화**: `notices.status`는 크롤링 주기마다 갱신 필요 (신청기간 만료 후 "종료"로 변경됨)

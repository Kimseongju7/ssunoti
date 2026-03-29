# SSUPath URL 쿼리 파라미터 분석 문서

## 📋 개요
숭실대학교 비교과 프로그램 목록 조회 API의 쿼리 파라미터 구조 분석

**기본 엔드포인트**: `https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do`

---

## 🔍 쿼리 파라미터 상세 분석

### 1. 페이지네이션 (Pagination)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `paginationInfo.currentPageNo` | Integer | 현재 페이지 번호 | `1`, `3` | 1부터 시작 |

**예시**:
```
paginationInfo.currentPageNo=3  # 3페이지
```

---

### 2. 정렬 (Sorting)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `sort` | String | 정렬 기준 코드 | `0001` | 고정값으로 추정 |

**추정 정렬 옵션**:
- `0001`: 기본 정렬 (등록일/공고일 내림차순 추정)

---

### 3. 운영 연도 및 학기 (Academic Year & Semester)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `operYySh` | String | 운영 연도 | `2025`, `2026` | 4자리 연도 |
| `operSemCdSh` | String | 학기 코드 | `0000` | 0000=전체 |
| `operSemCdShVal` | String | 학기 코드 값 | `0000` | operSemCdSh와 동일 |

**학기 코드 추정**:
- `0000`: 전체 학기
- `0001`: 1학기 (추정)
- `0002`: 2학기 (추정)
- `0003`: 여름학기 (추정)
- `0004`: 겨울학기 (추정)

---

### 4. 모집 상태 (Recruitment Status) ⭐ 핵심 필터

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `recStaCdSh` | String | 모집 상태 코드 | `RS01`, `RS02`, `RS03` | 필수 필터 |

**모집 상태 코드표**:

| 코드 | 의미 | 설명 |
|------|------|------|
| `0000` | 전체 | 모든 상태 포함 |
| `RS01` | 모집 대기 | 모집 시작 전 |
| `RS02` | 모집 중 | 현재 지원 가능 ⭐ |
| `RS03` | 종료 | 모집 마감 |

**크롤링 시 권장**: `recStaCdSh=RS02` (모집 중만 필터링)

---

### 5. 프로그램 분류 (Program Category) ⭐ 복수 선택 가능

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `prgmClsCdSh` | String / Array | 프로그램 분류 코드 | `PC02`, `PC15` | 복수 선택 시 파라미터 반복 |

**프로그램 분류 코드표**:

| 코드 | 카테고리 추정     |
|------|-------------|
| `0000` | 전체          |
| `PC01` | 교육/특강 (추정)  |
| `PC02` | 공모전/경진대회 ✅  |
| `PC03` | 봉사활동 (추정)   |
| `PC04` | 동아리/문화 (추정) |
| `PC15` | 창업          |

**복수 카테고리 선택 방법**:
```
# 공모전(PC02) + PC15 카테고리 동시 필터링
prgmClsCdSh=PC02&prgmClsCdSh=PC15
```

**실제 사용 예시**:
```
https://path.ssu.ac.kr/.../findIcmpNsbjtPgmList.do?...&prgmClsCdSh=PC02&prgmClsCdSh=PC15&...
```

---

### 6. 프로그램 형태 (Program Format)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `prgmFormCdSh` | String | 프로그램 형태 코드 | `0000` | 0000=전체 |
| `prgmFormCdShVal` | String | 프로그램 형태 코드 값 | `0000` | prgmFormCdSh와 동일 |

**형태 코드 추정**:
- `0000`: 전체
- 온라인/오프라인/혼합 등의 구분 가능성

---

### 7. 검색 (Search)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `searchValue` | String | 검색 키워드 | `sap`, `창업` | 제목/내용 검색 |

**사용 예시**:
```
searchValue=창업  # "창업" 키워드 검색
searchValue=sap   # "sap" 키워드 검색 (실제 사용 확인됨)
searchValue=      # 공백 = 전체 검색
```

**실제 URL 예시**:
```
https://path.ssu.ac.kr/.../findIcmpNsbjtPgmList.do?...&searchValue=sap&...
```

**주의사항**:
- URL 인코딩 필요 (한글 검색어는 자동으로 인코딩됨)
- 검색 범위: 공고 제목 및 내용 추정

---

### 8. 조직 필터 (Organization)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `vshOrgid` | String | 주관 조직 ID | (공백) | 특정 기관 필터 |
| `vshOrgzNm` | String | 주관 조직명 | (공백) | 조직명 검색 |

---

### 9. 교육 일자 (Education Date)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `eduFrDt` | String | 교육 시작일 | `20260101` | YYYYMMDD 형식 추정 |
| `eduToDt` | String | 교육 종료일 | `20260131` | YYYYMMDD 형식 추정 |

---

### 10. 학과 필터 (Department)

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `scpfDpmtCdSh` | String | 학과 코드 | (공백) | 특정 학과 필터 |
| `scpfDpmtCdNm` | String | 학과명 | (공백) | 학과명 검색 |

---

### 11. 기타 파라미터

| 파라미터 | 타입 | 설명 | 예시 | 비고 |
|---------|------|------|------|------|
| `chkAblyCount` | Integer | 능력 체크 카운트 | `0` | 용도 불명 |

---

## 🎯 크롤링용 추천 URL 패턴

### 1️⃣ 모집 중인 전체 공고 (가장 중요)
```
https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do?paginationInfo.currentPageNo=1&sort=0001&chkAblyCount=0&operYySh=2026&operSemCdSh=0000&operSemCdShVal=0000&vshOrgid=&vshOrgzNm=&recStaCdSh=RS02&searchValue=&prgmFormCdSh=0000&prgmFormCdShVal=0000&eduFrDt=&eduToDt=&scpfDpmtCdSh=&scpfDpmtCdNm=
```

**핵심 파라미터**:
- `operYySh=2026` (현재 연도)
- `recStaCdSh=RS02` (모집 중만 필터링)
- `paginationInfo.currentPageNo=1` (1페이지부터 순회)

---

### 2️⃣ 순수 검색어만 사용 (필터 없음)
```
https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do?paginationInfo.currentPageNo=1&sort=0001&chkAblyCount=0&operYySh=2025&operSemCdSh=0000&operSemCdShVal=0000&vshOrgid=&vshOrgzNm=&searchValue=sap&prgmFormCdSh=0000&prgmFormCdShVal=0000&eduFrDt=&eduToDt=&scpfDpmtCdSh=&scpfDpmtCdNm=
```

**핵심 파라미터**:
- `searchValue=sap` (검색어만 설정)
- `recStaCdSh` 파라미터 없음 = **모든 모집 상태** 포함
- `prgmClsCdSh` 파라미터 없음 = **모든 카테고리** 포함

**사용 시나리오**:
- 특정 키워드로 모든 공고 검색 (상태, 카테고리 무관)
- 사용자 맞춤 검색 기능 구현 시 유용

---

### 3️⃣ 공모전/경진대회만 필터링
```
https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do?paginationInfo.currentPageNo=1&sort=0001&chkAblyCount=0&operYySh=2026&operSemCdSh=0000&operSemCdShVal=0000&vshOrgid=&vshOrgzNm=&recStaCdSh=RS02&prgmClsCdSh=PC02&searchValue=&prgmFormCdSh=0000&prgmFormCdShVal=0000&eduFrDt=&eduToDt=&scpfDpmtCdSh=&scpfDpmtCdNm=
```

**추가 파라미터**:
- `prgmClsCdSh=PC02` (공모전 카테고리)
- `recStaCdSh=RS02` (모집 중만)

---

### 3️⃣ 최소 필수 파라미터 패턴 (간소화)
```
https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do?paginationInfo.currentPageNo=1&operYySh=2026&recStaCdSh=RS02
```

**테스트 필요**: 최소 파라미터로 동작하는지 확인 필요

---

## 🔑 파라미터 생략 시 동작 (중요)

### 필수 vs 선택적 파라미터

**완전 생략 가능한 파라미터** (생략 시 "전체" 적용):
- `recStaCdSh` - 생략 시 모든 모집 상태 포함
- `prgmClsCdSh` - 생략 시 모든 카테고리 포함
- `searchValue` - 생략 시 전체 검색

**항상 포함되는 파라미터** (생략 불가):
- `paginationInfo.currentPageNo` - 페이지 번호
- `sort` - 정렬 기준
- `operYySh` - 운영 연도

**실제 사용 예시**:
```
# 파라미터 생략 패턴 (2025년 전체 공고 중 "sap" 검색)
https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do?paginationInfo.currentPageNo=1&sort=0001&chkAblyCount=0&operYySh=2025&operSemCdSh=0000&operSemCdShVal=0000&vshOrgid=&vshOrgzNm=&searchValue=sap&prgmFormCdSh=0000&prgmFormCdShVal=0000&eduFrDt=&eduToDt=&scpfDpmtCdSh=&scpfDpmtCdNm=
```

**주의**:
- 파라미터를 **빈 값으로 포함** (`recStaCdSh=`)하는 것과 **완전히 생략**하는 것은 다를 수 있음
- 빈 값 포함 시: 서버가 기본값 적용
- 완전 생략 시: 파라미터 무시 (전체 조회)

---

## 💡 크롤링 구현 시 고려사항

### 1. 연도 자동 업데이트
```python
from datetime import datetime

current_year = datetime.now().year
url = f"...&operYySh={current_year}&..."
```

### 2. 페이지네이션 처리
```python
page = 1
while True:
    url = f"...&paginationInfo.currentPageNo={page}&..."
    # 크롤링 로직
    if no_more_data:
        break
    page += 1
```

### 3. 모집 상태별 크롤링 전략

| 상태 | 크롤링 주기 | 알림 여부 |
|------|-----------|----------|
| RS01 (모집 대기) | 1일 1회 | ❌ |
| RS02 (모집 중) | 1시간 1회 | ✅ 신규 발견 시 알림 |
| RS03 (종료) | 크롤링 불필요 | ❌ |

### 4. 중복 체크 로직
- 각 공고의 고유 ID 추출 필요
- Firestore에 저장된 `notice_id`와 비교

---

## 🔗 API 응답 형식 분석 필요 사항

현재 문서는 URL 파라미터만 분석했습니다. 실제 구현을 위해 추가 확인 필요:

1. **응답 데이터 형식**: JSON? HTML? XML?
2. **페이지당 항목 수**: 한 페이지에 몇 개씩 표시되는가?
3. **공고 상세 URL 패턴**: 개별 공고 상세 페이지 URL 구조
4. **총 페이지 수 확인 방법**: 마지막 페이지 판별 로직
5. **프로그램 분류 코드 전체 목록**: PC01, PC03, PC04 등 확인

---

## 📝 업데이트 이력

- **2026-01-26 v1.0**: 초안 작성 (URL 패턴 분석 완료)
- **2026-01-26 v1.1**: 복수 카테고리 선택 패턴 추가 (`prgmClsCdSh` 중복 사용)
- **2026-01-26 v1.2**: 검색어 기능 상세 분석 추가 (`searchValue` 실제 사용 예시)
- **2026-01-26 v1.3**: 파라미터 생략 시 동작 분석 추가 (필수/선택 파라미터 구분)
- **2026-01-26 v1.4**: 순수 검색 패턴 추가 (필터 없이 검색어만 사용)
- **TODO**: 실제 크롤링 테스트 후 응답 형식 문서화

---

## ⚠️ 주의사항

1. **Bot 감지 회피**: `undetected-chromedriver` 사용 권장 (CLAUDE.md 명시됨)
2. **요청 간격**: 서버 부하 방지를 위해 최소 1~2초 간격 권장
3. **세션 유지**: 로그인 세션이 필요한지 확인 필요
4. **파라미터 인코딩**: URL 인코딩 처리 필요 여부 확인
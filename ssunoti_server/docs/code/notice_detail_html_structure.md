# 공고 상세 페이지 HTML 구조 분석

**출처**: `notice_detail.html`, `notice_detail2.html` (SSUPath 비교과 프로그램 상세 페이지)
**URL**: `https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmInfo.do?encSddpbSeq=...`

---

## 전체 페이지 컨테이너 구조

```
div#tilesContent.con_box
└── section
    ├── [섹션 1] 프로그램 상세 정보
    │   ├── div.table_top
    │   │   └── h4                         ← 프로그램 제목
    │   └── div.table_wrap
    │       └── table.table.t_view
    │           └── tbody > tr             ← 각 필드 행
    │
    └── [섹션 2] 강좌 정보
        ├── div.table_top > h4             ("강좌 정보")
        ├── div.table_wrap#intlNsbjtLtrInfoList  ← 강좌 기본정보 (출석관리, 진행속성)
        ├── div.table_wrap#intlNsbjtLtrInfoList  ← 1회차
        ├── div.table_wrap#intlNsbjtLtrInfoList  ← 2회차
        └── ...                            ← 회차 수만큼 반복
```

> **주의**: `id="intlNsbjtLtrInfoList"`가 여러 개 중복 사용됨.
> 첫 번째는 강좌 기본정보, 그 이후부터 각 회차 정보임.

---

## 섹션 1: 프로그램 상세 정보

### 프로그램 제목
- **선택자**: `div.table_top > h4`
- **예시**: `"2026-1학기 자기주도학습챌린지 <러닝러닝>"`

```html
<div class="table_top">
  <h4>2026-1학기 자기주도학습챌린지 &lt;러닝러닝&gt;</h4>
  <div class="like_btnwrap type2">
    <a href="#;" class="col02 shpbBtn"
       data-params='{"encExtcrSeq":"...", "shpbYn":"Y"}'>
      <span class="shpbIcon off">찜하기</span>
    </a>
  </div>
</div>
```

---

### 필드별 선택자 (메인 테이블 `table.t_view tbody`)

각 필드는 `<tr><th scope="row">레이블</th><td colspan="3">값</td></tr>` 구조.
`th` 텍스트로 `td` 값을 매핑한다.

| 필드 | th 텍스트 | 예시값 (detail) | 예시값 (detail2) |
|---|---|---|---|
| 운영조직 | `운영조직` | `교수학습혁신팀` | `교수학습혁신팀` |
| 담당자 이메일 | `담당자 이메일` | `gjshim@ssu.ac.kr` | `121560@ssu.ac.kr` |
| 담당자 번호 | `담당자 번호` | `02-828-7132` | `02-828-7136` |
| 프로그램 유형 | `프로그램 유형` | `학습역량강화 / 학습지원프로그램` | `학습역량강화 / 학습지원프로그램` |
| 운영년도/학기 | `운영년도/학기` | `2026년 1학기` | `2026년 1학기` |
| 프로그램 분류 | `프로그램 분류` | `기타` | `특강/워크숍` |
| 프로그램 형식 | `프로그램 형식` | `비교과 (비학점)` | `비교과 (비학점)` |
| 프로그램 목표 | `프로그램 목표` | 텍스트 (긴 문장) | 텍스트 (긴 문장) |
| 한줄 소개 | `프로그램 한줄 소개` | `내가 직접 짠 학습(Learning) 코스로...` | `체계적인 학습전략과...` |
| 운영방식 | `운영방식` | `대면/비대면 혼합` | `대면` |
| 신청방법 | `신청방법` | `내부` | `내부` |
| 선정방법 | `선정방법` | `직접선발` | `선착순선발` |
| 이수 인증서 | `이수 인증서` | `O` | `O` |
| 지급 마일리지 | `지급 마일리지` | `160` | `20` |

---

### 신청기간 + 선정방법 (같은 tr에 위치)

신청기간과 선정방법은 **한 행에 두 필드가 함께** 있음.

```html
<tr>
  <th scope="row">신청기간</th>
  <td>2026.03.27 00:00 ~ 2026.04.03 00:00</td>
  <th scope="row">선정방법</th>
  <td>직접선발</td>
</tr>
```

- 신청기간: `th[신청기간]` 다음 `td` (첫 번째)
- 선정방법: `th[선정방법]` 다음 `td`
- 형식: `"2026.03.27 00:00 ~ 2026.04.03 00:00"` (` ~ ` 공백 포함으로 분리)

---

### 신청대상

```html
<tr>
  <th scope="row">신청대상</th>
  <td colspan="3">
    <ul class="ul_chk ul_inline">
      <li>숭실대학교</li>
    </ul>
  </td>
</tr>
```

- **선택자**: `th[신청대상] + td ul.ul_chk li`

---

### 신청신분

```html
<tr>
  <th scope="row">신청신분</th>
  <td colspan="3">
    <div class='cdDiv'>학생</div>
  </td>
</tr>
```

- **선택자**: `th[신청신분] + td .cdDiv`
- **예시**: `"학생"`, `"전체"`, `"학생, 일반인"`

---

### 학생 신청대상 상세정보

학적, 구분, 학년 세 가지 `dl.flex_dl`로 구성됨.

```html
<tr>
  <th scope="row">학생 신청대상 상세정보</th>
  <td colspan="3">
    <dl class="flex_dl">
      <dt>학적:</dt>
      <dd><div class='cdDiv'>재학</div></dd>
    </dl>
    <dl class="flex_dl">
      <dt>구분:</dt>
      <dd><div class='cdDiv'>대학</div></dd>
    </dl>
    <dl class="flex_dl">
      <dt>학년:</dt>
      <dd><div class='cdDiv'>1학년, 2학년, 3학년, 4학년, 5학년</div></dd>
      <!-- detail2의 경우: <div class='cdDiv'>전체</div> -->
    </dl>
  </td>
</tr>
```

- 학적: `dl.flex_dl:nth-of-type(1) dd .cdDiv`
- 구분: `dl.flex_dl:nth-of-type(2) dd .cdDiv`
- 학년: `dl.flex_dl:nth-of-type(3) dd .cdDiv` → `,` 로 split하거나 그대로 저장

---

### 정원 / 대기자

숫자가 `<b>` 태그로 감싸진 혼합 텍스트 구조.

```html
<tr>
  <th scope="row">정원/대기자</th>
  <td colspan="3">
    <b>정원</b> 100<b>명</b> / <b>대기자</b> 100<b>명</b>
  </td>
</tr>
```

- **선택자**: `th[정원/대기자] + td`
- **파싱 방법**: `td.get_text()` → 정규식 또는 숫자만 추출
  - `"정원 100명 / 대기자 100명"` → 정원: `100`, 대기자: `100`

---

### 첨부파일

```html
<tr>
  <th scope="row">첨부파일</th>
  <td colspan="3">
    <ul class="cmnFileLst iconBg">
      <li>
        <a href="/common/cmnFile/download.do?encSvrFileNm=...">
          붙임 1. 러닝 러닝_학습계획서(양식).hwp
        </a>
      </li>
      <!-- 파일 없을 경우: <li>-</li> 또는 빈 ul -->
    </ul>
  </td>
</tr>
```

- **선택자**: `th[첨부파일] + td .cmnFileLst li a`
- 파일명: `.get_text(strip=True)`
- 다운로드 URL: `a['href']` → `BASE_URL + href` 로 절대경로 변환

---

### 핵심역량 비중도

```html
<tr>
  <th scope="row">핵심역량 비중도</th>
  <td colspan="3">
    <ul class="ul_chk">
      <li><span>리더십역량</span><strong>50</strong>%</li>
      <li><span>창의역량</span><strong>25</strong>%</li>
      <li><span>융합역량</span><strong>25</strong>%</li>
    </ul>
  </td>
</tr>
```

- 역량명: `th[핵심역량 비중도] + td .ul_chk li span`
- 비중: `th[핵심역량 비중도] + td .ul_chk li strong` → `int()`

---

### 프로그램 주요내용

CKEditor로 작성된 HTML 콘텐츠가 그대로 삽입됨.

```html
<tr>
  <th scope="row">프로그램 주요내용</th>
  <td colspan="3">
    <div class="td_box imgViewDiv">
      <div class='ck-contentEditDiv'>
        <!-- 리치 HTML 콘텐츠 -->
        <p>안녕하세요 교수학습혁신센터입니다...</p>
      </div>
    </div>
  </td>
</tr>
```

- **선택자**: `th[프로그램 주요내용] + td .ck-contentEditDiv`
- HTML 태그 포함 저장 또는 `.get_text()`로 순수 텍스트 추출 선택

---

## 섹션 2: 강좌 정보

### 강좌 기본 정보 (첫 번째 `#intlNsbjtLtrInfoList`)

```html
<div class="table_wrap" id="intlNsbjtLtrInfoList">
  <table class="table t_view add_tr">
    <tbody>
      <tr><th scope="row" colspan="2">운영년도 및 학기</th><td>2026/1학기</td></tr>
      <tr><th scope="row" colspan="2">출석관리</th><td>Y</td></tr>
      <tr><th scope="row" colspan="2">진행속성</th><td>일정기간 참여</td></tr>
      <!-- detail2: 출석관리 N, 진행속성 1회 -->
    </tbody>
  </table>
</div>
```

- 운영년도/학기: `tr:nth-of-type(1) td`
- 출석관리: `tr:nth-of-type(2) td` → `"Y"` / `"N"`
- 진행속성: `tr:nth-of-type(3) td` → `"일정기간 참여"` / `"1회"`

---

### 회차 정보 (두 번째 이후 `#intlNsbjtLtrInfoList`)

각 회차는 독립된 `div.table_wrap` 블록. `id`가 동일(`intlNsbjtLtrInfoList`)하게 중복됨.

```html
<div class="table_wrap" id="intlNsbjtLtrInfoList">
  <table class="table t_view add_tr">
    <tbody>
      <tr>
        <th rowspan="5">1<b>회차</b></th>
        <th>교육기간</th>
        <td>2026.04.06 00:00 ~ 2026.04.30 23:59</td>
      </tr>
      <tr>
        <th>교육장소/강사</th>
        <td> / </td>
      </tr>
      <tr>
        <th>강좌명</th>
        <td>2026-1 러닝러닝 4월 학습 월별 보고서&증빙 제출</td>
      </tr>
      <tr>
        <th>첨부파일</th>
        <td>
          <ul class="cmnFileLst">
            <li><a href="...">파일명</a></li>
          </ul>
        </td>
      </tr>
      <tr>
        <th>과제제출</th>
        <td>
          <b>제출</b>
          <span class="pl20">2026.04.27 00:00 ~ 2026.05.04 00:00</span>
          <!-- 과제 없을 경우: <b>미제출</b> -->
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**회차 필드 선택자 (각 블록 내부 기준):**

| 필드 | 선택자 | 예시값 |
|---|---|---|
| 회차번호 | `th[rowspan] b` 앞 텍스트 + `b` | `1` |
| 교육기간 | `th:contains("교육기간") + td` | `"2026.04.06 00:00 ~ 2026.04.30 23:59"` |
| 교육장소 | `th:contains("교육장소/강사") + td` → `/` 앞 | `""` (비어있을 수 있음) |
| 강사 | `th:contains("교육장소/강사") + td` → `/` 뒤 | `""` (비어있을 수 있음) |
| 강좌명 | `th:contains("강좌명") + td` | `"2026-1 러닝러닝 4월..."` |
| 첨부파일 | `th:contains("첨부파일") + td .cmnFileLst li a` | 파일 객체 리스트 |
| 과제제출 여부 | `th:contains("과제제출") + td b` | `"제출"` / `"미제출"` |
| 과제제출 기간 | `th:contains("과제제출") + td span.pl20` | `"2026.04.27 00:00 ~ 2026.05.04 00:00"` |

---

## detail.html vs detail2.html 비교

| 항목 | detail.html | detail2.html |
|---|---|---|
| 프로그램 분류 | 기타 | 특강/워크숍 |
| 선정방법 | 직접선발 | 선착순선발 |
| 운영방식 | 대면/비대면 혼합 | 대면 |
| 학생 신청대상 학년 | 1~5학년 개별 나열 | `전체` |
| 정원 | 100명 / 대기자 100명 | 60명 / 대기자 20명 |
| 지급 마일리지 | 160 | 20 |
| 출석관리 | Y | N |
| 진행속성 | 일정기간 참여 | 1회 |
| **회차 수** | **3회차** | **1회차** |
| 과제제출 | 제출 (기간 있음) | 미제출 |
| 첨부파일 | 있음 (복수) | 없음 |

**HTML 구조는 동일**하며 데이터 값만 다름.

---

## 파싱 시 주의사항

- **`id` 중복**: `intlNsbjtLtrInfoList`가 여러 번 등장. `find()`는 첫 번째만 반환하므로 `find_all()`로 모두 가져온 뒤 인덱스로 구분 필요
- **신청기간 구분자**: 목록 페이지는 `~`, 상세 페이지는 ` ~ ` (공백 포함). `split('~')` 후 `strip()` 필수
- **교육장소/강사 분리**: `" / "` 로 분리. 둘 다 비어있을 수 있음
- **정원/대기자 숫자 추출**: `<b>` 태그가 섞인 텍스트 — `re.findall(r'\d+', td.get_text())` 활용 권장
- **프로그램 주요내용**: HTML 태그 포함 가능 — Firestore 1MB 제한 고려, 필요 시 `get_text()`로 plain text 저장
- **첨부파일 없음 처리**: `<li>-</li>` 또는 빈 `ul`로 표현될 수 있음 → `href` 속성 존재 여부로 판단

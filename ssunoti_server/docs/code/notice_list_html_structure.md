# 공고 목록 페이지 HTML 구조 분석

**출처**: `notice_list.html` (SSUPath 비교과 프로그램 목록 페이지)
**URL**: `https://path.ssu.ac.kr/ptfol/imng/icmpNsbjtPgm/findIcmpNsbjtPgmList.do`

---

## 전체 구조

```
div.lica_wrap
└── ul
    └── li  (공고 1개)
        ├── div.cont_box
        │   ├── div.img_wrap          ← 포스터 이미지
        │   └── div.desc_wrap
        │       ├── div.text_wrap     ← 상태, 조직, 형식, 제목, 설명
        │       └── div.info_wrap     ← 신청기간, 교육기간, 신청대상, 신청신분
        └── div.etc_cont
            └── ul.rq_desc
                ├── li.info           ← 마일리지
                ├── li.cnt            ← 신청자/대기자/모집정원
                └── li.cabil          ← 역량 태그 (없는 공고도 있음)
```

---

## 필드별 CSS 선택자 및 예시값

### notice_id
- **선택자**: `a.detailBtn[data-params]` → JSON 파싱 → `encSddpbSeq`
- **예시**: `"63c64f19a5f1916fe434bc109041961f"`
- **비고**: 공고마다 여러 `a.detailBtn`이 있으나 `encSddpbSeq` 값은 동일

```html
<a href="#" class="tit ellipsis detailBtn"
   data-params='{"encSddpbSeq":"63c64f19a5f1916fe434bc109041961f","paginationInfo.currentPageNo":"1"}'>
```

### status (모집 상태)
- **선택자**: `div.label_box > a.detailBtn > span`
- **가능한 값**: `"모집중"`, `"모집대기"`, `"종료"`

```html
<div class="label_box">
  <a href="#" class="btn01 col08 detailBtn" data-params='{"encSddpbSeq":"..."}'>
    <span>모집중</span>
  </a>
</div>
```

### organizer (운영조직) / program_format (프로그램 형식)
- **선택자**: `ul.major_type > li`
  - `li:nth(0)` → organizer
  - `li:nth(1)` → program_format
- **예시**: `"교수학습혁신팀"` / `"비교과 (비학점)"`
- **program_format 예시**: `"비교과 (비학점)"`, `"전공교과연계 비교과 (학점인정)"`, `"전공교과연계 비교과 (학점불인정)"`

```html
<ul class="major_type">
  <li>교수학습혁신팀</li>
  <li>비교과 (비학점)</li>
</ul>
```

### title (제목)
- **선택자**: `a.tit.detailBtn`
- **예시**: `"2026-1학기 자기주도학습챌린지 <러닝러닝>"`

```html
<a href="#" class="tit ellipsis detailBtn" data-params='{"encSddpbSeq":"..."}'>
  2026-1학기 자기주도학습챌린지 &lt;러닝러닝&gt;
</a>
```

### summary (간단설명)
- **선택자**: `p.desc`
- **예시**: `"내가 직접 짠 학습(Learning) 코스로 달리는(Running) 한 학기의 여정"`

```html
<p class="desc ellipsis">내가 직접 짠 학습(Learning) 코스로 달리는(Running) 한 학기의 여정</p>
```

### application_period / education_period (기간)
- **선택자**: `div.info_wrap dl` → dt 텍스트로 키 매핑
  - `dt == "신청기간"` → `dd` 텍스트
  - `dt == "교육기간"` → `dd` 텍스트
- **형식**: `"2026.03.27 00:00~2026.04.03 00:00"` (`~` 로 start/end 분리)

```html
<div class="info_wrap">
  <dl><dt>신청기간</dt><dd>2026.03.27 00:00~2026.04.03 00:00</dd></dl>
  <dl><dt>교육기간</dt><dd>2026.04.06 00:00~2026.06.30 23:59</dd></dl>
  <dl><dt>신청대상</dt><dd>숭실대학교</dd></dl>
  <dl><dt>신청신분</dt><dd><div class='cdDiv'>학생</div></dd></dl>
</div>
```

### target (신청대상) / target_status (신청신분)
- **target 선택자**: `div.info_wrap dl dt[신청대상] + dd`
- **target_status 선택자**: `div.info_wrap dl dt[신청신분] + dd > div.cdDiv`
- **target_status 예시**: `"학생"`, `"전체"`, `"학생, 일반인"`

### mileage (마일리지)
- **선택자**: `li.info > dl > dd`
- **예시**: `160`, `20`, `10`, `600`

```html
<li class="info">
  <dl><dt>마일리지</dt><dd>160</dd></dl>
</li>
```

### applicant_count / waitlist_count / capacity (인원)
- **선택자**: `li.cnt > dl` → dt 텍스트로 키 매핑
  - `"신청자"` → applicant_count
  - `"대기자"` → waitlist_count
  - `"모집정원"` → capacity

```html
<li class="cnt">
  <dl><dt>신청자</dt><dd>52</dd></dl>
  <dl><dt>대기자</dt><dd>0</dd></dl>
  <dl><dt>모집정원</dt><dd>100</dd></dl>
  <p class="cnt_desc">모집이 마감된 프로그램입니다.</p>
</li>
```

### competency_tags (역량 태그)
- **선택자**: `li.cabil > dl > dd > span.on`
- **비고**: `li.cabil` 자체가 없는 공고도 존재 → 빈 리스트 반환
- **예시**: `["리더십", "창의", "융합"]`, `["융합", "창의", "의사소통"]`

```html
<li class="cabil">
  <dl>
    <dt>#역량</dt>
    <dd>
      <span class="on">리더십</span>
      <span class="on">창의</span>
      <span class="on">융합</span>
    </dd>
  </dl>
</li>
```

### poster_url (썸네일 이미지)
- **선택자**: `div.img_wrap > a > img[src]`
- **비고**: `src`가 `/`로 시작하는 상대경로 → `https://path.ssu.ac.kr` 접두사 추가 필요

```html
<div class="img_wrap">
  <a href="#" class="detailBtn" data-params='{"encSddpbSeq":"..."}'>
    <img src="/common/cmnFile/thumbnail.do?encSvrFileNm=63c6...&width=170&height=120"
         id="repnImg" alt=".." />
  </a>
</div>
```

---

## 주의사항

- `li` 중 `a.detailBtn`이 없는 항목(빈 레이아웃용 li)이 섞여 있을 수 있음 → 파싱 전 필터링 필요
- `mileage`, `applicant_count` 등 숫자 필드가 `"-"` 등 비숫자로 올 가능성 있음 → 추후 방어 처리 검토
- `신청신분`의 `div.cdDiv` 내부 텍스트에 공백이 포함될 수 있음 (`"학생 "`) → `strip()` 필수

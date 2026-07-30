# SSUNoti Design System

> SSUPath(`https://path.ssu.ac.kr`)의 실제 CSS 에서 추출한 토큰을 기반으로 한다.
> 출처: `common/1user/common/css/common.css`, `portfolio/style.css`, `font.css`
> 추출일: 2026-07-30

SSUPath 원본에는 정의된 디자인 시스템이 없다 — CSS 전체에 고유 색상이 **528개**
흩어져 있다. 이 문서는 빈도 상위 값과 실제 컴포넌트 셀렉터에서 쓰이는 값만 골라
**없던 시스템을 재구성한 것**이다. 목표는 SSUPath 를 픽셀 단위로 베끼는 것이 아니라,
학생이 SSUPath 에서 보던 색·라벨 형태를 앱에서도 알아보게 만드는 것이다.

---

## 1. Visual Theme & Atmosphere

**성격** — 대학 학사 포털. 신뢰감이 우선이고 개성은 뒤다. 차분한 남색·청록 계열에
정보 밀도가 높은 레이아웃.

| 축 | 위치 |
|---|---|
| 톤 | 공식적 · 절제 (놀이성 없음) |
| 밀도 | 높음. 한 카드에 제목 + 메타 4종 + 라벨 2~3개 |
| 채도 | 낮은 배경 + 라벨에만 고채도 |
| 모서리 | 부드럽지만 둥글지 않다 (3~10px, 라벨만 pill) |
| 그림자 | 거의 없음. 있으면 아주 얕게 |

**핵심 결정 — 상태를 색으로 말한다.** SSUPath 는 모집 상태를 pill 라벨의 배경색으로
구분한다(모집중 파랑 / 대기 청록 / 종료 회색). 텍스트를 읽지 않고 색만 봐도
지원 가능 여부를 안다. 이 앱도 그 규칙을 지킨다.

**모바일 번역** — SSUPath 는 데스크톱 3열 정보 그리드다. 좁은 화면에서는 그 밀도를
그대로 못 옮기므로, 목록 카드에는 제목 + 라벨만 두고 나머지는 상세로 내린다.

---

## 2. Color Palette & Roles

### Brand

| 토큰 | Hex | 원본 출현 | 역할 |
|---|---|---|---|
| `brandNavy` | `#0E2767` | 67회 · `.label_box .col08` | 최상위 강조. 앱바, 주요 버튼 |
| `brandTeal` | `#00688F` | 79회 · 그림자 색 원본 | 보조 강조. 선택 상태, 링크 |
| `brandCyan` | `#00A4CA` | 50회 | 포인트. 진행 표시, 하이라이트 |

### Status (pill 라벨 배경 — 원본 클래스와 1:1)

| 토큰 | Hex | 원본 | 의미 |
|---|---|---|---|
| `statusOpen` | `#0D97FF` | `.col01` | 모집중 |
| `statusWaiting` | `#43B5A4` | `.col02` | 모집대기 |
| `statusNeutral` | `#747474` | `.col05` | 일반 분류 |
| `statusEmphasis` | `#0E2767` | `.col08` | 강조 분류 |
| `statusClosed` | `#BCBCBC` | `.end .label` | 종료 |

> 라벨 위 글자는 **항상 `#FFFFFF`**. 예외 없음.

### Text

| 토큰 | Hex | 원본 |
|---|---|---|
| `textStrong` | `#222222` | 제목 `.tit`, 정보값 |
| `textBody` | `#333333` | 본문 (261회, 최다) |
| `textMuted` | `#666666` | 보조 설명 |
| `textFaint` | `#999999` | 메타 라벨 `.label_box` |
| `textDisabled` | `#949494` | 종료 공고 제목 `.end .tit` |

### Surface & Line

| 토큰 | Hex | 원본 |
|---|---|---|
| `surface` | `#FFFFFF` | 기본 (487회) |
| `surfaceSubtle` | `#FDFDFD` | 정보 박스 `.etc_cont` |
| `surfaceAlt` | `#FAFAFA` | 섹션 구분 배경 |
| `border` | `#E6E6E6` | 정보 박스 테두리 |
| `borderSoft` | `#E8E8E8` | 목록 구분선 (dashed) |
| `borderStrong` | `#E1E5E6` | 입력 필드 |

### Semantic (원본에 없어 신규 정의)

SSUPath 는 마감 임박·정원 임박을 색으로 표시하지 않는다. 이 앱의 고유 기능이라
경고색을 새로 정한다.

| 토큰 | Hex | 역할 |
|---|---|---|
| `warning` | `#E8590C` | 마감 임박, 정원 임박 |
| `danger` | `#C92A2A` | 마감됨, 오류 |
| `favorite` | `#E64980` | 찜 하트 |

> `warning` 은 `statusOpen`(`#0D97FF`)과 색상환에서 충분히 멀어 색약 사용자도
> 구분 가능하다. 다만 **색에만 의존하지 않는다** — 7절 참조.

---

## 3. Typography Rules

**본문** `Noto Sans KR` — 원본이 100/300/400/500/600 다섯 웨이트를 로드한다.
**숫자·영문 강조** `Poppins` 600 — 원본이 이 용도로만 쓴다. D-day, 인원수에 적용.

| 역할 | 크기 | 웨이트 | 색 | 원본 근거 |
|---|---|---|---|---|
| `displayLarge` | 24 | 600 | `textStrong` | `font-size:24px` (31회) |
| `titleLarge` | 20 | 600 | `textStrong` | `.tit` 데스크톱 |
| `titleMedium` | 18 | 600 | `textStrong` | `.tit` 축소형 (107회) |
| `bodyLarge` | 16 | 400 | `textBody` | 194회 |
| `bodyMedium` | 15 | 400 | `textBody` | `.etc_cont li` (159회) |
| `bodySmall` | 14 | 400 | `textMuted` | **최다 287회 = 실질 기본** |
| `labelMedium` | 13 | 400 | `#FFFFFF` | pill 라벨 |
| `labelSmall` | 12 | 400 | `textFaint` | 캡션 (52회) |

**줄간격** — 제목 1.35, 본문 1.6. 한글은 라틴보다 넓은 행간이 필요하다.
**pill 라벨만 `line-height: 1`** (원본 명시).

**금지** — 400 미만 웨이트를 본문에 쓰지 않는다. 원본은 Thin/Light 를 로드하지만
장식용이고, 모바일 한글 가독성에서 100/300 은 읽기 어렵다.

---

## 4. Component Stylings

### Status Pill (원본 `.label_box > span`)

```
padding      : 5px 15px
border-radius: 50px          ← 완전한 pill
font-size    : 13px
font-weight  : 400
line-height  : 1
color        : #FFFFFF
background   : status 토큰
간격         : 우측 4px
```

### Info Card (원본 `.etc_cont`)

```
padding      : 12px 20px
border       : 1px solid #E6E6E6
border-radius: 10px
background   : #FDFDFD
font-size    : 15px
color        : #222222
```

상세 화면의 정원·마감 정보 블록에 그대로 쓴다.

### Notice Card (원본 `.lica_wrap > ul > li` 를 모바일로 번역)

원본은 카드가 아니라 **구분선으로 나뉜 목록**이다 (`padding: 30px 0` +
`border-top: 1px dashed #E8E8E8`). 모바일에서는 세로 여백 30px 이 과하므로:

```
padding      : 16px
divider      : 1px dashed #E8E8E8   ← dashed 유지. 원본의 특징
background   : #FFFFFF
elevation    : 0                     ← 그림자 없음. 구분선으로만 분리
tap ripple   : brandTeal 12%
```

**종료 상태** — 제목을 `#949494` 로 낮추고 라벨을 `#BCBCBC` 로. 숨기지 않는다.

### Button

| 종류 | 배경 | 글자 | 반경 |
|---|---|---|---|
| Primary | `brandNavy` | `#FFFFFF` | 5px |
| Secondary | `#FFFFFF` | `brandTeal` | 5px, 테두리 `brandTeal` |
| Disabled | `#E6E6E6` | `#999999` | 5px |

Primary 그림자 `0 4px 8px rgba(0,104,143,0.24)` — 원본 값 그대로. 회색이 아니라
**청록 기운이 있는 그림자**이며 이것이 SSUPath 특유의 질감이다.

### Navigation Bar

```
배경         : #FFFFFF
선택 아이콘   : brandNavy
미선택       : #999999
indicator    : brandTeal 12%
상단 경계선   : 1px solid #E8E8E8
```

---

## 5. Layout Principles

**간격 스케일** — 원본의 `padding/margin` 실측값에서 4의 배수만 추림.

```
xs  4      pill 사이
sm  8      아이콘-텍스트
md  12     카드 내부 세로
lg  16     카드 패딩, 화면 좌우
xl  20     정보 박스 좌우
2xl 24     섹션 사이
3xl 30     원본 목록 항목 여백 (데스크톱 전용)
```

**반경 스케일**

```
sm  3px    작은 요소 (원본 55회, 최다)
md  5px    버튼 (46회)
lg  10px   카드·정보 박스 (13회)
pill 50px  상태 라벨
```

원본 최다값이 3px 다. **거의 각진 인터페이스**이며 12px 이상 큰 반경은 쓰지 않는다.

**목록** — 카드를 띄우지 않고 dashed 구분선으로 나눈다. Material 기본
`Card` + `elevation` 을 쓰면 원본과 질감이 어긋난다.

**본문 최대폭** — 태블릿·웹에서 600px 이상 늘리지 않는다. 한글 한 줄이 길면 읽기 나쁘다.

---

## 6. Depth & Elevation

원본은 그림자를 거의 쓰지 않는다. 쓰는 곳도 극히 얕다.

| 레벨 | 값 | 용도 |
|---|---|---|
| 0 | 없음 | 목록 카드, 기본 표면 |
| 1 | `0 3px 8px rgba(0,0,0,0.05)` | 떠 있는 컨테이너 |
| 2 | `0 5px 15px 2px rgba(0,0,0,0.05)` | 모달, 바텀시트 |
| brand | `0 4px 8px rgba(0,104,143,0.24)` | Primary 버튼 |

**표면 위계는 그림자가 아니라 배경색과 선으로 만든다.**
`#FFFFFF` → `#FDFDFD` → `#FAFAFA` 순서로 낮아지고, 경계는 `#E6E6E6`/`#E8E8E8`.

---

## 7. Do's and Don'ts

### Do

- 상태는 **pill 라벨 + 색**으로 표시한다. SSUPath 에서 학생이 이미 익힌 규칙이다
- 종료 공고를 숨기지 말고 **흐리게** 표시한다 (`#949494` / `#BCBCBC`)
- 목록은 dashed 구분선으로 나눈다
- 숫자(인원, D-day)는 `Poppins` 600 으로 눈에 띄게 한다
- Primary 그림자에 브랜드 청록을 섞는다

### Don't

- ❌ **정원 미상(`capacity == null`)을 `0` 으로 표시하지 않는다.**
  `0/0` 은 마감으로 읽힌다. "정원 미정" 이라고 쓴다 → ADR-0003
- ❌ **마감 없음(`deadline == null`)을 "오늘 마감" 으로 표시하지 않는다.**
  "상시모집" 이라고 쓴다
- ❌ **경고를 색으로만 말하지 않는다.** 마감 임박은 색 + `D-2` 텍스트 + 아이콘
  세 가지를 함께 쓴다. 색약 사용자와 흑백 스크린샷에서도 읽혀야 한다
- ❌ 12px 이상 큰 반경, Material 기본 elevation, 그라디언트
- ❌ 400 미만 폰트 웨이트를 본문에
- ❌ 라벨 색을 임의로 바꾸지 않는다. 5개 status 토큰 안에서만 쓴다

---

## 8. Responsive Behavior

| 폭 | 레이아웃 |
|---|---|
| < 600 | 단일 열. 카드 좌우 여백 16 |
| 600–1023 | 단일 열 + 본문 최대폭 600 중앙 정렬 |
| ≥ 1024 | 좌 목록 / 우 상세 2분할 |

**터치 타깃 최소 48×48.** 하트 버튼은 아이콘이 24px 이어도 터치 영역은 48px 을 지킨다.

**축약 순서** — 폭이 줄면 이 순서로 뗀다: ① 요약 본문 → ② 대기자 수 →
③ 운영조직. **제목과 상태 라벨은 절대 떼지 않는다.**

**웹 알림 없음** — 웹은 FCM topic 구독을 지원하지 않는다. 목록만 동작하며 이는
버그가 아니다.

---

## 9. Agent Prompt Guide

### 빠른 참조

```
navy    #0E2767   teal    #00688F   cyan    #00A4CA
open    #0D97FF   waiting #43B5A4   closed  #BCBCBC
strong  #222222   body    #333333   muted   #666666   faint #999999
border  #E6E6E6   soft    #E8E8E8   subtle  #FDFDFD
warning #E8590C   danger  #C92A2A   favorite #E64980
```

```
반경  3 / 5 / 10 / 50(pill)      간격  4 / 8 / 12 / 16 / 20 / 24
폰트  Noto Sans KR (400·500·600) + Poppins 600 (숫자)
크기  12 / 13 / 14 / 15 / 16 / 18 / 20 / 24
```

### 프롬프트 예시

> SSUNoti 공고 카드를 만들어라. 흰 배경, 그림자 없음, 아래쪽에
> `1px dashed #E8E8E8` 구분선. 패딩 16. 제목은 18px/600/`#222222` 2줄 말줄임.
> 아래에 pill 라벨(반경 50, 패딩 5×15, 13px, 흰 글자): 모집중은 `#0D97FF`,
> 종료는 `#BCBCBC`. 정원은 `신청/정원` 을 Poppins 600 으로, 정원이 null 이면
> "정원 미정" 회색 라벨. 마감 3일 이내면 `#E8590C` 라벨에 알람 아이콘 + `D-2`.
> 마감이 null 이면 "상시모집" 청록 라벨. 우측에 48×48 터치 영역의 하트 버튼,
> 켜지면 `#E64980`.

### 절대 규칙

1. `capacity == null` → "정원 미정". 절대 `0` 아님
2. `deadline == null` → "상시모집". 절대 "오늘 마감" 아님
3. 경고는 색 + 텍스트 + 아이콘 세 겹
4. 라벨 글자는 흰색 고정
5. 목록에 그림자 쓰지 않음

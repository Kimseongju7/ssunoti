# SSUNoti Design System

> 기반: [Linear.app Design System](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/linear.app/DESIGN.md)
> 개정일: 2026-07-30

Linear 의 시스템 구조를 SSUNoti 에 옮긴 것이다. 원본을 그대로 쓰지 않고
세 곳을 의도적으로 바꿨다 — **명암 모드**, **상태 색 표현 방식**,
**한글 타이포그래피**. 바꾼 이유는 각 절에 적었다.

---

## 1. Visual Theme & Atmosphere

**성격** — 흰 캔버스 위에 짙은 회색 글자, 라벤더 강조 하나. 장식이 없고
정보가 주인공이다. 깊이는 그림자가 아니라 **표면 사다리 + 1px 실선**으로 만든다.

| 축 | 위치 |
|---|---|
| 모드 | **라이트.** 원본에서 바꾼 부분 ⓪ — 아래 참조 |
| 캔버스 | `#FFFFFF` (원본 Inverse Canvas) |
| 채도 | 극도로 낮음. 라벤더는 희소 자원 |
| 모서리 | 8px 기본. pill 은 상태 배지에만 |
| 그림자 | **없음.** 표면 단계와 실선으로만 위계를 만든다 |

### 원본에서 바꾼 부분 ⓪ — 명암 모드

Linear 원본은 *"Don't create a light-mode marketing version"* 이라고 명시하고
Known Limitations 에도 *"Light mode is not supported or specified"* 라고 적는다.

**이 프로젝트는 라이트 모드를 쓴다.** 학사 포털 사용자가 SSUPath(흰 배경)와
번갈아 보는 앱이라, 다크로 두면 두 화면을 오갈 때마다 눈이 적응해야 한다.

색을 임의로 지어내지 않기 위해 원본이 **문서화한 Inverse 토큰**을 기준으로 삼았다:
`Inverse Canvas #FFFFFF`, `Inverse Surface-1 #F5F6F6`, `Inverse Ink #000000`.
원본에 없는 중간 단계는 파생값이며 2절에 표시했다.

**유지되는 것** — 표면 사다리 구조, 그림자 없음, 라벤더의 희소성, 상태 점 방식,
반경·간격 스케일, 타입 스케일. 뒤집은 것은 명암뿐이다.

**이 앱에서의 의미** — 공고 목록은 텍스트 덩어리다. 배경이 조용할수록 제목이
읽힌다. 색을 뿌리는 대신 **상태를 작은 점 하나로** 말한다.

---

## 2. Color Palette & Roles

### Brand & Accent

| 토큰 | Hex | 역할 |
|---|---|---|
| `accent` | `#5E6AD2` | 브랜드, 주요 CTA, 포커스 링, 찜 활성 |
| `accentHover` | `#828FFF` | hover |
| `accentFocus` | `#5E69D1` | 포커스 아웃라인 (50% 투명도) |

> **라벤더는 희소 자원이다.** 브랜드 마크, 주요 상호작용, 포커스에만 쓴다.
> 카드 배경이나 섹션을 라벤더로 채우지 않는다.

### Surface Ladder (4단계. 건너뛰지 않는다)

| 토큰 | Hex | 출처 | 용도 |
|---|---|---|---|
| `canvas` | `#FFFFFF` | 원본 Inverse Canvas | 기본 배경, 목록 행 |
| `surface1` | `#F5F6F6` | 원본 Inverse Surface-1 | 카드, 정보 패널 |
| `surface2` | `#EDEEF0` | **파생** | 상태 배지, 강조 카드 |
| `surface3` | `#E7E8EB` | **파생** | 드롭다운 |
| `surface4` | `#E1E2E6` | **파생** | 가장 들린 표면 |

> 원본 `Inverse Surface-2` 는 `#F6F7F7` 로 `surface1` 과 1단위 차이다.
> 마케팅 타일에는 충분하지만 앱에서는 두 단계가 구분되지 않아 낮춰 잡았다.

### Hairlines (전부 파생)

| 토큰 | Hex | 용도 |
|---|---|---|
| `hairline` | `#E3E4E8` | 기본 1px 경계 · 목록 구분선 |
| `hairlineStrong` | `#D2D4DA` | 포커스 링 경계 |
| `hairlineTertiary` | `#C4C7CE` | 중첩 표면 경계 |

### Ink

| 토큰 | Hex | 용도 |
|---|---|---|
| `ink` | `#0D0E10` | 제목, 본문 주요 |
| `inkMuted` | `#3C4149` | 보조 메타 |
| `inkSubtle` | `#6B7280` | 3차 · 비선택 상태 |
| `inkTertiary` | `#9CA3AF` | 비활성, 각주, **종료 공고** |

> 원본 `Inverse Ink` 는 `#000000` 이지만 순수 검정을 쓰지 않았다.
> 캔버스를 순수 검정으로 쓰지 않는다는 원본 규칙을 뒤집어 적용한 것이다.

### Status Tags — 원본에서 바꾼 부분 ①

Linear 마케팅 규칙은 orange·pink·green 같은 2차 색상 도입을 금지한다.
그러나 원본 Known Limitations 가 명시한다 — *"Product UI color tags … reside in
in-product surfaces only"*. **SSUNoti 는 제품 UI다.**

다만 표현 방식을 Linear 식으로 바꾼다. 색을 면적으로 쓰지 않고 **점(dot) 하나로만**
쓴다. 배지 자체는 `surface2` 배경에 `inkMuted` 글자다.

| 토큰 | Hex | 의미 |
|---|---|---|
| `tagOpen` | `#2F80ED` | 모집중 |
| `tagAlways` | `#1E8E3E` | 상시모집 |
| `tagWarning` | `#D9730D` | 마감 임박 · 정원 임박 |
| `tagClosed` | `#9CA3AF` | 종료 · 마감됨 |

> 점은 6px 원. 배지 배경은 상태와 무관하게 항상 `surface2` 다.
> 이렇게 하면 목록에 색 덩어리가 생기지 않는다.
>
> 밝은 배경에서 읽히도록 다크 변형(`#4EA7FC` / `#27A644` / `#F2994A`)보다
> 어둡게 잡았다. 6px 점은 면적이 작아 대비가 부족하면 그냥 안 보인다.

---

## 3. Typography Rules

### 폰트 — 원본에서 바꾼 부분 ②

Linear 서체(Display/Text/Mono)는 독점이다. 원본이 오픈소스 대체를 허용한다:
Inter, Geist Sans, JetBrains Mono.

**문제는 Inter 에 한글이 없다는 것이다.**

| 용도 | 폰트 |
|---|---|
| 라틴·숫자 | `Inter` |
| 한글 | `Noto Sans KR` (폴백) |
| 숫자 강조 | `JetBrains Mono` — 정원·D-day |

### Type Scale

원본 값을 쓰되 **자간을 완화했다.** Linear 는 80px 에서 `-3.0px` 를 준다.
한글은 자모 간격이 이미 조밀해서 그 정도 음수 트래킹이면 글자가 뭉친다.

| 토큰 | 크기 | 웨이트 | 행간 | 자간(원본→적용) | 용도 |
|---|---|---|---|---|---|
| `displayMd` | 32 | 600 | 1.15 | -1.0 → **-0.6** | 화면 대제목 |
| `headline` | 24 | 600 | 1.20 | -0.6 → **-0.4** | 상세 제목 |
| `cardTitle` | 17 | 500 | 1.35 | -0.4 → **-0.2** | 공고 제목 |
| `subhead` | 16 | 400 | 1.45 | -0.2 → **0** | 리드 문단 |
| `body` | 15 | 400 | 1.55 | -0.05 → **0** | 기본 본문 |
| `bodySm` | 13 | 400 | 1.50 | 0 | 카드 본문, 푸터 |
| `caption` | 12 | 400 | 1.40 | 0 | 캡션, 메타, 배지 |
| `button` | 14 | 500 | 1.20 | 0 | 버튼 라벨 |
| `eyebrow` | 12 | 500 | 1.30 | **+0.4** | 분류 라벨 (양수 유지) |
| `mono` | 12 | 500 | 1.0 | 0 | 숫자 · D-day |

**핵심 원칙 유지** — 디스플레이는 600, 본문은 400. 그 사이를 섞지 않는다.
`eyebrow` 만 양수 자간을 써서 분류라는 성격을 드러낸다(원본 규칙 그대로).

한글 행간은 라틴보다 넓다 — 본문 1.55, 제목 1.15~1.35.

---

## 4. Component Stylings

### Status Badge (원본 `status-badge` 를 확장)

```
배경   : surface2  #EDEEF0     ← 상태와 무관하게 고정
글자   : inkMuted  #3C4149
타입   : caption (12px/400)
패딩   : 3px 8px  (원본 2px 8px 에서 터치 여유)
반경   : pill
점     : 6px 원, 좌측, 우측 여백 6px, 색 = status 토큰
```

### Notice Row (원본 `changelog-row`)

원본에 이미 목록 행 컴포넌트가 있다. 그대로 쓴다.

```
배경       : canvas #FFFFFF
글자       : ink #0D0E10
패딩       : 20px 16px   (원본 24px 0 을 모바일로 조정)
하단 경계선 : 1px #E3E4E8
```

**종료 상태** — 제목을 `inkTertiary` `#9CA3AF` 로 낮춘다. 숨기지 않는다.

### Info Card (원본 `feature-card`)

```
배경   : surface1 #F5F6F6
경계선 : 1px #E3E4E8
반경   : 12px
패딩   : 20px  (원본 24px 을 모바일로 조정)
```

### Buttons

| 종류 | 배경 | 글자 | 경계선 |
|---|---|---|---|
| Primary | `#5E6AD2` | `#FFFFFF` | 없음 |
| Secondary | `#FFFFFF` | `#0D0E10` | 1px `#E3E4E8` |
| Tertiary | `#FFFFFF` | `#0D0E10` | 없음 |

```
타입 : button (14px/500/1.20)
패딩 : 10px 14px   (원본 8px 14px 에서 터치 높이 확보)
반경 : 8px         ← pill 로 만들지 않는다
hover: #828FFF   pressed: #5E69D1
```

### Bottom Navigation (원본 `top-nav` 를 하단으로)

```
배경       : canvas #FFFFFF
상단 경계선 : 1px #E3E4E8
높이       : 56px
선택       : accent #5E6AD2 아이콘 + ink #0D0E10 라벨
비선택     : inkSubtle #6B7280
타입       : caption (12px/400)
```

### Favorite Toggle

```
비활성 : inkSubtle #6B7280, 외곽선 하트
활성   : accent #5E6AD2, 채운 하트
```

찜은 주요 상호작용이므로 라벤더를 쓴다. 분홍 같은 별도 색을 도입하지 않는다.

---

## 5. Layout Principles

### 간격 스케일 (원본 그대로)

```
xxs  4     점-텍스트
xs   8     배지 사이
sm   12    카드 내부 세로
md   16    행 좌우 패딩
lg   24    섹션 사이
xl   32    큰 구획
xxl  48    화면 상하 여백
```

### 반경 스케일 (원본 그대로)

```
xs   4px    작은 칩
sm   6px    인라인 태그
md   8px    버튼, 입력
lg   12px   카드
xl   16px   패널
pill 9999   상태 배지, 탭
```

### 컨테이너

| 폭 | 레이아웃 |
|---|---|
| < 768 | 1열 |
| 768–1023 | 1열 + 최대폭 720 중앙 |
| ≥ 1024 | 최대폭 1280, 좌 목록 / 우 상세 2분할 |

**여백 철학** — 구획은 여백이 아니라 **표면 단계와 실선**으로 나눈다.
같은 흰 배경 위에서 `surface1` 한 단계와 1px 실선이 경계를 만든다.

---

## 6. Depth & Elevation

**그림자를 쓰지 않는다.** 표면 사다리와 실선만으로 깊이를 만든다.

| 레벨 | 처리 | 적용 |
|---|---|---|
| 0 | 그림자·경계선 없음 | 본문, 목록 행 |
| 1 | `surface1` + 1px `hairline` | 카드, 정보 패널 |
| 2 | `surface2` + 1px `hairlineStrong` | 강조·hover 카드, 배지 |
| 3 | `surface3` 배경 | 하단 네비게이션, 드롭다운 |
| 4 | 2px `accentFocus` 아웃라인 (50%) | 포커스된 입력·버튼 |

단계를 건너뛰지 않는다. `canvas` 다음은 `surface1` 이지 `surface3` 이 아니다.

---

## 7. Do's and Don'ts

### Do

- 캔버스는 `#FFFFFF` 에 고정한다
- 라벤더는 **브랜드·주요 CTA·포커스·찜 활성**에만 쓴다
- 표면 4단계를 순서대로 쓴다
- 디스플레이 600 / 본문 400 조합을 지킨다
- 버튼 모서리는 8px
- 상태는 **작은 점 + 중립 배지**로 말한다
- 종료 공고를 숨기지 말고 `inkTertiary` 로 낮춘다

### Don't

- ❌ 카드나 섹션 배경을 라벤더로 채우지 않는다
- ❌ 순수 검정 `#000000` 을 글자색으로 쓰지 않는다
- ❌ 주요 버튼을 pill 로 만들지 않는다
- ❌ **`Center` 를 `bottomNavigationBar` 나 `appBar` 슬롯에 쓰지 않는다.**
  세로 공간을 전부 차지해 본문 높이가 0 이 된다. 폭만 제한하려면
  `Align(heightFactor: 1.0)` 을 쓴다
- ❌ 그라디언트·스포트라이트 효과를 넣지 않는다
- ❌ **한글에 -1.0px 이상의 음수 자간을 주지 않는다.** 글자가 뭉친다
- ❌ **정원 미상(`capacity == null`)을 `0` 으로 표시하지 않는다.**
  `0/0` 은 마감으로 읽힌다 → ADR-0003
- ❌ **마감 없음(`deadline == null`)을 "오늘 마감" 으로 표시하지 않는다.**
  "상시모집" 이라고 쓴다
- ❌ **경고를 색으로만 말하지 않는다.** 색 점 + `D-2` 텍스트 + 아이콘 세 겹

---

## 8. Responsive Behavior

| 이름 | 폭 | 조정 |
|---|---|---|
| Desktop | ≥1280 | 최대폭 1280, 2분할 |
| Tablet | 1024 | 2분할 진입 |
| Mobile-Lg | 768 | 1열, 최대폭 720 |
| Mobile | <480 | 1열, `displayMd` 32 → 24 |

**터치 규정** — 주요 버튼 ≥44px, 배지 ≥36px, 아이콘 버튼 터치 영역 44×44.

**축약 순서** — ① 요약 본문 → ② 대기자 → ③ 운영조직.
**제목과 상태 배지는 떼지 않는다.**

**웹 알림 없음** — 웹은 FCM topic 구독 미지원. 목록만 동작하며 버그가 아니다.

---

## 9. Agent Prompt Guide

### 빠른 참조

```
accent   #5E6AD2   hover #828FFF   focus #5E69D1
canvas   #FFFFFF   s1 #F5F6F6   s2 #EDEEF0   s3 #E7E8EB   s4 #E1E2E6
hairline #E3E4E8   strong #D2D4DA   tertiary #C4C7CE
ink      #0D0E10   muted #3C4149   subtle #6B7280   tertiary #9CA3AF
tag      open #2F80ED · always #1E8E3E · warning #D9730D · closed #9CA3AF
```

```
반경  4 / 6 / 8 / 12 / 16 / pill      간격  4 / 8 / 12 / 16 / 24 / 32 / 48
폰트  Inter + Noto Sans KR, 숫자는 JetBrains Mono
크기  12 / 13 / 14 / 15 / 16 / 17 / 24 / 32
```

### 프롬프트 예시

> SSUNoti 공고 목록 행을 만들어라. 배경 `#FFFFFF`, 그림자 없음, 하단
> `1px solid #E3E4E8`. 패딩 20×16. 제목은 17px/500/`#0D0E10`, 자간 -0.2,
> 2줄 말줄임. 아래에 상태 배지들: 배경은 전부 `#EDEEF0`, 글자 `#3C4149`
> 12px, pill, 패딩 3×8, 좌측에 6px 색 점 — 모집중 `#2F80ED`, 상시모집
> `#1E8E3E`, 마감임박 `#D9730D`, 종료 `#9CA3AF`. 정원은 `신청/정원` 을
> JetBrains Mono 로, null 이면 "정원 미정". 마감 3일 이내면 주황 점 +
> 알람 아이콘 + `D-2`. 우측에 44×44 터치 영역 하트, 켜지면 `#5E6AD2`.

### 절대 규칙

1. 캔버스는 `#FFFFFF`. 글자에 순수 검정을 쓰지 않는다
2. 라벤더는 브랜드·CTA·포커스·찜에만
3. 그림자 없음 — 표면 사다리 + 실선
4. 상태 배지 배경은 항상 `#EDEEF0`, 색은 점에만
5. `capacity == null` → "정원 미정". 절대 `0` 아님
6. `deadline == null` → "상시모집". 절대 "오늘 마감" 아님
7. 한글 음수 자간 -1.0px 초과 금지

# SSUNoti — 숭실대 비교과(SSUPath) 공고 알리미

모노레포 루트. 상세 문서는 아래를 따라갑니다.

| 문서 | 내용 |
|---|---|
| `ssunoti_server/CLAUDE.md` | 백엔드 아키텍처 · 파일 구조 · 구현 현황 · Firestore 설계 |
| `ssunoti_server/SSUPATH_URL_ANALYSIS.md` | SSUPath URL 구조 분석 |
| `ssunoti_server/docs/` | 크롤러 코드 문서, HTML 구조, 디버깅 기록 |
| `ssunoti_server/handover/` | 인계 문서 |
| `plan.md` | 초기 계획 |

## 구조

```
ssunoti/
├── ssunoti_server/    # Python 크롤러 + 스케줄러 (일부 구현)
└── ssunoti_flutter/   # Flutter 앱 (예정)
```

`[Python 크롤러] → [Firestore] ← [Flutter 앱]` / `[FCM 푸시] → [Flutter 앱]`

## 확정된 설계 결정

- **단일 수집 계정 구조** — 크롤링은 운영자 계정 하나로만 수행한다.
  사용자 학번·비밀번호는 수집하지도 보관하지도 않는다.
  찜하기는 앱 자체 DB 기능이며 SSUPath 계정과 무관하다.
  신청은 SSUPath 링크로 이동시킨다.
- 알림 3종: 신규 공고 등록 / 정원 임박 / 찜한 공고 마감 임박

## 주의

- `ssunoti_server/.env` 에 실계정 자격증명(`student_no`, `ssu_pw`)이 있다. 절대 커밋·출력 금지.
- `ssunoti_server/tests/` 는 SSUPath 에 실제 로그인·요청하는 통합 테스트를 포함한다.
  반복 실행 시 학교 서버에 부하가 간다.

<!-- ooo:START -->
<!-- ooo:VERSION:0.50.5 -->
# Ouroboros — Specification-First AI Development

> Before telling AI what to build, define what should be built.
> As Socrates asked 2,500 years ago — "What do you truly know?"
> Ouroboros turns that question into an evolutionary AI workflow engine.

Most AI coding fails at the input, not the output. Ouroboros fixes this by
**exposing hidden assumptions before any code is written**.

1. **Socratic Clarity** — Question until ambiguity ≤ 0.2
2. **Ontological Precision** — Solve the root problem, not symptoms
3. **Evolutionary Loops** — Each evaluation cycle feeds back into better specs

```
Interview → Seed → Execute → Evaluate
    ↑                           ↓
    └─── Evolutionary Loop ─────┘
```

## ooo Commands

Each command loads its agent/MCP on-demand. Details in each skill file.

| Command | Loads |
|---------|-------|
| `ooo` | — |
| `ooo interview` | `ouroboros:socratic-interviewer` |
| `ooo seed` | `ouroboros:seed-architect` |
| `ooo run` | MCP required |
| `ooo evolve` | MCP: `evolve_step` |
| `ooo evaluate` | `ouroboros:evaluator` |
| `ooo unstuck` | `ouroboros:{persona}` |
| `ooo status` | MCP: `session_status` |
| `ooo setup` | — |
| `ooo help` | — |

## Agents

Loaded on-demand — not preloaded.

**Core**: socratic-interviewer, ontologist, seed-architect, evaluator,
wonder, reflect, advocate, contrarian, judge
**Support**: hacker, simplifier, researcher, architect
<!-- ooo:END -->

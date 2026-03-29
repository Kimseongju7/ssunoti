# Claude Code 커스텀 슬래시 명령어 가이드

**작성일**: 2026-03-19
**목적**: 프로젝트에서 활용한 Claude Code 커스텀 명령어 정리 (면접 준비용)

---

## 개요

Claude Code는 `.claude/commands/` 디렉토리에 마크다운 파일을 작성하면 `/명령어` 형태로 호출 가능한 **커스텀 슬래시 명령어**를 만들 수 있다. 이 프로젝트에서는 반복적인 개발 워크플로우를 자동화하기 위해 6개의 명령어를 직접 정의하여 활용했다.

```
.claude/
└── commands/
    ├── commit.md          # Git 커밋 자동화
    ├── handover.md        # 세션 인수인계 문서 생성
    ├── make-document.md   # 코드/개념 문서 자동 생성
    ├── question.md        # Q&A 자동 저장
    ├── release.md         # 버전 릴리즈 자동화
    └── update-docstring.md # Docstring 자동 업데이트
```

---

## 명령어 상세

### 1. `/commit` — Git 커밋 자동화

**파일**: `.claude/commands/commit.md`

**목적**: 변경 사항을 분석해 Conventional Commits 형식의 커밋 메시지를 자동 생성하고 커밋을 진행한다.

**사용법**:
```
/commit
/commit --push        # 커밋 후 push까지
/commit --no-verify   # pre-commit hook 무시
```

**동작 흐름**:
1. `git status`, `git diff`, `git diff --cached`로 변경 사항 파악
2. 변경 내용을 분석해 커밋 메시지 자동 생성
3. 사용자에게 메시지 확인 요청 (수정/취소 가능)
4. staging되지 않은 파일 처리 여부 확인
5. 커밋 실행 → `--push` 플래그 시 push까지 수행

**커밋 메시지 형식**:
```
<type>: <subject>

<body (optional)>
```

| type | 의미 |
|------|------|
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 |
| `refactor` | 리팩토링 |
| `test` | 테스트 추가/수정 |
| `chore` | 설정, 의존성 등 기타 |

**왜 만들었나**: 커밋 메시지 컨벤션을 일관되게 유지하고, 변경 사항 분석을 매번 수동으로 하는 번거로움을 줄이기 위해.

---

### 2. `/handover` — 세션 인수인계 문서 생성

**파일**: `.claude/commands/handover.md`

**목적**: 작업 세션 종료 시 다음 세션에서 맥락을 이어받을 수 있도록 인수인계 문서를 자동 생성한다.

**사용법**:
```
/handover
```

**생성 파일**: `handover/YYYY-MM-DD-HHMM.md`

**문서 구성**:
- 세션 요약
- 완료된 작업 목록
- 수정/생성된 파일 목록
- 미완료 작업 (체크리스트)
- 다음 세션을 위한 메모
- 현재 프로젝트 상태 (빌드/테스트 통과 여부)
- 기술적 의사결정 기록

**CLAUDE.md와의 연동**:
```markdown
## Session Initialization
At the start of every new session:
1. Check for handover documents in `handover/` directory
2. Read the latest handover document
3. Summarize the previous session to the user in Korean
```

→ 세션 시작 시 Claude가 자동으로 이전 인수인계 문서를 읽고 요약해준다.

**왜 만들었나**: Claude Code는 세션이 끊기면 이전 대화 맥락을 잃는다. `/handover`로 작업 상태를 문서화해두면 새 세션에서 즉시 이어서 작업할 수 있다.

---

### 3. `/make-document` — 문서 자동 생성

**파일**: `.claude/commands/make-document.md`

**목적**: 소스 파일 또는 개념/주제에 대한 문서를 자동으로 생성한다.

**사용법**:
```
/make-document src/browser.py         # 코드 문서화
/make-document XPath 문법              # 개념 문서화
/make-document innerHTML과 outerHTML 차이
```

**케이스 분기**:

| 입력 유형 | 저장 위치 | 예시 |
|----------|----------|------|
| 파일 경로 (`.py`, `.js` 등) | `document/code/<filename>.md` | `document/code/browser.py.md` |
| 개념/주제 (텍스트) | `document/guide/<topic>.md` | `document/guide/xpath-syntax.md` |

**코드 문서 포함 내용**:
- 목적, 개요, 주요 구성요소
- 의존성 (이 파일이 의존하는 것 / 이 파일에 의존하는 것)
- 사용 예시, 주의사항

**가이드 문서 포함 내용**:
- 개요, 상세 설명, 사용법, 코드 예시, 주의사항

**왜 만들었나**: 코드를 작성할 때마다 문서를 수동으로 작성하는 것은 번거롭다. 코드 분석 후 구조화된 문서를 자동 생성함으로써 문서화 비용을 줄였다.

---

### 4. `/question` — Q&A 자동 저장

**파일**: `.claude/commands/question.md`

**목적**: 개발 중 생기는 질문에 답변하고, 해당 Q&A를 FAQ로 자동 저장한다.

**사용법**:
```
/question undetected-chromedriver가 봇 탐지를 우회하는 원리는?
/question XPath와 CSS Selector의 차이는?
```

**생성 파일**: `faq/YYYY-MM-DD-brief-topic.md`

**파일 구조**:
```markdown
# [주제]

**Date**: YYYY-MM-DD HH:MM
**Tags**: [tag1, tag2]

## Question
[원본 질문]

## Answer
[상세 답변]

## Related Documents
- [관련 링크]
```

**왜 만들었나**: 같은 질문을 반복하지 않기 위해. 개발하면서 생기는 궁금증을 자동으로 문서화해 지식 베이스를 쌓는다.

---

### 5. `/release` — 버전 릴리즈 자동화

**파일**: `.claude/commands/release.md`

**목적**: 버전 번호 변경, git 태그 생성 등 릴리즈 과정을 자동화한다.

**사용법**:
```
/release 0.2.0             # 버전 업데이트 + 태그 생성
/release 0.2.0 --push      # 태그까지 push
/release 0.2.0 --no-commit # 파일만 수정 (git 작업 없음)
```

**자동으로 업데이트되는 파일**:

| 파일 | 변경 내용 |
|------|----------|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `src/__init__.py` | `__version__ = "X.Y.Z"` |
| `README.md` | `@vX.Y.Z` (git install URL) |

**동작 흐름**:
1. semver 형식 검증 (X.Y.Z)
2. 모든 관련 파일에서 버전 업데이트
3. 변경 diff 보여주고 사용자 확인 요청
4. `chore: bump version to X.Y.Z` 커밋 생성
5. `vX.Y.Z` annotated 태그 생성
6. `--push` 시 push + tags push

**릴리즈 전 체크리스트** (명령어가 자동으로 안내):
- [ ] 모든 테스트 통과
- [ ] 커밋되지 않은 변경사항 없음
- [ ] main 브랜치에 있는지 확인

**왜 만들었나**: 릴리즈 시 여러 파일의 버전을 일일이 수정하고 태그를 만드는 과정에서 실수가 발생하기 쉽다. 이를 자동화해 일관성을 보장한다.

---

### 6. `/update-docstring` — Docstring 자동 업데이트

**파일**: `.claude/commands/update-docstring.md`

**목적**: 코드 변경 후 Docstring을 코드에 맞게 자동으로 추가/수정한다.

**사용법**:
```
/update-docstring src/browser.py     # 단일 파일
/update-docstring src/*.py           # glob 패턴
/update-docstring src/**/*.py        # 재귀적
```

**동작 흐름**:
1. 파일의 모든 클래스·메서드 파악
2. Docstring 상태 확인:
   - 없으면 → 새로 생성
   - 코드와 맞지 않으면 → 업데이트
   - 정확하면 → 유지
3. 변경 완료 후 리포트 (추가/수정/유지 건수)

**Google Style Docstring 형식** (CLAUDE.md 규칙):
```python
def method(self, arg1: str, arg2: int = 10) -> bool:
    """간단한 설명

    Args:
        arg1: 첫 번째 인자 설명
        arg2: 두 번째 인자 설명. 기본값 10

    Returns:
        반환값 설명

    Raises:
        ValueError: 발생 조건

    Example:
        >>> result = obj.method("test")
        >>> print(result)
    """
```

**왜 만들었나**: 코드를 수정할 때마다 Docstring을 수동으로 업데이트하는 것을 자주 잊어버린다. 명령어 한 번으로 전체 파일의 Docstring을 최신 상태로 유지할 수 있다.

---

## 커스텀 명령어 작성 방법

Claude Code에서 커스텀 슬래시 명령어를 만드는 방법:

1. `.claude/commands/` 디렉토리 생성
2. `<command-name>.md` 파일 작성
3. 파일 내에 명령어의 동작 방식을 자연어로 기술
4. `/command-name`으로 호출

**핵심 원리**: Claude가 마크다운 파일의 Instructions 섹션을 읽고 그대로 수행한다. 별도의 코드 작성 없이 자연어 명세만으로 자동화가 가능하다.

```markdown
# Command Name

## Usage
/command-name $ARGUMENTS

## Instructions
When this command is invoked:
1. Do this first
2. Then do this
3. Finally do this
```

---

## 워크플로우에서의 활용 패턴

```
개발 중
  └─ 질문 생길 때    → /question <질문>       → faq/ 자동 저장
  └─ 코드 작성 후    → /update-docstring      → docstring 최신화
  └─ 파일 문서화     → /make-document         → document/ 생성

커밋 시
  └─ 변경사항 커밋   → /commit [--push]       → 메시지 자동 생성

릴리즈 시
  └─ 버전 배포       → /release X.Y.Z [--push] → 태그까지 자동화

세션 종료 시
  └─ 작업 마무리     → /handover              → handover/ 저장
  └─ 다음 세션 시작  → Claude가 자동으로 이전 handover 읽고 요약
```

---

**최종 수정일**: 2026-03-19

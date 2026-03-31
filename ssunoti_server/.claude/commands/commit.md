# Commit

변경 사항을 자동으로 분석해서 논리적 단위로 나누어 여러 커밋을 생성합니다.
`git add` 없이 실행해도 자동으로 스테이징합니다.

## Usage
/commit [$ARGUMENTS]

## Arguments
- Optional flags:
  - `--push`: 모든 커밋 완료 후 자동으로 push 진행
  - `--no-verify`: Pre-commit hook 무시

## Instructions
When this command is invoked:

1. **변경 사항 전체 파악**:
   - `git status` 실행해서 모든 untracked/modified/deleted 파일 확인
   - `git diff` 로 각 파일의 실제 변경 내용 확인
   - `.env`, `credentials`, `serviceAccountKey.json` 등 민감한 파일이 포함되어 있으면 경고 후 staging에서 제외

2. **논리적 커밋 단위로 그룹 분류**:
   변경된 파일들을 아래 기준으로 여러 그룹으로 나눔. 하나의 그룹 = 하나의 커밋.
   - **같은 목적의 변경**끼리 묶기 (예: 기능 추가, 문서 수정, 테스트, 설정 변경)
   - **서로 다른 type**은 반드시 분리 (feat와 docs를 한 커밋에 묶지 않음)
   - **의존 관계**가 있는 파일은 같은 커밋으로 (예: 소스 변경 + 해당 테스트)
   - 변경이 하나의 논리적 작업이면 커밋 1개도 가능

   그룹 분류 예시:
   - 그룹 A: `feat` — src/crawler.py, tests/test_crawler.py
   - 그룹 B: `docs` — CLAUDE.md, plan.md
   - 그룹 C: `chore` — pyproject.toml

3. **커밋 계획 제시 및 사용자 확인**:
   분류한 그룹과 각 커밋 메시지 초안을 한눈에 보여주기:
   ```
   [커밋 1/3] feat: ...
     파일: src/crawler.py, tests/test_crawler.py

   [커밋 2/3] docs: ...
     파일: CLAUDE.md, plan.md

   [커밋 3/3] chore: ...
     파일: pyproject.toml
   ```
   사용자에게 확인 요청. "어", "ㅇ", "응", "yes", "y", "ok" 등 긍정 응답이면 바로 진행.
   수정 요청이 있으면 반영 후 재확인.

4. **순서대로 커밋 실행**:
   각 그룹에 대해 순서대로:
   - `git add <해당 파일들>` 실행
   - `git commit -m "..."` 실행 (Co-Authored-By 줄 없이)
   - 커밋 hash 출력
   - Pre-commit hook 실패 시: 에러 내용 보여주고 수정 후 새 커밋 생성 (amend 금지)

5. **Push** (only if `--push` flag):
   - 모든 커밋 완료 후 `git push` 실행

6. **결과 요약**:
   - 생성된 커밋 수 및 각 hash 표시
   - `--push` 사용하지 않았으면 push 명령어 제시

## Commit Message Format

```
<type>: <subject>

<body (optional)>
```

- Type: `feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore`
- Subject: 한글 명령조 (예: "크롤러 로그인 기능 추가")
- Co-Authored-By 줄 절대 추가하지 않음

## Important Notes

- **git add 자동 처리**: 사용자가 staging하지 않아도 커밋 실행 전 자동으로 `git add`
- **Never use --amend**: 새로운 commit만 생성
- **민감 파일 제외**: `.env`, `*Key.json`, `*secret*`, `credentials*` 파일은 staging 제외 후 경고
- **Co-Authored-By 금지**: 커밋 메시지에 절대 포함하지 않음

## Error Handling

- No changes: "변경사항이 없습니다" 메시지 표시
- Hook failure: 에러 내용 표시 후 수정 방법 제시
- Push failure: 로컬 변경사항은 유지하고 push 실패 원인 설명

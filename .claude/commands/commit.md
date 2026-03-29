# Commit

변경 사항을 자동으로 분석해서 commit message를 생성하고 commit을 진행합니다.

## Usage
/commit [$ARGUMENTS]

## Arguments
- Optional flags:
  - `--push`: Commit 후 자동으로 push 진행
  - `--no-verify`: Pre-commit hook 무시

## Instructions
When this command is invoked:

1. **변경 사항 확인**:
   - `git status` 실행해서 untracked/modified 파일 확인
   - `git diff` 실행해서 staged 변경사항 확인
   - `git diff --cached` 실행해서 unstaged 변경사항 확인
   - 변경 파일들을 사용자에게 보여줌

2. **Commit message 생성**:
   - 변경 사항을 분석해서 자동으로 commit message 작성
   - 다음 형식 따르기:
     ```
     <type>: <subject>

     <body (optional)>
     ```
   - Type 선택:
     - `feat`: 새로운 기능
     - `fix`: 버그 수정
     - `docs`: 문서 수정
     - `style`: 코드 스타일 (포맷, 들여쓰기 등)
     - `refactor`: 코드 리팩토링
     - `perf`: 성능 개선
     - `test`: 테스트 추가/수정
     - `chore`: 기타 (설정, 의존성 등)
   - Subject는 명령조 사용 (e.g., "add feature", "fix bug")
   - 한글 작성 가능

3. **사용자 확인**:
   - 생성된 commit message 보여주기
   - 사용자에게 확인 요청
   - 수정하고 싶으면 수정안 입력받기
   - 취소 옵션 제공

4. **Staging 처리**:
   - 아직 staged 되지 않은 파일 있으면 물어보기
   - 전체 추가할지 선택적 추가할지 확인

5. **Commit 실행**:
   - `git commit -m "..."` 실행
   - Pre-commit hook 실패 시 처리:
     - 에러 메시지 보여주기
     - hook 문제 수정 후 새로운 commit 만들기 제안 (amend 금지)

6. **Push** (only if `--push` flag):
   - `git push` 실행
   - 성공 메시지 출력

7. **결과 요약**:
   - Commit hash 표시
   - Commit message 재확인
   - 변경된 파일 수
   - `--push` 사용하지 않았으면 push 명령어 제시

## Examples

### Basic commit
```
/commit
```
변경사항 분석 후 commit message 생성 및 commit

### Commit with push
```
/commit --push
```
Commit 후 바로 push까지 진행

### Skip pre-commit hook
```
/commit --no-verify
```
Pre-commit hook 무시하고 commit

## Important Notes

- **Never use --amend**: 새로운 commit을 만들어야 함 (이전 commit 손상 방지)
- **Check for secrets**: Commit 전에 민감한 파일(.env, credentials 등) 포함되지 않았는지 확인
- **Preserve exact messages**: 사용자가 제시한 commit message 형식 정확히 따르기
- **Git safety**: 모든 git 명령어는 안전하게 실행 (destructive 명령어 피하기)

## Error Handling

- No changes: "변경사항이 없습니다" 메시지 표시
- Hook failure: 에러 내용 표시 후 수정 방법 제시
- Push failure: 로컬 변경사항은 유지하고 push 실패 원인 설명
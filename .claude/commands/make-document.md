# Make Document

Create documentation for a file or a topic/concept.

## Usage
/make-document <filepath or request>

## Instructions

When this command is invoked, determine the input type and act accordingly:

### Case 1: File Path or Filename (has file extension like .py, .js, .md, etc.)

If the input looks like a file path or filename with extension:

1. Read and analyze the specified file thoroughly
2. Create a documentation file in `document/code/` directory
3. Filename: `<original-filename>.md` (e.g., `browser.py.md`)
4. The documentation should include:
   - **목적**: 파일의 역할과 존재 이유
   - **개요**: 기능에 대한 고수준 설명
   - **주요 구성요소**: 주요 함수, 클래스 설명
   - **의존성**: 이 파일이 의존하는 것과 이 파일에 의존하는 것
   - **사용 예시**: 주요 기능 사용법
   - **주의사항**: 엣지 케이스, 고려사항
   - **최종 수정일**: 현재 날짜

### Case 2: Topic/Concept Request (no file extension, plain text)

If the input is a word, phrase, or request (e.g., "@property 데코레이터에 관해 설명해 줘"):

1. Understand the topic or concept being requested
2. Create a documentation file in `document/guide/` directory
3. Filename: Choose an appropriate descriptive name in English (e.g., `python-property-decorator.md`, `xpath-syntax.md`)
4. The documentation should include:
   - **개요**: 개념에 대한 간단한 설명
   - **상세 설명**: 개념에 대한 자세한 설명
   - **사용법**: 어떻게 사용하는지
   - **예시**: 코드 예시 또는 실제 사용 예
   - **주의사항**: 알아야 할 점, 흔한 실수
   - **관련 자료**: 관련 개념이나 참고 링크 (선택사항)
   - **최종 수정일**: 현재 날짜

## Common Rules

- All content must be written in **Korean**
- Use clear, concise language suitable for developers
- Include code snippets where helpful
- Format in Markdown
- Create the directory if it doesn't exist

## Examples

### File Documentation
```
/make-document src/browser.py
```
Creates `document/code/browser.py.md`

### Concept Documentation
```
/make-document @property 데코레이터에 관해 설명해 줘
```
Creates `document/guide/python-property-decorator.md`

```
/make-document XPath 문법
```
Creates `document/guide/xpath-syntax.md`

```
/make-document innerHTML과 outerHTML 차이
```
Creates `document/guide/innerhtml-vs-outerhtml.md`
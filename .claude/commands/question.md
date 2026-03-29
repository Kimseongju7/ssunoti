# Question

Answer a question and automatically record both the question and answer in the FAQ directory.

## Usage
/question <your question>

## Instructions
When this command is invoked:

1. Answer the user's question thoroughly and clearly in Korean
2. After providing the answer, automatically create a FAQ record:
   - Create a new markdown file in the `faq/` directory
   - Filename format: `YYYY-MM-DD-brief-topic.md`
   - All content in the file must be written in Korean
   - Include: title, original question, complete answer, timestamp, tags

3. File structure:
```markdown
# [Topic]

**Date**: YYYY-MM-DD HH:MM
**Tags**: [tag1, tag2]

## Question
[Original question]

## Answer
[Complete answer]

## Related Documents
- [Links if any]
```

4. Create `faq/` directory if it doesn't exist
5. Use descriptive filenames for easy searching
6. Add appropriate tags (#config, #bug, #feature, etc.)

## Example
```
/question How does the authentication system work?
```

This will:
1. Provide detailed answer in Korean
2. Create `faq/2026-01-21-authentication-system.md` with Q&A in Korean
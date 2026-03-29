# Handover

Create a handover document for session end.

## Usage
/handover

## Instructions
When this command is invoked:

1. **Create a handover document** in `handover/` directory:
   - Filename: `YYYY-MM-DD-HHMM.md`
   - All content must be written in Korean

2. **Document structure**:
```markdown
# Handover Document

**Date**: YYYY-MM-DD HH:MM
**Session Period**: [start] ~ [end]

## Summary
[Brief summary of session work]

## Completed Tasks
- [Task 1]
- [Task 2]

## Modified Files
- `path/to/file.py`: [changes]

## Created Files
- `path/to/newfile.py`: [purpose]

## Pending Tasks
- [ ] [Task 1]
- [ ] [Task 2]

## Notes
- [Important notes for next session]

## Current Status
- Project: [normal/has errors/needs testing]
- Build: [success/fail/not run]
- Tests: [pass/fail/not run]

## Related Documents
- [Links]

## Technical Decisions
- [Important decisions and reasons]
```

3. **Content guidelines**:
   - Be specific and actionable
   - Include file paths
   - Highlight blockers or issues
   - Note dependencies or waiting items

4. Create `handover/` directory if it doesn't exist

5. After creating: confirm completion and show file path

## Example
```
/handover
```

This will:
1. Analyze current session's work
2. Create `handover/2026-01-21-1430.md` with handover info in Korean
3. Confirm completion
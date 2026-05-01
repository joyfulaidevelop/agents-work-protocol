# Bug Triage Skill

## Name

bug-triage

## Description

Bug classification, severity assessment, category assignment, and routing to the appropriate handler.

## Trigger Conditions

- New bug reported
- Bug needs classification
- Bug category is unclear
- Periodic bug review/triage session

## Steps

1. **Reproduce** (if possible)
   - Verify the bug can be reproduced
   - Document reproduction steps
   - If not reproducible, mark as `wontfix` with note

2. **Classify Category**
   - `code`: Logic error, crash, wrong output → Backend Engineer
   - `design`: UX flow issue, feature behavior problem → Product Designer
   - `performance`: Slow, memory leak, resource exhaustion → Backend Engineer
   - `security`: Vulnerability, auth bypass, injection → Reviewer
   - `compatibility`: Cross-platform/browser issues → Test Engineer

3. **Assess Severity**
   - `critical`: System down, data loss, security breach
   - `high`: Major feature broken, no workaround
   - `medium`: Feature partially broken, workaround exists
   - `low`: Cosmetic issue, minor inconvenience

4. **Assign**
   - Route to appropriate agent based on category
   - Use `bugs_cli.py update <id> --assigned-to <agent>`

5. **Update Bug**
   ```bash
   python bugs_cli.py update <id> --status confirmed --assigned-to <agent>
   ```

## Resources

- `bugs/BUGS.md` — bug workflow documentation
- `bugs/bugs_cli.py` — bug management CLI

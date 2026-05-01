# Code Review Skill

## Name

code-review

## Description

Structured code review with checklist, severity classification, and actionable feedback output.

## Trigger Conditions

- User requests code review
- PR needs review
- Security audit required
- Pre-merge quality gate

## Steps

1. **Gather Context**
   - Read the changed files
   - Read related test files
   - Check `memories/architecture.md` for architectural context

2. **Review Checklist**
   - [ ] Correctness: Does the code do what it's supposed to?
   - [ ] Security: Any injection, auth, or data exposure issues?
   - [ ] Performance: Obvious performance problems?
   - [ ] Error handling: Are errors handled properly?
   - [ ] Naming: Clear variable/function names?
   - [ ] DRY: Unnecessary duplication?
   - [ ] Test coverage: Are there tests for the changes?

3. **Classify Issues**
   - **Critical**: Security vulnerabilities, data loss risks, crashes
   - **Major**: Logic errors, missing error handling, performance issues
   - **Minor**: Style issues, naming improvements, minor refactoring
   - **Suggestion**: Nice-to-have improvements

4. **Output Report**
   - Use the reviewer agent's output format
   - Include file paths and line numbers
   - Provide fix suggestions, not just problem descriptions

## Resources

- `resources/review-checklist.md` — detailed checklist (create as needed)

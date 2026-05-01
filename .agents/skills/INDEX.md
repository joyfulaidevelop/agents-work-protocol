# Skills Index

> Route index for skills. Load SKILL.md only when the skill is needed.

| Skill | Directory | Description | Load When |
|-------|-----------|-------------|-----------|
| Code Review | `code-review/` | Structured code review with checklist and output format | Reviewing code, PR review, security audit |
| Bug Triage | `bug-triage/` | Bug classification, severity assessment, assignment | Bug reported, bug needs classification |
| Plan Management | `plan-management/` | Plan creation, status tracking, archival | Creating plan, updating plan status, plan archival |

## Loading Policy

Each skill directory contains:
- `SKILL.md` — full skill definition (load on match)
- `scripts/` — executable scripts
- `resources/` — templates and static resources

Read `INDEX.md` first. Only enter a skill directory and read `SKILL.md` when the task matches the "Load When" condition.

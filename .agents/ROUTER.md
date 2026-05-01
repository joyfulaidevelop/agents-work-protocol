# ROUTER.md

Spec Version: 0.1.0

## Task Routing Table

| User Intent | Read First | Then Maybe Read | Use Skill | Delegate To |
|---|---|---|---|---|
| New feature development | `roadmaps/ROADMAP.md`, `todo/` CLI | `plans/INDEX.md`, `memories/architecture.md` | plan-management, code-review | product-designer, backend-engineer |
| Bug report | `bugs/BUGS.md` | `bugs_cli.py query open` | bug-triage | test-engineer |
| Design dispute | `memories/decisions.md` | `roadmaps/ROADMAP.md` | — | product-designer |
| Code review | `prompts/INDEX.md` → reviewer.md | `skills/code-review/SKILL.md` | code-review | reviewer |
| Project memory query | `memories/MEMORY.md` | matched child memory file | — | — |
| Status check | `todo/` CLI, `plans/INDEX.md` | `bugs_cli.py query open` | — | — |
| DevOps / deployment | `prompts/INDEX.md` → devops-engineer.md | relevant skill SKILL.md | — | devops-engineer |
| Test planning | `prompts/INDEX.md` → test-engineer.md | `bugs_cli.py query open` | — | test-engineer |

## Loading Policy

1. Always read INDEX / README / MANIFEST files first.
2. Load full content only after confirming the task matches a resource.
3. Query SQLite databases exclusively through their CLI scripts.
4. NEVER unconditionally read `chats.sqlite` or dump full chat history.
5. Sub-agent prompts are loaded only at delegation time.

## Escalation Rules

- If a task doesn't match any route → respond directly or ask user for clarification.
- If multiple sub-agents could handle a task → prefer the most specific one.
- If a sub-agent fails → retry once with additional context, then escalate to user.

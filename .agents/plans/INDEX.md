# Plans Index

> Route index for active plans. Check this before creating a new plan to avoid duplicates.

## Status Values

| Status | Meaning |
|--------|---------|
| `new` | Plan created, not yet started |
| `working` | An agent has claimed this plan |
| `blocked` | Plan is waiting on a dependency |
| `review` | Plan output is ready for review |
| `done` | Plan completed — move to `archive/done/` |
| `cancel` | Plan cancelled — move to `archive/cancel/` |

## Naming Convention

```
YYYY-MM-DD_plan-name_status.md
```

## Active Plans

<!-- Add active plans here as they are created. Example:
- `2026-05-01_auth-refactor_new.md` — Refactor authentication middleware (owner: none)
-->

_No active plans yet._

## Archive

Completed plans move to `archive/done/`. Cancelled plans move to `archive/cancel/`.

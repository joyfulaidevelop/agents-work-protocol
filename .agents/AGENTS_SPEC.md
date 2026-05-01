# AGENTS_SPEC.md

> The `.agents/` Directory Specification — how this system works, for humans and advanced agents.

Spec Version: 0.1.0

---

## 1. Purpose

`.agents/` is a project-level directory that defines how AI agents discover, coordinate, and manage work. It acts as an agent-native context operating system: bootstrapping, routing, state management, and inter-agent coordination all live here.

## 2. Design Principles

### 2.1 Three-Tier Context Disclosure

The system follows a strict loading hierarchy to prevent context window pollution:

| Tier | Name | Content | When Loaded |
|------|------|---------|-------------|
| 0 | Bootstrap Hook | `AGENTS.md` | Automatically on agent start |
| 1 | Route Index | `SOUL.md`, `ROUTER.md`, `MANIFEST.yaml` | Immediately after bootstrap |
| 2 | Task Content | Prompts, skills, memories, plans, bugs, etc. | Only when a task requires it |

### 2.2 Route-Then-Load

Agents must never scan or load the entire `.agents/` directory. The correct pattern is:

1. Read the index / manifest for the relevant resource category.
2. Determine if the current task needs a specific resource.
3. Load only the matched resource.

### 2.3 State Via Database, Not Files

Transactional state (bugs, todos, chat logs) is stored in SQLite and accessed through CLI scripts. This prevents file-based conflicts when multiple agents work concurrently.

### 2.4 Files Are Documents, Not State

Plans, memories, and roadmaps are files because they benefit from human readability and version control. They use YAML frontmatter for machine-parseable metadata.

## 3. Directory Layout

```
.agents/
├── AGENTS.md              # Auto-loaded bootstrap hook
├── SOUL.md                # Primary agent role, work loop, discipline
├── ROUTER.md              # Human-readable task routing table
├── MANIFEST.yaml          # Machine-readable resource index
├── AGENTS_SPEC.md         # This file — the spec document
├── VERSION                # Spec version string
│
├── prompts/               # Sub-agent prompt definitions
│   ├── INDEX.md           #   Route index for sub-agents
│   ├── product-designer.md
│   ├── backend-engineer.md
│   ├── test-engineer.md
│   ├── devops-engineer.md
│   └── reviewer.md
│
├── skills/                # Reusable skill definitions
│   ├── INDEX.md           #   Route index for skills
│   ├── code-review/
│   │   ├── SKILL.md       #   Skill definition
│   │   ├── scripts/
│   │   └── resources/
│   ├── bug-triage/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── resources/
│   └── plan-management/
│       ├── SKILL.md
│       ├── scripts/
│       └── resources/
│
├── memories/              # Project memory hierarchy
│   ├── MEMORY.md          #   Root index (≤1KB)
│   ├── project.md
│   ├── architecture.md
│   ├── user-preferences.md
│   └── decisions.md
│
├── plans/                 # Task plans with status tracking
│   ├── INDEX.md           #   Current plans index
│   ├── archive/
│   │   ├── done/
│   │   └── cancel/
│   └── YYYY-MM-DD_plan-name_status.md
│
├── bugs/                  # Bug tracking system
│   ├── BUGS.md            #   Bug workflow documentation
│   ├── bugs.sqlite        #   Bug database
│   ├── bugs_cli.py        #   CLI for bug CRUD operations
│   └── archive/           #   Closed bug attachments
│
├── todo/                  # Task/todo tracking system
│   ├── TODO.md            #   Todo workflow documentation
│   ├── todo.sqlite        #   Todo database
│   └── todo_cli.py        #   CLI for todo CRUD operations
│
├── chats/                 # Conversation history
│   ├── CHATS.md           #   Chat system documentation
│   ├── chats.sqlite       #   Chat database
│   └── chats_cli.py       #   CLI for chat queries
│
├── roadmaps/              # Project roadmaps
│   ├── ROADMAP.md         #   Main roadmap
│   ├── milestones/        #   Milestone documents
│   └── branches/          #   Branch/alternative roadmaps
│
└── logs/
    └── agent-runs/        #   Agent execution logs (append-only)
```

## 4. File Format Conventions

### 4.1 Plans

Naming: `YYYY-MM-DD_plan-name_status.md`

Status values: `new` | `working` | `blocked` | `review` | `done` | `cancel`

Frontmatter:

```yaml
---
id: plan-YYYY-MM-DD-plan-name
status: new|working|blocked|review|done|cancel
owner: agent-name
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
locked_by: agent-name        # only if status=working
locked_at: ISO-8601          # only if status=working
spec_version: 0.1.0
---
```

### 4.2 Memories

`MEMORY.md` is the root index, limited to 1KB. It contains pointers to child memory files. Each child memory file covers one topic.

### 4.3 Sub-Agent Prompts

Each prompt file in `prompts/` defines:

- Role description
- Responsibilities
- Input format expected
- Output format required
- Skills it should use
- When to escalate back to the primary agent

### 4.4 Skills

Each skill directory contains:

- `SKILL.md` — skill definition: name, description, trigger conditions, steps, resources
- `scripts/` — executable scripts the skill uses
- `resources/` — static resources (templates, configs)

### 4.5 SQLite Databases

All SQLite databases use CLI scripts for access. The CLI pattern is:

```bash
python cli_script.py <command> [options]
# Commands: init, add, list, query, update, close, export
```

## 5. Agent Workflow

### 5.1 Startup

1. Agent reads `AGENTS.md` (auto-loaded by most agent systems).
2. Reads `SOUL.md`, `ROUTER.md`, `MANIFEST.yaml`.
3. Optionally reads `memories/MEMORY.md` for project context.

### 5.2 Task Processing (OODRA Cycle)

```
Observe  → Read user input
Orient   → Identify intent
Route    → Match to resources via ROUTER.md
Retrieve → Load only needed content
Decide   → Execute or delegate
Act      → Perform the work
Verify   → Test and validate
Write    → Update state (plans, bugs, todo, memory)
Report   → Tell user the result
```

### 5.3 Sub-Agent Delegation

1. Read target prompt from `prompts/`.
2. Construct structured input.
3. Execute sub-agent in isolated context.
4. Collect structured output.

### 5.4 State Write-Back

After completing work:

- **Plans**: Update frontmatter `status` and `updated_at`. Move to `archive/done/` or `archive/cancel/` when finished.
- **Bugs**: Use `bugs_cli.py` to update status, category, and resolution.
- **Todos**: Use `todo_cli.py` to update steps and status.
- **Memories**: Update `MEMORY.md` root or child files with new knowledge.

## 6. Concurrency and Locking

- Plans use `locked_by` and `locked_at` frontmatter to prevent duplicate work.
- Before starting a plan, check if `status=working` and `locked_by` is set.
- SQLite databases handle concurrent writes natively.
- If a lock is stale (>24h), the next agent may claim the task.

## 7. Version Compatibility

When `VERSION` indicates a different spec version than what an agent expects:

- Minor version differences: proceed, new fields are optional.
- Major version differences: read `AGENTS_SPEC.md` for the current spec before proceeding.

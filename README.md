# AGENTS Work Protocol

> An open protocol that lets all AI agent tools speak the same language.

## The Problem

I use multiple AI agent tools in the same software project. Each tool has its
own strengths, but they easily become information silos: one agent learns the
architecture, another files bugs, another creates plans, and the next one starts
without reliable access to that project state.

A project's knowledge and progress should belong to the project, not to any
single agent tool's private storage.

**AGENTS Work Protocol** defines a shared `.agents/` directory that every agent
tool can read and update consistently.

## What It Is

AGENTS Work Protocol is an open, project-level work specification. Its core
idea:

**Place a `.agents/` directory at the project root, serving as a shared context
operating system for all agent tools.**

No matter which agent tool opens the project, as long as it follows this
protocol, it can:

- Read the same project memory
- Use the same set of reusable skills
- Query the same bug, chat, plan, and todo state
- Understand the same roadmap and work conventions
- Continue work started by another agent

Agent tools may differ. Project knowledge has one source of truth.

## Core Design Principles

### Signposts, Not Content

The protocol uses **three-tier context disclosure**:

| Tier | Content | When Loaded |
|------|---------|-------------|
| Tier 0 | Bootstrap hook (`AGENTS.md`) | Auto-loaded by agent |
| Tier 1 | Role definition + routing (`SOUL.md`, `ROUTER.md`, `MANIFEST.yaml`) | Immediately after bootstrap |
| Tier 2 | Actual content (prompts, skills, memories, workflow, bugs...) | On demand, when a task matches |

Agents should read signposts first, then load specific content only when it is
needed. Do not dump the entire `.agents/` directory into the context window.

### Files for Knowledge, SQLite for State

- **Files** store human-readable knowledge: role definitions, routing,
  reusable skills, project memory, and roadmaps.
- **SQLite databases** store mutable state: workflow plans/todos, bugs, and
  chat logs.

Plans and todos are not separate systems. A plan is a durable project phase or
goal; todos are the executable steps inside that plan. They live together in
the workflow database so agents can query, update, and resume work without
splitting state across markdown files and a second todo database.

### Workflow Is the Project Work Queue

The canonical project workflow state lives at:

```text
.agents/workflow/workflow.sqlite
```

It contains:

- `plans`: large work phases, milestones, or goals
- `todos`: at most two levels of steps inside a plan
- `workflow_events`: append-only audit trail for plan/todo changes
- `workflow_meta`: protocol and migration metadata

By default, tools should list only active records. Completed and cancelled
records stay in the database and are shown only when explicitly requested.

### Tool-Agnostic

This protocol is not tied to any specific agent tool. It is a directory
structure, storage convention, and workflow specification. Any agent tool that
can read files and use SQLite can adopt it.

Claude Code can use it. Codex can use it. Hermes can use it. Future tools can
use it.

## Directory Structure

```text
.agents/
├── AGENTS.md              # Auto-loaded bootstrap hook (Tier 0)
├── SOUL.md                # Primary agent role + work loop
├── ROUTER.md              # Task routing table (human-readable)
├── MANIFEST.yaml          # Resource index (machine-readable)
├── AGENTS_SPEC.md         # Full specification document
├── VERSION                # Spec version string
│
├── prompts/               # Sub-agent role definitions
│   ├── INDEX.md           #   Signpost: read this first
│   └── *.md
│
├── skills/                # Reusable skills and procedures
│   ├── INDEX.md
│   └── <skill>/SKILL.md
│
├── memories/              # Project memory
│   ├── MEMORY.md          #   Root index, pointers only
│   └── *.md
│
├── workflow/              # Unified plan + todo workflow state
│   ├── WORKFLOW.md        #   Human-readable workflow guide
│   ├── workflow.sqlite    #   Canonical workflow database
│   ├── workflow_cli.py    #   Standard CLI for agents/tools
│   └── archive/           #   Legacy imports or exported snapshots
│
├── bugs/                  # Bug tracking system
│   ├── BUGS.md
│   ├── bugs.sqlite
│   └── bugs_cli.py
│
├── chats/                 # Conversation history
│   ├── CHATS.md
│   ├── chats.sqlite
│   └── chats_cli.py
│
└── roadmaps/              # Project roadmaps
    └── ROADMAP.md
```

Legacy `plans/` and `todo/` directories from v0.1.x are import sources only.
After migration, agents should not use them as the active source of truth.

## Workflow Model

### Plans

A plan is a large phase, milestone, or durable goal. A project may have many
plans, but only one should normally be active for a given agent workflow.

Plan status values:

- `new`
- `working`
- `blocked`
- `review`
- `done`
- `cancel`

### Todos

Todos are executable steps inside a plan. Nesting is limited to two levels:

```text
Plan
├── Todo
│   └── Child todo
└── Todo
```

Third-level nesting is invalid. Use dependencies for ordering constraints that
do not fit the two-level shape.

Todo status values:

- `pending`
- `in_progress`
- `blocked`
- `done`
- `cancel`

## Standard Workflow CLI

Implementations should provide:

```bash
python .agents/workflow/workflow_cli.py init
python .agents/workflow/workflow_cli.py plan add --title "Database design"
python .agents/workflow/workflow_cli.py plan list
python .agents/workflow/workflow_cli.py plan show <plan_id>
python .agents/workflow/workflow_cli.py plan activate <plan_id>
python .agents/workflow/workflow_cli.py plan update <plan_id> --status done

python .agents/workflow/workflow_cli.py todo add --plan <plan_id> --title "Create schema"
python .agents/workflow/workflow_cli.py todo add --parent <todo_id> --title "Add indexes"
python .agents/workflow/workflow_cli.py todo list --plan <plan_id>
python .agents/workflow/workflow_cli.py todo update <todo_id> --status in_progress
python .agents/workflow/workflow_cli.py todo done <todo_id>
```

The CLI should query SQLite directly and should not require dumping full tables
into the agent context.

## Migration From v0.1.x

Older projects may contain:

```text
.agents/plans/*.md
.agents/plans/_active.md
.agents/todo/todo.sqlite
.agents/todo/todo_cli.py
```

Migration rules:

1. Import markdown plans into `workflow.sqlite:plans`.
2. Use `_active.md` to mark the matching imported plan as active when possible.
3. Import old todo rows into `workflow.sqlite:todos`.
4. Preserve dependencies when the old todo database has them.
5. Move imported legacy files under `.agents/workflow/archive/imported-<timestamp>/`.
6. Do not keep writing active state to the legacy locations.

## Work Loop

When an agent enters a project, it follows the OODRA cycle:

```text
Observe  -> Read user input
Orient   -> Identify intent
Route    -> Match resources via ROUTER.md
Retrieve -> Load only necessary content
Decide   -> Execute yourself or delegate to sub-agent
Act      -> Perform the work
Verify   -> Validate results
Write    -> Update workflow/bugs/memory as appropriate
Report   -> Report results to user
```

For multi-step work, the agent should create or update a workflow plan and todo
list before or during execution. Completed work should be marked `done`, not
deleted.

## Quick Start

1. Copy the `.agents/` directory into your project root.
2. Edit `memories/MEMORY.md` with your project information.
3. Edit `roadmaps/ROADMAP.md` with your roadmap.
4. Run `python .agents/workflow/workflow_cli.py init`.
5. Run `python .agents/bugs/bugs_cli.py init` if bug tracking is used.
6. Point your agent tool to read `.agents/AGENTS.md` as the entry point.

## Spec Versioning

Current version: **v0.2.0**

The version follows [Semantic Versioning](https://semver.org/):

- **Major**: incompatible structural changes after the protocol reaches 1.0
- **Minor**: protocol shape changes or feature additions during 0.x
- **Patch**: compatible clarifications and bug fixes

Version is synchronized across:

- `.agents/VERSION`
- `.agents/SOUL.md`
- `.agents/ROUTER.md`
- `.agents/AGENTS_SPEC.md`
- `.agents/MANIFEST.yaml`

## License

MIT

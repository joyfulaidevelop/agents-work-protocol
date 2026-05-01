# AGENTS Work Protocol

> An open protocol that lets all AI agent tools speak the same language.

## The Problem

I'm a programmer. In my daily work, I use multiple AI agent tools — Claude Code, OpenAI Codex, OpenClaw, Hermes, and others. Each excels at different things, so I switch between them depending on the task at hand.

But I quickly ran into a problem: **these tools are information silos.**

Claude Code accumulates architectural memory and design decisions in one project. When I switch to Codex, it knows nothing about any of that. A bug filed by one agent remains unresolved while the next agent repeats the same mistakes. I find myself explaining the same project context, conventions, progress, and decisions over and over again in natural language to each new tool.

That's wrong.

A project's knowledge — its architecture, decisions, progress, bugs, plans — should not be locked inside any single agent tool's private storage. It should belong to the project itself.

**That's why I built the AGENTS Work Protocol.**

## What It Is

AGENTS Work Protocol is an open, project-level work specification. Its core idea:

**Place a `.agents/` directory at the project root, serving as a shared context operating system for all agent tools.**

No matter which agent tool opens the project, as long as it follows this protocol, it can:

- Read the same project memory
- Use the same set of skills
- Query the same bug and todo databases
- Understand the same roadmap and plans
- Follow the same work conventions

Agent tools may differ. Project knowledge has one source of truth.

## Core Design Principles

### Signposts, Not Content

The most important design decision in this protocol is **three-tier context disclosure**:

| Tier | Content | When Loaded |
|------|---------|-------------|
| Tier 0 | Bootstrap hook (`AGENTS.md`) | Auto-loaded by agent |
| Tier 1 | Role definition + routing (`SOUL.md`, `ROUTER.md`, `MANIFEST.yaml`) | Immediately after bootstrap |
| Tier 2 | Actual content (prompts, skills, memories, plans, bugs...) | On-demand, when a task matches |

This follows a RAG-like retrieval philosophy: show the agent signposts first ("here's what exists and where to find it"), then load specific content only when confirmed necessary. Never dump everything into the context window upfront.

The context window is a scarce resource. Loading too much pollutes attention. Loading too little leaves the agent lost. The balance between signposts and content is the core tension this protocol addresses.

### Files for Readability, Databases for State

- **Plans**, **memories**, and **roadmaps** are stored as files — human-readable, git-trackable, and loadable on demand
- **Bugs**, **todos**, and **chat logs** are stored in SQLite — supporting structured queries, concurrent writes, and state transitions

Each storage format serves its purpose. They don't replace each other.

### Tool-Agnostic

This protocol is not tied to any specific agent tool. It's simply a directory structure, file format conventions, and workflow specification. Any agent tool that can read files and execute Python scripts can adopt it.

Claude Code can use it. Codex can use it. Future tools can use it.

## Directory Structure

```
.agents/
├── AGENTS.md              # Auto-loaded bootstrap hook (Tier 0)
├── SOUL.md                # Primary agent role + work loop
├── ROUTER.md              # Task routing table (human-readable)
├── MANIFEST.yaml          # Resource index (machine-readable)
├── AGENTS_SPEC.md         # Full specification document
├── VERSION                # Spec version string
│
├── prompts/               # Sub-agent role definitions
│   ├── INDEX.md           #   Signpost (read this first)
│   ├── product-designer.md
│   ├── backend-engineer.md
│   ├── test-engineer.md
│   ├── devops-engineer.md
│   └── reviewer.md
│
├── skills/                # Reusable skills
│   ├── INDEX.md
│   ├── code-review/
│   ├── bug-triage/
│   └── plan-management/
│
├── memories/              # Project memory
│   ├── MEMORY.md          #   Root index (≤1KB, pointers only)
│   ├── architecture.md
│   ├── decisions.md
│   ├── project.md
│   └── user-preferences.md
│
├── plans/                 # Task plans
│   ├── INDEX.md
│   └── archive/{done,cancel}/
│
├── bugs/                  # Bug tracking system
│   ├── bugs.sqlite + bugs_cli.py
│
├── todo/                  # Todo tracking system
│   ├── todo.sqlite + todo_cli.py
│
├── chats/                 # Conversation history
│   ├── chats.sqlite + chats_cli.py
│
└── roadmaps/              # Project roadmaps
    └── ROADMAP.md
```

## Work Loop

When an agent enters a project, it follows the OODRA cycle:

```
Observe  → Read user input
Orient   → Identify intent
Route    → Match resources via ROUTER.md
Retrieve → Load only necessary content
Decide   → Execute yourself or delegate to sub-agent
Act      → Perform the work
Verify   → Validate results
Write    → Update state (plans/todo/bugs/memory)
Report   → Report results to user
```

## Quick Start

1. Copy the `.agents/` directory into your project root
2. Edit `memories/MEMORY.md` with your project info
3. Edit `roadmaps/ROADMAP.md` with your roadmap
4. Run `python .agents/bugs/bugs_cli.py init` to initialize databases (skip if already initialized)
5. Point your agent tool to read `.agents/AGENTS.md` as the entry point

## Spec Versioning

Current version: **v0.1.0**

The version follows [Semantic Versioning](https://semver.org/):
- **Major**: Incompatible structural changes
- **Minor**: Backward-compatible feature additions
- **Patch**: Backward-compatible bug fixes

Version is synchronized across:
- `.agents/VERSION`
- `.agents/SOUL.md`
- `.agents/ROUTER.md`
- `.agents/AGENTS_SPEC.md`
- `.agents/MANIFEST.yaml`

## License

MIT

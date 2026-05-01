# Todo System

> Todo tracking workflow documentation.

## Overview

Todos are tracked in `todo.sqlite` and managed through `todo_cli.py`.

## Todo Structure

Each todo item has:
- **title**: Short description of the task
- **description**: Detailed requirements
- **status**: Current state (see below)
- **priority**: `critical`, `high`, `medium`, `low`
- **assignee**: Which agent or person is responsible
- **depends_on**: List of todo IDs that must complete first
- **created_at / updated_at**: Timestamps

## Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `in_progress` | Currently being worked on |
| `blocked` | Waiting on a dependency |
| `done` | Completed |
| `cancel` | No longer needed |

## CLI Usage

```bash
# Initialize database (run once)
python todo_cli.py init

# Add a todo
python todo_cli.py add --title "Task name" --priority high --description "Details"

# List pending todos
python todo_cli.py list --status pending

# Query todos by priority
python todo_cli.py query --priority high

# Update todo status
python todo_cli.py update <todo_id> --status in_progress --assignee backend-engineer

# Complete a todo
python todo_cli.py update <todo_id> --status done

# Add dependency
python todo_cli.py add-dep <todo_id> <other_todo_id>
```

## Conventions

- Break large tasks into ordered todo items.
- Use `depends_on` to establish execution order.
- When starting a todo, set `status=in_progress` and `assignee`.
- Update `updated_at` on every status change.

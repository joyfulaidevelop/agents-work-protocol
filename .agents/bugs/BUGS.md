# Bugs System

> Bug tracking workflow documentation.

## Overview

Bugs are tracked in `bugs.sqlite` and managed through `bugs_cli.py`.

## Bug Categories

| Category | Description | Handler |
|----------|-------------|---------|
| `code` | Code-level functional bugs (logic error, crash, wrong output) | Backend Engineer / Test Engineer |
| `design` | Design-level issues (wrong UX flow, missing feature behavior) | Product Designer |
| `performance` | Performance degradation, memory leak, slow response | Backend Engineer |
| `security` | Security vulnerabilities, injection, auth bypass | Reviewer |
| `compatibility` | Cross-browser, cross-platform, API compatibility | Test Engineer |

## Bug Lifecycle

```
open → confirmed → assigned → fixing → review → closed
                                                  ↘ wontfix
```

## CLI Usage

```bash
# Initialize database (run once)
python bugs_cli.py init

# Add a bug
python bugs_cli.py add --title "Bug title" --category code --severity high --description "Details"

# List open bugs
python bugs_cli.py list --status open

# Query bugs by category
python bugs_cli.py query --category code --status open

# Update bug status
python bugs_cli.py update <bug_id> --status confirmed --assigned-to backend-engineer

# Close a bug
python bugs_cli.py update <bug_id> --status closed --resolution "Fixed in commit abc123"

# Export bugs report
python bugs_cli.py export --format markdown --output bugs_report.md
```

## Conventions

- Every bug must have a category and severity.
- `severity` values: `critical`, `high`, `medium`, `low`.
- When a bug is closed, add a `resolution` field explaining the fix.
- Closed bug attachments (logs, screenshots) go in `archive/`.

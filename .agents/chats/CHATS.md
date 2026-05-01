# Chats System

> Conversation history tracking documentation.

## Overview

Chat logs are stored in `chats.sqlite` and queried through `chats_cli.py`.

## Purpose

- Record significant agent-user conversations for future context.
- Enable agents to recall past decisions and discussions.
- Provide searchable history without loading everything into context.

## CLI Usage

```bash
# Initialize database (run once)
python chats_cli.py init

# Save a conversation summary
python chats_cli.py add --summary "Discussed auth refactor approach" --participants "user,SOUL" --tags "auth,architecture"

# Search conversations
python chats_cli.py search --query "authentication" --limit 10

# List recent conversations
python chats_cli.py list --limit 20

# Get conversation details
python chats_cli.py get <chat_id>

# Export conversation log
python chats_cli.py export --format markdown --output chat_export.md
```

## Conventions

- Do NOT save full conversation transcripts. Save structured summaries.
- Tag conversations for searchability.
- Use `participants` to track who was involved (user, SOUL, sub-agent names).
- NEVER dump the full chats database. Always query with filters.

# AGENTS.md

> Auto-loaded hook for any agent entering this project.

## Spec Version

Read `.agents/VERSION` for the current spec version.

## Bootstrap Sequence

1. Read `.agents/SOUL.md` — your role and work discipline.
2. Read `.agents/ROUTER.md` — where to find what you need.
3. Read `.agents/MANIFEST.yaml` — machine-readable resource index.

## Rules

- Do NOT scan the entire `.agents/` directory on startup.
- Do NOT load all files at once. Follow the 3-tier context disclosure model.
- Only read content files when a task requires them.
- Query SQLite databases through their CLI scripts, never dump full tables.
- Before creating new files, check `.agents/AGENTS_SPEC.md` for naming and format conventions.

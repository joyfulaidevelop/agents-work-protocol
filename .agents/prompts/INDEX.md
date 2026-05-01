# Prompts Index

> Route index for sub-agent prompts. Load full prompt only when delegating.

| Agent | File | Role | Delegate When |
|-------|------|------|---------------|
| Product Designer | `product-designer.md` | Feature design, UX decisions, design spec review | User requests feature design, design dispute, UX decision |
| Backend Engineer | `backend-engineer.md` | Code implementation, API design, architecture | Code implementation, API work, performance optimization |
| Test Engineer | `test-engineer.md` | Testing strategy, test writing, bug verification | Test planning, bug verification, quality assurance |
| DevOps Engineer | `devops-engineer.md` | Deployment, CI/CD, infrastructure, monitoring | Deployment, infrastructure, CI/CD pipeline work |
| Reviewer | `reviewer.md` | Code review, design review, security audit | Code review, PR review, security audit |

## Delegation Protocol

1. Read the target agent's prompt file.
2. Provide: task description, relevant context snippets, expected output format.
3. Sub-agent runs in isolated context.
4. Collect structured output.

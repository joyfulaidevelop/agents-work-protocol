# Plan Management Skill

## Name

plan-management

## Description

Plan creation, status tracking, locking, and archival for multi-step task execution.

## Trigger Conditions

- Creating a new plan for a multi-step task
- Checking plan status
- Updating plan progress
- Archiving completed or cancelled plans

## Steps

1. **Check Existing Plans**
   - Read `plans/INDEX.md`
   - Verify no duplicate plan exists for the same task

2. **Create Plan**
   - Use naming: `YYYY-MM-DD_plan-name_new.md`
   - Include frontmatter:
     ```yaml
     ---
     id: plan-YYYY-MM-DD-plan-name
     status: new
     owner: agent-name
     created_at: YYYY-MM-DD
     updated_at: YYYY-MM-DD
     spec_version: 0.1.0
     ---
     ```
   - Body: problem statement, steps, success criteria, dependencies

3. **Claim Plan**
   - Update frontmatter: `status: working`, `locked_by: <agent>`, `locked_at: <timestamp>`
   - Before claiming, check if another agent has locked it
   - If lock is stale (>24h), may claim with a note

4. **Update Plan**
   - Update `updated_at` on every change
   - Add progress notes as the plan executes
   - Change status as needed: `blocked`, `review`

5. **Archive Plan**
   - On completion: move to `archive/done/`, set `status: done`
   - On cancellation: move to `archive/cancel/`, set `status: cancel`
   - Update `plans/INDEX.md` to remove archived plan

## Resources

- `plans/INDEX.md` — active plans index
- `plans/archive/` — archived plans

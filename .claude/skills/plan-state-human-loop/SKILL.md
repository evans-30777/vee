# Skill: Plan, State & Human-in-the-Loop Control

## Purpose
Every meaningful task must have an explicit, inspectable plan and project state so the human can see what is happening, what is finished, what remains, and where human knowledge or approval is required.

## Mandatory plan structure
Before implementation of a medium/large task, maintain a current plan with:

### Goal
What outcome are we trying to achieve?

### In scope
What will be changed in this task?

### Out of scope
What will deliberately not be changed?

### Steps
A short ordered list of concrete actions.

### Status
Use only:
- `NOT STARTED`
- `IN PROGRESS`
- `DONE`
- `BLOCKED`
- `NEEDS HUMAN INPUT`

### Verification
How success will be checked.

For very small tasks, the visible plan may be one line, but the agent must still know the goal and completion condition.

## Mandatory state tracking
For multi-step work, keep a project/task state record in the repository when the project supports persistent documentation. Prefer:

`docs/PROJECT_STATUS.md`

If a project already has an established status/progress file, use that instead of creating a duplicate.

The state record should contain:
- Current goal
- Current phase
- Completed work
- Remaining work
- Open decisions
- Blockers
- Needs human input
- Risks/issues
- Last verification performed
- Next action

Keep it concise. Update it after meaningful milestones, not after every trivial edit.

## Human-in-the-loop rule
The human is the final authority for business decisions, unclear requirements, credentials, content claims, legal/compliance interpretations, and irreversible choices.

Whenever human knowledge is required, write it down explicitly as:

**NEEDS HUMAN INPUT:** <exact information needed and why>

Do not hide clarification requests inside implementation notes.

When clarification is received:
1. record the decision
2. update the relevant status item
3. continue from the affected step

## Progress visibility
Every substantial response to the human should contain:

**Goal:** one sentence

**Done:** concrete completed items

**Not done:** remaining items

**Issues / clarification:** only real issues or missing information

**Next:** the immediate next action

Keep this compact. Never manufacture progress just to populate the section.

## Re-planning rule
Plans are living documents. If implementation reveals new information:
- update the plan
- explain the changed decision briefly
- preserve completed work
- do not pretend the original plan still applies

## No false completion
Never mark an item `DONE` because code was written. It is `DONE` only when the required verification has passed.

Never mark a feature complete when a required dependency, migration, integration, content item, test, or deployment step is still outstanding.

## Task boundaries
For large work:
1. define phase
2. implement phase
3. verify phase
4. update state
5. report to human
6. proceed only when the next phase is safe

Avoid giant "build everything" changes with no checkpoint.

## Token economy
State tracking must improve execution, not create bureaucracy:
- use short entries
- update only on meaningful state changes
- do not repeat entire plans in every message
- do not create a new planning document when an existing one can serve
- read only the relevant state section when resuming work

# VEE Agency Claude Project Skills

## Purpose
These skills control how Claude should work on the VEE Agency website project. The priorities are:

1. Accuracy
2. Completing the requested task
3. Preserving working code
4. Minimal unnecessary token use
5. Clear, verifiable reporting

## Mandatory source order
Use project documents as follows:

1. `00_MASTER_WEBSITE_SPEC.md` — business/product source of truth
2. `01_TECHNICAL_DJANGO_IMPLEMENTATION_GUIDE.md` — architecture/implementation rules
3. `02_DESIGN_SYSTEM_MOTION_ACCESSIBILITY.md` — visual, motion and accessibility rules
4. `03_SEO_AEO_CONTENT_GUIDELINES.md` — search/content rules
5. `04_CODING_AGENT_MASTER_PROMPT.md` — engineering guardrails
6. `05_PROJECT_README_AND_AGENT_WORKFLOW.md` — workflow and definition of done

## Critical rule
If information is not present in the project sources or supplied by the user, do not invent it. Mark it as **unknown / needs confirmation**.

## Token economy
Do not reread or reproduce entire documents when only a section is needed. Search for the relevant heading/term, read the smallest useful context, then act.

Do not generate long plans for small tasks. For small tasks: inspect → change → verify → report.

Do not explain obvious code. Report only decisions, changes, verification and blockers.

## Working mode
- Prefer the smallest safe change.
- Reuse existing architecture before creating new abstractions.
- Never claim something was tested unless it was actually tested.
- Never claim a browser/UI result unless it was actually inspected.
- Do not ask for information that is already confirmed in project sources.
- Ask only when missing information blocks a correct implementation.

## Conflict rule
When sources conflict, do not silently reconcile them. Identify the conflict, prefer the latest confirmed user decision, and state the affected assumption before changing it.

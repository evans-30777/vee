# Skill: Task Router

Use this decision tree before acting.

## A. User asks for an explanation
Read only the relevant project source section. Answer directly. No code changes.

## B. User asks for a small code/content change
Inspect the affected files only → implement → verify → report.

## C. User asks for a feature
Inspect existing architecture and related components first. Identify dependencies and integration points. Implement end-to-end, not as an isolated snippet.

## D. User asks for a bug fix
Reproduce or inspect the failure first. Fix the root cause rather than masking the symptom. Run a focused regression check.

## E. User asks for a redesign
Read the design system and inspect the current component/page first. Preserve business behavior unless explicitly asked to change it.

## F. User asks for SEO/content
Use the SEO/content skill and master specification. Do not invent business claims.

## G. User asks for a large change
Break into coherent stages and complete one stage at a time. After each stage, verify before continuing.

## Stop conditions
Stop and ask only when:
- two authoritative sources conflict and cannot be resolved from the latest user decision
- a required secret/credential is missing
- a destructive change requires approval
- a business fact is required but unknown
- implementation would otherwise require guessing

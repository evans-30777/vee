# Skill: No Guessing & Evidence Discipline

## Rule
Never fill an information gap with a plausible answer.

## Evidence hierarchy
1. Explicit user instruction in the current task
2. Latest confirmed project source of truth
3. Other project documentation
4. Existing repository behavior/data
5. External research only when the task explicitly requires it
6. General knowledge only for non-project facts that do not affect business requirements

## When uncertain
Use one of:
- **Confirmed:** directly supported by a source.
- **Observed:** found in the existing repository.
- **Inference:** logically suggested but not confirmed.
- **Unknown:** insufficient evidence.
- **Blocked:** cannot proceed safely without confirmation.

Never convert Inference/Unknown into Confirmed.

## Forbidden assumptions
Do not guess:
- business claims
- prices
- contact details
- social URLs
- testimonials
- client names/logos
- metrics/results
- awards
- staff/team members
- hosting configuration
- API credentials
- secrets
- production environment values
- SEO claims
- legal/compliance claims
- framework versions
- installed packages
- existing database structure

## Placeholder policy
Placeholders are allowed only during implementation when technically necessary and must be clearly marked and tracked; none may remain unintentionally in production.

Never invent content merely to make a UI look populated.

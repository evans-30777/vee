# Skill: Grill Me — Human Discovery & Uncertainty Removal

## Purpose
Use a disciplined, relentless interview to remove ambiguity before implementation. The goal is shared understanding, not conversational volume.

This skill is based on the core design of Matt Pocock's `grill-me`: interrogate the plan/design branch by branch, resolve dependencies in order, ask one question at a time, provide a recommended answer, and inspect the codebase/files when they can answer the question instead of asking the human. citeturn354692search0turn354692search1

## Activation
Run when:
- the user says `grill me`, `stress-test this`, `pressure-test this`, `remove doubt`, or similar
- a requested feature/design contains material unresolved decisions
- the task is high-risk or ambiguous enough that implementation would otherwise require assumptions
- the user explicitly asks to be questioned before work begins

Do NOT automatically start a long grilling for routine, already-specified tasks.

## Core rules
1. Interview relentlessly until every material branch needed for correct implementation is resolved or explicitly marked blocked.
2. Ask **one question at a time**. Never dump a questionnaire unless the user explicitly asks for a batch.
3. Each question must include a concise recommended answer when a reasonable recommendation exists. The user may accept, reject, or modify it.
4. Prefer evidence over questions: inspect the repository, project docs, existing data, configuration, templates, tests, and current behavior before asking the human something the project can answer.
5. Never ask a question whose answer is already confirmed in project sources or prior decisions.
6. Start with parent decisions before dependent decisions. Re-evaluate downstream questions when an answer changes the branch.
7. Ask only questions that materially reduce ambiguity, rework, risk, or incorrect assumptions. Do not ask for trivia.
8. Continue until the implementation path is sufficiently deterministic. “I think this is probably fine” is not a valid completion criterion when evidence is missing.

## Question quality
Questions should resolve things such as:
- exact behavior
- user journey
- business rules
- scope boundaries
- required versus optional functionality
- permissions/roles
- content ownership
- data source and source of truth
- integration behavior
- failure behavior
- edge cases
- SEO/indexing intent
- design priorities
- mobile/responsive behavior
- accessibility requirements
- launch criteria
- operational ownership

When useful, present 2–4 likely options plus a free-form option. Do not force a multiple-choice answer when the decision genuinely requires the user's own wording.

## Decision tree method
For the current task, maintain:
- **Resolved decisions**
- **Open decisions**
- **Blocked decisions**
- **Assumptions explicitly accepted by the user**

Do not silently collapse these categories.

## Recommended answer rule
A recommended answer is a proposal, not a fact. Label it as **Recommendation** and keep the underlying fact/decision separate.

Example:
> **Question:** Should enquiries create a database record before email notification?
> **Recommendation:** Yes — save first, then notify, so an SMTP failure does not erase the lead.

## Stop condition
Finish grilling when:
- all material branches required for the current implementation are resolved; and
- no critical business, technical, content, security, SEO, or UX ambiguity remains; and
- remaining unknowns are explicitly recorded with an owner/action.

Then produce a compact **Grill Summary** containing:
- decisions made
- decisions still open
- blocked items
- accepted assumptions
- resulting implementation direction

Do not start implementation before the user confirms the shared understanding when the grill was explicitly requested as a pre-build gate.

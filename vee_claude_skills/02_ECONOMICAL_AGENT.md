# Skill: Economical Agent

## Objective
Finish the job with the fewest useful reasoning/tool steps, without reducing correctness.

## Retrieval discipline
Before reading files, determine the smallest information needed.

Use targeted search/read for:
- exact models
- relevant settings
- affected template
- affected view/form/url
- required design token
- relevant SEO rule

Do not load the entire repository unless the task genuinely requires global understanding.

## Planning discipline
For a small change, use a one-line plan internally and execute.

For a medium/large change, provide at most:
- Goal
- Files/areas affected
- Verification method

Do not write speculative architecture documents before inspecting the actual code.

## Coding discipline
- Reuse existing components.
- Prefer configuration/data changes over duplicated code.
- Avoid new dependencies unless necessary.
- Avoid unnecessary refactors.
- Avoid premature abstraction.
- Avoid rewriting functioning code.

## Verification discipline
Verify only what the change could affect, plus basic regression checks.

Examples:
- model change → migrations + Django checks + affected admin/views
- template change → route render + responsive/console check if available
- CSS change → affected pages + mobile/desktop
- SEO change → rendered metadata/URLs/sitemap/robots as applicable
- form change → validation + success/failure path

## Response discipline
End with a compact report:
- Done
- Verified
- Remaining / Blocked

Do not dump code unless requested.

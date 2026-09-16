# Skill: Verification & Reporting

## Definition of done
A task is complete only when the requested behavior exists in the real project and has been verified to the extent practical.

## Verification checklist
Use only applicable checks:
- Django system checks
- test suite / targeted tests
- URL resolution
- template rendering
- form submission/validation
- migration checks
- admin behavior
- browser console
- responsive layout
- SEO output
- broken links
- asset loading

## Evidence-based reporting
Report only what was actually done.

Good:
> Implemented the contact form model and admin list; ran Django checks and targeted form tests.

Bad:
> Everything is fully tested and production-ready.

unless that was actually established.

## Failure handling
When something fails:
1. identify the exact failure
2. inspect the relevant code/output
3. make the smallest fix
4. rerun the relevant check

If blocked by missing information, stop before making a risky assumption and state exactly what is needed.

## Final response format
Use:

**Done** — what changed.

**Verified** — checks actually performed.

**Remaining** — unresolved issue(s), or `None`.

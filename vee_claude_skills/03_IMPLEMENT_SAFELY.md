# Skill: Safe Django Implementation

## Before changing code
Inspect the current implementation first. Specifically check:
- settings and environment loading
- installed packages
- URL configuration
- relevant app/models
- migrations
- templates/static assets
- admin configuration
- deployment configuration
- tests

Do not assume the repository matches the specification exactly.

## Change protocol
1. Identify the smallest correct implementation.
2. Reuse existing project conventions.
3. Make the change.
4. Run the narrowest meaningful tests/checks.
5. Inspect affected output.
6. Fix failures before moving on.

## Database
Never edit production data casually.

When models change:
- create migrations
- inspect migration operations
- run migration checks/tests
- preserve existing data compatibility

Do not make destructive schema changes without explicit approval.

## Configuration
Secrets belong in environment variables, never source code.

Do not replace real environment configuration with guessed values.

## CMS
Content the owner should manage later belongs in Django Admin where appropriate, including services, packages, posts, locations, testimonials and case studies.

Do not duplicate business values across multiple templates when a controlled model/source can provide them.

## Existing functionality
Do not replace working systems just because an alternative is aesthetically cleaner.
Change only what is necessary for the requested outcome.

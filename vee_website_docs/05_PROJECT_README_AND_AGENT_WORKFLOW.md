# VEE Agency Website — Project README & AI-Agent Workflow

## Purpose

This document controls how AI coding agents should work on the VEE Agency website without introducing regressions, contradictory business information, or incomplete implementations.

---

## Documents and Authority

Read these files in order:

1. `00_MASTER_WEBSITE_SPEC.md`
2. `01_TECHNICAL_DJANGO_IMPLEMENTATION_GUIDE.md`
3. `02_DESIGN_SYSTEM_MOTION_ACCESSIBILITY.md`
4. `03_SEO_AEO_CONTENT_GUIDELINES.md`
5. `04_CODING_AGENT_MASTER_PROMPT.md`

If the repository contains additional documentation, reconcile it against these files before making architecture changes.

---

## Agent Working Method

### Phase 1 — Inspect

Before editing:

- inspect the current codebase
- identify framework/version
- identify database
- inspect current models and migrations
- inspect templates
- inspect static files
- inspect settings
- inspect deployment files
- inspect tests

### Phase 2 — Plan

For a non-trivial task, state:

- what will change
- which files will change
- why
- what dependencies are required
- how it will be tested

Do not produce a huge speculative rewrite.

### Phase 3 — Implement

Make the smallest coherent set of changes that solves the requirement.

Preserve working functionality.

### Phase 4 — Verify

After implementation:

- run automated tests
- run migrations checks
- run Django checks
- inspect URLs
- inspect templates
- inspect browser console
- inspect responsive behavior

### Phase 5 — Review

Ask:

- Did I introduce placeholder content?
- Did I contradict a confirmed VEE fact?
- Did I break mobile?
- Did I add unnecessary JavaScript?
- Did I create an SEO problem?
- Did I make admin harder to use?
- Did I introduce secrets or insecure defaults?

### Phase 6 — Report

Provide a concise implementation summary:

- completed
- files changed
- tests run
- issues found
- remaining work

---

## Never Do This

- Do not replace the entire project because one component is inconvenient.
- Do not rewrite models without considering migrations and existing data.
- Do not change package pricing without explicit approval.
- Do not add social accounts that have not been confirmed.
- Do not fabricate content to make a section look populated.
- Do not claim a feature was tested when it was only written.
- Do not use production secrets in source control.
- Do not leave debugging tools enabled in production.
- Do not make the home page depend on JavaScript just to display text.

---

## Definition of Done

A task is done only when:

1. code is implemented
2. code is integrated into the real application
3. the feature works in its real route/template context
4. tests or direct verification were performed
5. responsive behavior was checked where visual
6. documentation is updated when behavior/architecture changed
7. no known regression was introduced

---

## Prompt for a Coding Agent

Copy the following when handing the project to an AI coding agent:

```text
You are the lead engineer for veeagency.co.ke.

Read every file in /docs before changing architecture. Treat 00_MASTER_WEBSITE_SPEC.md as the business source of truth. Treat the technical, design, SEO/AEO and workflow documents as implementation rules.

Do not guess about VEE Agency business information. Confirmed values include:
- Syokimau, Machakos County, Kenya
- primary local emphasis: Nairobi, Machakos, Kajiado, Kiambu
- nationwide service coverage across Kenya
- WhatsApp/phone: 0759 643 882
- email: hello@veeagency.co.ke
- social: Facebook and Instagram
- HostAfrica hosting
- blog live at launch
- testimonials/case studies added later through Django Admin
- Essential KES 15,000/month
- Standard KES 25,000/month
- Premium KES 45,000/month
- reference/original prices: KES 18,000 / 30,000 / 55,000 where displayed as crossed-out values

Before coding:
1. inspect the current repository
2. inspect settings, models, migrations, templates, static assets and deployment files
3. determine what already works
4. produce a concise implementation plan for the requested change

During coding:
- preserve working behavior
- prefer standard Django patterns
- keep the architecture maintainable
- make CMS-managed content editable from Admin
- build mobile-first
- keep JavaScript progressive enhancement
- respect accessibility and reduced motion
- optimize for performance
- implement SEO/AEO correctly
- never invent proof, testimonials, clients, results or statistics
- never hard-code secrets

When implementing a feature, verify it end-to-end in the real application rather than only creating files.

Before declaring success:
- run tests
- run Django checks
- verify affected routes
- verify forms
- verify responsive behavior
- check browser console for errors
- verify SEO metadata where relevant
- verify no placeholders remain
- update documentation when architecture or configuration changes

When reporting back, state exactly what was changed, how it was tested, and any remaining risks or tasks. Never claim a test was performed if it was not.
```

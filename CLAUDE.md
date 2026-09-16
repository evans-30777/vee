# Claude Configuration for VEE Agency

## Git & Commit Policy

**Authorization:** You have permission to commit directly to `main` branch.
- Create commits for all changes
- Push directly to `main` without creating feature branches or pull requests
- Use clear, descriptive commit messages
- Include standard attribution lines in commits

## Project Structure

Read the following in order for all implementation decisions:

1. `vee_website_docs/00_MASTER_WEBSITE_SPEC.md` — business source of truth
2. `vee_website_docs/01_TECHNICAL_DJANGO_IMPLEMENTATION_GUIDE.md` — Django architecture
3. `vee_website_docs/02_DESIGN_SYSTEM_MOTION_ACCESSIBILITY.md` — design/UX/accessibility
4. `vee_website_docs/03_SEO_AEO_CONTENT_GUIDELINES.md` — SEO and content rules
5. `vee_website_docs/04_CODING_AGENT_MASTER_PROMPT.md` — engineering guardrails
6. `vee_website_docs/05_PROJECT_README_AND_AGENT_WORKFLOW.md` — workflow and verification

## Claude Skills

Apply these skills from `vee_claude_skills/` directory:

1. **Skills Index** (00_SKILLS_INDEX.md) — mandatory source order, token economy, working mode
2. **No Guessing & Evidence** (01_NO_GUESSING_EVIDENCE.md) — evidence hierarchy, forbidden assumptions
3. **Economical Agent** (02_ECONOMICAL_AGENT.md) — minimal tokens, no speculative work
4. **Safe Django Implementation** (03_IMPLEMENT_SAFELY.md) — Django protocols
5. **Design, Content, SEO & UX** (04_DESIGN_CONTENT_SEO.md) — visual and content rules
6. **Task Router** (06_TASK_ROUTER.md) — decision tree for task types
7. **Grill Me** (07_GRILL_ME_HUMAN_DISCOVERY.md) — use when ambiguity requires removal
8. **Plan & State, Human-in-Loop** (08_PLAN_STATE_HUMAN_IN_LOOP.md) — track state and decisions

## Confirmed VEE Business Facts

**Do not guess these — they are locked:**

- Base location: Syokimau, Machakos County, Kenya
- Primary service areas: Nairobi, Machakos, Kajiado, Kiambu (strong local emphasis)
- Coverage: All counties in Kenya (nationwide)
- **Phone numbers (both public, different channels):**
  - Calls: 0717 115 737
  - WhatsApp: 0759 643 882 (+254 759 643 882 international) — `https://wa.me/254759643882`
- Email: hello@veeagency.co.ke
- Social: Facebook, Instagram (confirmed; X, TikTok, LinkedIn only in content/posts, not primary brand channels)
- Hosting: HostAfrica
- Operator: Solo — Evans (VEE Agency founder/author). No other team members unless confirmed later.
- **Package Pricing (current):**
  - Essential: KES 15,000/month
  - Standard: KES 25,000/month
  - Premium: KES 45,000/month
  - Website Creation: **from** KES 30,000 (one-time base price; complex builds — e-commerce, booking/hospitality — quoted case-by-case above base, not itemized on the site)
- Website Creation approach: One service, not separate SKUs per site type. Site "type" (portfolio, business, e-commerce, booking/hospitality, etc.) determines scope/complexity within the same KES 30,000+ offering — always built with SEO/AEO/GEO-ready structure and clear enquiry/booking paths.
- Blog: Fully live at launch; author writes weekly posts
- Testimonials/Case Studies: CMS-ready in Django Admin; added over time, never fabricated
- Analytics: GA4, Google Search Console, Meta Pixel (client-side for now)
- Legal: Privacy Policy, Terms of Service, Cookie Policy, Disclaimer required
- Brand assets: real logo at `initial assets/logo.png` (dark red + orange V mark, confirms master spec colors). `nvidia inspiration/` = motion/layout reference only (hero, menu, footer feel) — not a literal template. Other files in `initial assets/` are marked "context only, do not use directly" per `initial assets/instructions.txt` — do not embed those flyer images/colors (blue scheme) into the live site.
- Social links (Facebook, Instagram): build the field/icon slot now; leave empty until the owner provides real URLs. Per Empty-State Rule, do not render an icon with no URL.
- Design mandate: this is a conversion-focused sales site, not a portfolio piece for VEE itself. Every section must build enough trust that a cold visitor is ready to enquire before they ever call.
- Theme: dark-mode only at launch (per `02_DESIGN_SYSTEM_MOTION_ACCESSIBILITY.md`). A real light-mode + toggle is Phase 2 — do not build a half-finished toggle at launch.
- Website Development page must include a static mockup showcase: 3 example layouts (Portfolio, E-commerce, Booking/Hospitality) — visual only, no backend/models, clearly labeled as example layouts (never presented as real client work, per the never-fabricate-proof rule).
- Build order for this project: backend fully implemented and verified first (models, admin, forms, URLs) before frontend/template/styling work begins.

## Never Do This

- Do not fabricate testimonials, client logos, case-study results, or statistics
- Do not invent team members or staff beyond the author/owner
- Do not hard-code secrets or API keys
- Do not change confirmed pricing without explicit approval
- Do not leave placeholder content in production
- Do not claim a feature was tested when it was only written
- Do not add social platforms beyond confirmed ones
- Do not use production secrets in source control

## Definition of Done

A task is complete when:

1. Code is implemented and committed
2. Code integrates into the real application
3. Feature works in its real route/template context
4. Tests/verification were performed
5. Responsive behavior checked (where visual)
6. Documentation updated if architecture changed
7. No known regressions introduced

## Token Economy

- Do not reread entire documents when only a section is needed
- Search for the relevant heading, read minimal context, then act
- For small tasks: inspect → change → verify → report
- Do not explain obvious code
- Do not speculate about architecture before inspecting the actual codebase


# VEE Agency — Full Site Audit

**Date:** 17 September 2026
**Scope:** Entire site — structure, customer journeys, UI/UX, SEO/AEO/GEO, forms, motion, typography, accessibility, content depth, legal, security.
**Commit audited:** `21bd6b2`
**Verdict:** The site is well built and honest. It is not yet a converting machine, and it cannot currently prove whether it converts at all.


---

## Remediation status — 17 September 2026

All four phases are implemented, verified and pushed. What follows is the
original audit, kept as the record of what was found and why.

**Fixed (52 of 56 findings):** every P0, P1, P2 and P3 item except the four
that need information only the owner has.

**Still open — owner input required:**

| # | Item | What is needed |
|---|---|---|
| 11 | Social URLs, bio, headshot | Real Facebook and Instagram URLs, a short bio and a photo. The fields and the schema `sameAs` wiring are built and stay hidden until they are filled. |
| 10 | Legal review | The Privacy Policy now covers the controller's identity, ODPC complaints, retention, named recipients and cross-border transfer. A lawyer should still read all four documents. |
| — | Pricing FAQ gaps | Contract length, cancellation terms and setup fees are the three questions buyers ask that the site still cannot answer. Nothing was invented; decide the policy and they can be added. |
| E-10 | Local signals | Geo coordinates, opening hours and a Google Business Profile link. Take these from the real GBP rather than guessing a pin. |

**Decisions the owner made during remediation (17 September 2026):**

- Package tiers are **cumulative** — each includes the one below it. The
  comparison table is built on this, and a test enforces it.
- Struck-through "was" prices are **removed**, from the cards and from the
  seeder. Actual prices unchanged.
- The contact page commits to a reply **within one working day**.

**Two findings were corrected during the work:**

- **P-02 said "6 font files".** Wrong — Inter and Space Grotesk are both
  *variable* fonts, and Google was serving one file per family covering every
  weight. The real figure was two files. The finding still stood on the
  third-party-origin and privacy grounds, and self-hosting them is done.
- **A-10 partly overstated the problem.** Django 5.2 already emitted
  `aria-invalid` and `aria-describedby` correctly for errors; only the *hint*
  text was unassociated. Fixed as stated, but error association was never
  broken.

**Three problems were found while fixing others, none of which were in the
original audit:**

1. **The newsletter never showed a confirmation.** Its status element is a
   sibling of the form, not a child, so `form.querySelector` returned null and
   an early `return` swallowed everything after it. Nobody subscribing had ever
   seen a success or failure message.
2. **`seed_content` destroyed its own definitions as it read them**, popping
   `slug` out of module-level constants. A second run in the same process
   seeded rows with no slug. Running it once per deploy is the only reason it
   never bit.
3. **The desktop nav had no `white-space: nowrap`**, so "Web Development"
   wrapped onto two or three lines at every width below 1280 — the header sat
   at triple height on a common laptop width.

**Verification performed after the work:**

- 120 tests pass, three consecutive runs; `check --deploy` clean under
  production settings.
- Heading hierarchy re-extracted from all 19 pages: no skipped levels, exactly
  one `h1` each.
- Responsive sweep of 156 combinations (12 pages x 13 widths, 320–1920px): no
  horizontal overflow, no wrapped nav link.
- Contrast re-measured: every control boundary and focus state ≥3:1, every
  text pair ≥4.5:1.
- CSP verified across nine pages: no violations, no console errors, carousels,
  reveals and fonts all working.
- Consent re-verified end to end: no tracker request before a decision, none
  after declining even on a conversion page, both tags on accept, and a
  conversion queued through the banner still recorded.
- JavaScript disabled: every reveal visible, no preloader trap, all five hero
  slides stacked, forms and the comparison table usable.

---

## How this audit was done

Everything below was verified against the running site, not inferred from reading code:

- All 10 top-level pages were rendered from a live server and the HTML inspected.
- Contrast ratios were **computed numerically** (WCAG relative luminance), not eyeballed.
- Heading hierarchy was extracted programmatically from the rendered DOM of every page.
- Content depth was measured by word count from the database.
- The contact form was submitted with invalid data and the real error markup inspected.
- The internal link graph was built from the rendered pages.
- JSON-LD was parsed on every page to confirm validity.
- CSS custom properties were cross-checked: every `var()` against every declaration.
- The test suite was run (63 tests, all passing).

Where a finding is a measurement, the measurement is given. Where something is a judgement call, it is labelled as one.

---

## Scoreboard

| Area | State | Biggest single problem |
|---|---|---|
| Structural integrity | **Good** | Two broken CSS variables, section numbering out of order |
| Conversion architecture | **Adequate** | Nothing is measured — no analytics, no conversion events |
| Customer journeys | **Mixed** | Three journeys end with no next step |
| UI / UX consistency | **Good with gaps** | Letter-initial icons survived the icon replacement in 4 places |
| Accessibility | **Mixed** | Focus indicator fails AA on both light and dark backgrounds |
| SEO | **Weak** | Service pages carry 55–88 words each |
| AEO | **Weak** | FAQ schema exists only on home and blog posts |
| GEO / local | **Adequate** | No service × location pages, no geo coordinates |
| Forms | **Adequate** | `novalidate` with no client-side validation to replace it |
| Motion / performance | **Mixed** | ~2.25s splash screen on every page view |
| Typography | **Good** | Third-party font on the critical path |
| Content depth | **Weak** | Blog cannot contain headings or internal links |
| Legal / trust | **Risky** | Legal pages claim to have been updated today, every day |

---

## The three things that matter most

Before the detailed list, these are the findings that would change the business outcome.

### 1. You cannot see a single conversion

`SiteSettings` has GA4, Meta Pixel and Search Console **all blank**. Even once they are filled in, `static/js/main.js` fires **no conversion event anywhere** — not on enquiry submit, not on the thank-you page, not on WhatsApp clicks, not on click-to-call, not on newsletter signup.

The home page alone has 8 links to the contact form and 8 links out to WhatsApp. **None of the 16 are tracked.** WhatsApp is almost certainly the primary conversion path for a Kenyan services business, and it is entirely invisible.

Everything else in this audit is an opinion until this is fixed. With it fixed, the rest becomes measurable.

### 2. Every share of this site is a bare link

Verified: **zero `og:image` tags across all 10 pages.** `default_social_image` is blank and no page sets one.

In Kenya, links travel on WhatsApp. A WhatsApp link with no preview image is a grey box — it looks broken, and it converts far worse than a card with an image. The same applies to Facebook and LinkedIn shares. This is the cheapest high-impact fix on the list.

### 3. The pages that should rank carry almost no content

Measured from the database:

| Page type | Words of body content |
|---|---|
| Service pages (7) | **55 – 88** |
| Location pages (4) | **122 – 155** |
| Blog posts (3) | **212 – 261** |

Service pages are the pages targeting your commercial money keywords. At 55–88 words they will not rank against competitors, and answer engines have nothing to extract or cite. This is the single largest gap between the site's ambition and its current capability.

---

## 1. Structural errors

### S-01 · Two CSS variables are used but never defined — P2
`--brand-hover` is referenced at `static/css/main.css:333` (`.btn--ghost:hover`) and `static/css/main.css:1646` (`.prose a:hover`) but is defined nowhere in the token block. An undefined custom property is invalid at computed-value time, so `color` falls back to *inherit* rather than staying put.

**Effect:** every "Explore →", "See all services →", "Read the blog →" ghost link, and every link inside blog and legal prose, changes to an unpredictable inherited colour on hover instead of darkening as intended.
**Fix:** define `--brand-hover` (e.g. `#A83310`, already proven at 6.68:1) or point both rules at the existing `--brand-btn-hover`.
**Benefit:** hover affordance works as designed on every text link in the site.

### S-02 · Home page section numbers run 01, 02, 03, **07**, 04, 05, 06 — P2
`templates/core/home.html:280` labels the Growth Packages section `07`, and it sits between `03` (website types) and `04` (growth system).

**Effect:** the editorial numbering was added to make the page feel structured; out of order it does the opposite and reads as a mistake on a page selling attention to detail.
**Fix:** renumber in DOM order, or drop the numbers from the two sections that were inserted later.
**Benefit:** the page reads as deliberately sequenced, which is the whole point of the device.

### S-03 · Letter-initial icons survived the icon replacement in four places — P2
The earlier change replaced service letter initials with SVG icons, but missed:

- `templates/core/web_development.html:114, 119, 124` — the SEO/AEO/GEO cards still render bare letters **"S"**, **"A"**, **"G"**.
- `templates/locations/location_list.html:21` — county cards render `{{ location.county|slice:":1" }}`, so **Kajiado and Kiambu both display "K"**, and Machakos and Nairobi display "M" and "N" with no meaning attached.

**Effect:** the exact pattern you asked to remove is still live on two pages, and on the locations page two of four cards are visually identical.
**Fix:** three new SVGs for search/answer/AI, and either county-appropriate marks or a map-pin icon for locations.
**Benefit:** visual consistency across every card in the site.

### S-04 · Desktop and mobile navigation don't match — P2
`templates/partials/header.html:10-18` (desktop) has 7 items. `:43-52` (mobile) has 8 — it includes **Areas We Serve**, which desktop omits. The footer "Explore" column lists Areas We Serve but omits **Contact**.

**Effect:** a desktop visitor cannot reach the location pages from the header. Your local SEO landing pages are less discoverable on the device where most research happens.
**Fix:** one navigation source of truth; decide whether Areas We Serve is a primary nav item and apply that decision in all three places.
**Benefit:** consistent navigation, better internal link equity to the location pages.

### S-05 · `/case-studies/` is an orphaned, empty page — and it is in the sitemap — P1
Verified: **zero internal links** point to `/case-studies/` from any of the 10 rendered pages (the links are inside `{% if case_studies %}` guards, and there are no case studies). The page is nonetheless listed in `sitemap.xml` at priority 0.8.

**Effect:** you are actively submitting an empty page to Google. It is thin content on a brand-new domain, which is exactly the signal a new site cannot afford.
**Fix:** exclude it from the sitemap and `noindex` it while empty; the view already knows whether the list is empty. Re-include automatically once the first case study is published.
**Benefit:** no thin-content signal, no crawl budget wasted, no dead link if it is ever linked.

### S-06 · Three of five blog categories are empty but are published — P2
Measured: `ads-performance` (0 posts), `case-studies` (0), `social-media` (0); `seo-aeo` (2), `web-development` (1). All five render as clickable tags on `/blog/` and all five appear in `sitemap.xml`.

**Effect:** three of the five category links a reader can click lead to "No posts in this category yet — check back soon." Three more thin pages submitted to Google.
**Fix:** only render and submit categories that have at least one published post.
**Benefit:** no dead-end clicks, three fewer thin URLs.

### S-07 · One of seven services never appears on the home page — P2
`apps/core/views.py:21` slices `[:6]`. There are 7 active services, so **Digital Ads Management** is never shown — despite being stage 04 of the Growth System that the same page explains.

**Effect:** the home page argues that ads matter, then doesn't show the service. It also receives only one inbound internal link site-wide.
**Fix:** show all 7 (the showcase is a slider — it costs no vertical space), or pick the 6 deliberately and say so.
**Benefit:** the services shown match the story told.

### S-08 · `matchMedia().addEventListener` is unguarded — P2
`static/js/main.js:126`. The rest of the file is carefully written for old browsers (`var`, `Array.prototype.slice.call`, guarded `fetch`, guarded `IntersectionObserver`), then uses an API unsupported on Safari ≤13.7 / iOS ≤13.

**Effect:** on those browsers this throws inside `initMobileNav()`, aborting `init()` before `initReveals`, `initBackToTop`, `initNewsletter`, `initCookieConsent`, the hero carousel and the services showcase. The consequence worth caring about: **the cookie banner never appears, so analytics never load** — those users become invisible even after you fix finding 1. The hero also freezes on slide 1.
*(Credit where due: because reveals are only armed by JS, content stays visible. The progressive-enhancement design saves the page from being blank.)*
**Fix:** feature-detect `addEventListener` on the MediaQueryList, or wrap each init in try/catch so one failure cannot cascade.
**Benefit:** one old browser can no longer silently disable analytics and the carousel.

### S-09 · Canonical URLs and the sitemap derive from different sources — P2
`apps/core/seo.py` builds canonicals from `SITE_BASE_URL`. `sitemap.xml` and `robots.txt` use `request.get_host()`.

**Effect:** the day these disagree — `www` vs bare domain, or a stale env var after the HostAfrica move — the sitemap will list URLs whose canonical tag points somewhere else. Google treats that as a conflicting signal and it is very hard to notice.
**Fix:** one source of truth for the site's absolute base URL, used by both.
**Benefit:** removes a silent, high-cost failure mode at exactly the moment you switch domains.

### S-10 · Three unused packages ship to production — P3
`markdown`, `bleach` and `python-slugify` are in `requirements.txt`. Verified: **no imports anywhere** in `apps/` or `veeagency/`.

This is not just tidiness — it is the fossil of a decision. `markdown` + `bleach` were added to render blog bodies as rich text, and that never got wired up. See **C-01**.

---

## 2. Customer journeys

I walked five journeys end to end.

### J-1 · Cold Google search → service page → enquiry
`/services/seo-optimization/` → aside panel → "Check if this is your priority" → contact form.

**Works.** The CTA copy is specific, the aside repeats contact options, the breadcrumb orients.
**Breaks:** the page gives a visitor **75 words** to decide with. No FAQ, no "what this looks like in month one", no price justification, no link to a relevant blog post or to the packages page. A stranger arriving here has nothing to build confidence on before being asked to commit.

### J-2 · Packages → choose a plan → enquiry
`/packages/` → "Choose Premium Growth" → `/contact/?service=premium`.

**Works:** verified that the dropdown is correctly preselected to `premium`.
**Breaks:** **nothing on the contact page acknowledges the choice.** The visitor clicked a specific, priced commitment and landed on a generic form with a lead reading "Let's see what's holding you back". The momentum from choosing a plan is thrown away.

**Fix:** when `?service=` is present, lead with it — "You're enquiring about Premium Growth — KES 45,000/month" and adjust the heading and button copy.
**Benefit:** continuity between the decision and the form is one of the highest-leverage conversion fixes available on any pricing site.

### J-3 · Home → website type → quote
`/` → website-type mockups → ...nowhere.

**Breaks:** the three mockup cards do exactly the right job of self-identification — "I'm an e-commerce business" — and then offer **no CTA at all**. The visitor has to scroll back up or find the generic buttons below the block.

**Fix:** a CTA per card, prefilled: "Get a quote for an e-commerce site".
**Benefit:** converts an identification moment into an enquiry at the point of highest intent.

### J-4 · Blog post → audit
`/blog/website-cost-kenya/` → CTA band → contact.

**Works:** the CTA is contextual and well written.
**Breaks:** the post cannot link to `/web-development/` or `/packages/` — see **C-01**. A reader who has just read "KES 30,000 is a realistic starting point" has no in-content path to the page that explains that offer.

### J-5 · Blog category or author page → anywhere
`/blog/category/social-media/` → "No posts in this category yet" → `← All insights`.
`/blog/author/<user>/` → article list → nothing.

**Breaks:** both are dead ends with no audit CTA. The author page additionally has no bio (not supplied yet), so it is currently an H1 and a list.

---

## 3. UI / UX gaps and inconsistencies

### U-01 · The packages page has no comparison — P1
Three cards, each with a long feature list (4, 8 and 7 items). A visitor cannot see **what Standard adds over Essential** without reading both lists and diffing them mentally.

**Fix:** a feature × tier comparison table under the cards (cards for the pitch, table for the decision).
**Benefit:** this is the standard pattern for a reason — it converts the "which one" question from work into a glance, and it reliably pushes buyers up a tier.

### U-02 · No objection handling on the pricing page — P1
There is no FAQ on `/packages/`. Unanswered: Is there a contract? What is the minimum term? Can I cancel? Is there a setup fee? What happens to my accounts if I leave? Do I pay for ad spend separately? *(The last one is answered — but only as a small dim line under the cards.)*

**Fix:** a pricing FAQ, with FAQ schema (see **E-06**).
**Benefit:** objections handled on the page instead of in an email you may never receive. Also the single best AEO opportunity on the site.

### U-03 · Permanent struck-through prices — P1
All three monthly packages carry a `reference_price` shown struck through: 18,000→15,000, 30,000→25,000, 55,000→45,000. It is permanent, unexplained and undated.

**Effect:** a discount that never ends is not a discount. It reads as the oldest trick in retail, on a page headed "Clear prices. No guessing." — which actively undercuts the positioning the whole site is built on. It is also the kind of claim consumer-protection regulators look at.
**Fix:** either remove it, or state what it is ("Launch pricing — held until 31 December 2026") and honour the date.
**Benefit:** protects the honesty positioning, which is your actual differentiator.

### U-04 · The service prices argue against the packages — P2
Measured: Website Management KES 5,000, Competitor Analysis 5,000, Digital Ads Management 5,000, SEO 10,000, SEO+AEO 15,000 — versus Essential Growth at 15,000/month.

**Effect:** an attentive visitor can price up individual services and conclude the package is not obviously better value. The site never explains why the bundle is worth more than its parts (it is — the Growth System section makes exactly that argument — but the two are never connected).
**Fix:** either connect them explicitly on the packages page, or reconsider whether per-service "from" prices belong on the site at all.
**Benefit:** the pricing architecture stops competing with itself.

### U-05 · Ten near-identical CTA bands — P2
`.cta-band` appears **10 times** across 9 templates, and three of them open with the identical eyebrow "Free audit" (`packages/package_list.html:63`, `services/service_list.html:36`, `core/about.html:98`).

**Effect:** the CTA copy was rewritten to be context-specific and it is genuinely good — but the *container* is identical every time, so by the third page it reads as furniture and gets scrolled past.
**Fix:** two or three visual variants (full-bleed dark, inline split, compact bar) assigned by page role.
**Benefit:** the ask stays visible instead of becoming wallpaper.

### U-06 · WhatsApp exits are everywhere and untracked — P2
8 WhatsApp links on the home page, all `target="_blank"`.

**Effect:** WhatsApp is probably your best converting channel, and it is simultaneously your biggest unmeasured leak. Every one of those clicks leaves the site with no record.
**Fix:** track them (see **M-01**), and consider whether 8 on one page is more than the funnel needs.
**Benefit:** you find out which sections actually drive contact.

### U-07 · Case-study and testimonial sections are invisible, not "empty" — P3
The empty-state rule is correctly applied — no fabricated proof, which is right. But the effect is that a first-time visitor sees **no social proof of any kind** and the site never acknowledges why.

**Fix:** consider one honest line where the proof would go — "We're new enough that we'd rather show you the work than someone else's logo. Ask us for a reference." This is a judgement call, not a defect.
**Benefit:** turns an absence into a statement of the same honesty the rest of the site trades on.

### U-08 · CTA voice slips on one page — P3
`web_development.html` uses **"Get Your Website"** (title case) twice. Every other CTA on the site is sentence case and outcome-led ("Get my free audit", "Get a recommendation").

### U-09 · "Related services" aren't related — P3
`apps/services/views.py` picks `exclude(pk=service.pk)[:3]` — the first three other services in display order — and the heading says "Works well with".

**Fix:** a `related` M2M field, or order by shared attributes. Small change, removes a small dishonesty.

### U-10 · No response-time commitment near the submit button — P2
The contact page promises an honest audit but never says **when**. "We read your enquiry" gives no timeframe.

**Fix:** a concrete promise you can keep ("We reply within one working day").
**Benefit:** removes the commonest unspoken hesitation at the point of submission.

---

## 4. Accessibility — measured

All ratios below were computed, not estimated.

### A-01 · The focus indicator fails WCAG 1.4.11 on both backgrounds — P1

| Context | Measured | Required |
|---|---|---|
| `--focus-ring` on the page background | **2.48:1** | 3:1 |
| `--focus-ring` on `.section--dark` | **1.77:1** | 3:1 |

`:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(184,58,18,.55) }` is a single global token that is too faint on light and nearly invisible on dark.

**Effect:** keyboard users — including anyone using a phone with a Bluetooth keyboard, and every screen-reader user — can lose track of where they are. On the dark band it is effectively no indicator at all.
**Fix:** raise the alpha and add a light outer ring so the indicator works on any background; override the token inside `.section--dark`. Keep a real `outline` alongside the shadow so it survives forced-colors mode.
**Benefit:** the single highest-value accessibility fix here, and it costs two lines.

### A-02 · Control boundaries fail 1.4.11 — P1

| Element | Measured | Required |
|---|---|---|
| Form input border (`--border-strong` on white) | **1.47:1** | 3:1 |
| `.btn--secondary` border on the page background | **1.46:1** | 3:1 |
| `.section--dark .btn--secondary` border | **2.13:1** | 3:1 |

**Effect:** the enquiry form — the conversion surface of the entire site — has input boundaries a visually impaired user cannot reliably see. The secondary button's border is its *only* visual boundary; at 1.46:1 the button edge effectively disappears. "Chat on WhatsApp" is a secondary button in many places.
**Fix:** a dedicated `--border-control` token at ≥3:1 for interactive boundaries, kept separate from decorative card borders (which do not need to meet this).
**Benefit:** AA compliance on the elements that matter, without darkening the whole design.

### A-03 · Carousel dots fail target size — P1
`.carousel__dot` renders at **32 × 4 px**; `.showcase__dot` at **28 × 4 px**. WCAG 2.5.8 requires 24 × 24 px.

**Effect:** on a phone these are close to unhittable. On the services showcase they are the only visible way to jump between services.
**Fix:** keep the 4px visual bar, wrap it in a transparent 24–44px tall hit area (padding, not size).
**Benefit:** the controls become usable on the device most of your visitors are on. No visual change at all.

### A-04 · Both carousels autoplay with no pause control — P1 (WCAG 2.2.2, Level A)
The hero carousel advances every **6s**; the services showcase every **5s**. Both pause on hover, focus, pointer-down and hidden tab — that is good engineering, but WCAG 2.2.2 requires an explicit, discoverable **pause/stop mechanism** for anything that auto-updates for more than 5 seconds. Hover is not one.

**Effect:** a Level A failure — the lowest bar in the standard. Also a practical one: a slow reader on the services showcase gets moved off the card mid-sentence.
**Fix:** a visible pause/play toggle in both control rows.
**Benefit:** Level A compliance, and readers stop being interrupted.

### A-05 · Invalid ARIA tab pattern on the hero carousel — P2
The dots use `role="tablist"` and `role="tab"`, but the slides are `role="group"` with `aria-roledescription="slide"`. There are **no `tabpanel`s and no `aria-controls`**, so the tabs control nothing as far as assistive technology is concerned.

**Fix:** drop the tab roles and use plain buttons with `aria-label` (the carousel pattern), since the slides are already correctly marked up as slides.
**Benefit:** screen readers describe what is actually there.

### A-06 · Two pages skip a heading level — P2
Verified from the rendered DOM:

- `/blog/` — `h1` → `h3` (post cards are `h3`, with no section `h2`)
- `/services/` — `h1` → `h3` (service cards are `h3`, no section `h2`)

Related: card headings are inconsistent site-wide — `/locations/` uses `h2` for county cards while `/services/` and `/blog/` use `h3` for equivalent cards.

**Fix:** a visually-hidden `h2` per listing section, and one rule for card heading level.
**Benefit:** correct document outline for screen readers and for Google's content parsing.

### A-07 · Five rotating `<h2>`s sit at the top of the home page outline — P2
The hero carousel slide titles are `<h2>` elements. Four of the five are `aria-hidden` and invisible at any given moment, but all five are in the outline — **above** "Being online isn't the same as being found", which is the page's real first heading.

**Effect:** the document outline says the page is about five rotating topics before it says what the page argues.
**Fix:** make slide titles `<p>` with display styling, or move the carousel after the first content section in the DOM.
**Benefit:** cleaner outline for both assistive tech and search.

### A-08 · Gradient headline text disappears in forced-colors mode — P2
`.accent` uses `background-clip: text; color: transparent`. Windows High Contrast Mode overrides backgrounds but honours `color: transparent`.

**Effect:** "Grow online." on the home page, "earns its cost" on web-development, and "Straight answers." on about become **invisible** for high-contrast users — losing the emphasised half of each H1.
**Fix:** `@media (forced-colors: active) { .accent { color: CanvasText; background: none; } }`.

### A-09 · The cookie banner never receives focus — P2
It is `role="dialog"` and appears programmatically, but focus is not moved into it. A keyboard or screen-reader user is not told it exists and must tab to the end of the document to find it.
*(The consent logic itself is well built — decline is equally prominent, Escape declines rather than dismisses, and nothing loads before consent. This is a discoverability gap, not a consent-integrity one.)*

### A-10 · Field hint text is not announced — P2
`.field__help` spans in `templates/contact/contact.html:43, 56` have no `id`. Django correctly sets `aria-describedby` to the *error* list, so the hints ("Optional — but it's the fastest way to reach you", "A rough range is enough") are never associated with their inputs.

**Effect:** a screen-reader user does not learn that phone and budget are optional — likely to abandon at a field they think is required.
**Fix:** give each hint an id and include it in the field's `aria-describedby`.

*(Worth noting for balance: Django 5.2 emits `aria-invalid="true"` and `aria-describedby="id_x_error"` correctly — verified in the rendered error markup. Error association is not the problem; hint association is.)*

### A-11 · Floating buttons ignore the iOS safe area — P3
`.floats` uses `bottom: clamp(0.9rem, 3vw, 1.75rem)` with no `env(safe-area-inset-bottom)`.

**Effect:** on iPhones with a home indicator, the WhatsApp and back-to-top buttons can sit partly under it.

---

## 5. Contrast and colour

### C-01 · Brand orange used as link text, failing AA — P2
`--brand` `#E64A1A` on the page background measures **3.76:1** — below the 4.5:1 required for body text. `CLAUDE.md` already states this rule ("`--brand` is for fills and decoration only"), and it is violated in five places:

- `templates/404.html:19`
- `templates/contact/thank_you.html:21, 22`
- `static/css/main.css:1707` (`a.tag:hover`)
- `static/css/main.css:1767` (`.pagination a:hover`)

**Effect:** on the thank-you page — a page every converting visitor sees — both onward links fail contrast.
**Fix:** `--brand-ink` (`#B83A12`, measured 5.52:1) in all five.

**For the record, everything else measured clean:**

| Pair | Measured | AA |
|---|---|---|
| Body text on background | 17.59:1 | Pass |
| `--text-muted` | 7.50:1 | Pass |
| `--text-dim` on tinted surface | 4.92:1 | Pass |
| `--brand-ink` text | 5.52:1 | Pass |
| White on primary button | 5.05:1 | Pass |
| Dark text on WhatsApp green | 8.01:1 | Pass |
| Dark band body copy | 11.03:1 | Pass |
| Dark band `.dim` | 6.21:1 | Pass |
| Staging banner | 8.16:1 | Pass |

The text palette is genuinely well constructed. The failures are all in *non-text* contrast (A-02) and these five stragglers.

---

## 6. SEO

### E-01 · Service pages are too thin to rank — P1
Measured: **55–88 words** of body content across all seven.

| Service | Words |
|---|---|
| website-creation | 88 |
| digital-ads-management | 81 |
| seo-optimization | 75 |
| website-audit-revamp | 71 |
| seo-aeo-optimization | 67 |
| competitor-analysis | 64 |
| website-management | 55 |

**Effect:** these are your commercial landing pages. At this depth they cannot compete for "SEO services Kenya" or "website design Nairobi", and there is nothing for an answer engine to quote.
**Fix:** 600–900 words each, structured as: what it is → who it is for → what you actually do → what changes → what it costs → 3–4 FAQs. The existing `deliverables` JSON gives you the skeleton.
**Benefit:** the highest-ROI SEO work available — seven commercial pages moving from unrankable to competitive.

### E-02 · The blog cannot contain headings, lists or internal links — P1
`BlogPost.body` is a plain `TextField` rendered with `{{ post.body|linebreaks }}`, which escapes HTML.

This is not theoretical. The seeded post `website-cost-kenya` was **written with five subheadings** — "What the site has to do", "Whether the content exists", "Whether search was considered", "What happens after launch", "A reasonable expectation" — and every one of them renders as an ordinary paragraph. The reader sees a wall of text; Google sees no structure.

**The compounding cost:** the blog is normally a site's main internal-linking engine. Here it **cannot link to a single service or package page.** That is why the internal link graph is as thin as it is (service detail pages get 2 inbound links each).

**Fix:** render the body as Markdown, sanitised. `markdown` and `bleach` are **already in `requirements.txt` and already installed** — this was clearly the original intent and was never wired up.
**Benefit:** proper heading structure, internal linking, lists and emphasis — unlocked for every future post as well as the three that exist.

### E-03 · Blog posts and location pages are short — P1
Blog posts: **212–261 words**. Location pages: **122–155 words**.

The content itself is good — the location pages are genuinely differentiated per county (Kajiado talks about Kitengela and Ongata Rongai; Nairobi talks about neighbourhood-level search), which correctly avoids the doorway-page trap. They are just too short to win.

**Fix:** blog posts to 800–1,200 words; location pages to 400–600 with a local FAQ and named towns.

### E-04 · Four meta descriptions are truncated in search results — P2
Measured character counts:

| Page | Description | Title |
|---|---|---|
| `/web-development/` | **198** | 50 |
| `/services/` | **198** | 54 |
| `/` (home) | **192** | 49 |
| `/blog/` | **167** | **64** |

Google truncates around 155–160 characters. In all four cases the truncated tail is the part carrying the local keywords and the reason to click.

Additionally: **zero services and zero blog posts have a `meta_description` set** — all fall back to a truncated `short_description` or `excerpt`, which were written as page copy, not as search snippets.

### E-05 · No BreadcrumbList schema — P2
Breadcrumbs are rendered on service detail, location detail, web-development, blog posts, author and category pages — with no corresponding schema.

**Benefit of fixing:** breadcrumb trails in search results instead of a raw URL. Measurably improves click-through, and it is a template-level change.

### E-06 · FAQ schema exists only on the home page and blog posts — P1
`/packages/`, `/services/`, all seven service detail pages, `/web-development/` and all four location pages have **no FAQ content and no FAQ schema**.

**Effect:** the queries that actually convert for this business are questions — "how much does a website cost in Nairobi", "what does SEO cost in Kenya", "do I need a booking system for my hotel". You answer the first one on the home page and nowhere else.
**Fix:** 3–5 FAQs per service page, per location page, and on the packages page, all with schema.
**Benefit:** this is the single biggest AEO and featured-snippet opportunity on the site.

### E-07 · The pricing page publishes no pricing schema — P1
`/packages/` — the money page, headed "Clear prices. No guessing." — has **no `Offer`, `Product` or `OfferCatalog` markup**. Its only structured data is the generic `ProfessionalService` block that every page carries.

**Fix:** `OfferCatalog` with an `Offer` per package.
**Benefit:** prices become extractable by Google and by AI assistants — directly serving the AEO/GEO positioning the site sells.

### E-08 · The business entity is duplicated on every page with no `@id` — P2
The full `ProfessionalService` block (address, telephone, priceRange, areaServed) is emitted on all 10+ pages including the Privacy Policy. Without an `@id`, each page declares a **separate, unlinked business entity**.

**Fix:** one canonical entity on the home page with `"@id": "https://veeagency.co.ke/#organization"`, and `@id` references elsewhere.
**Benefit:** one consolidated entity for Google's knowledge graph instead of eleven fragments.

### E-09 · "From" prices published as fixed prices — P2
`templates/services/service_detail.html` emits `"price": "<starting_price>"` for a price the page itself displays as "Starting from". Same pattern on `/web-development/`.

**Fix:** `PriceSpecification` with `minPrice`.
**Benefit:** accurate rich results; avoids publishing a price you may not honour.

### E-10 · Local signals are incomplete — P2
`ProfessionalService` has no `geo` coordinates, no `openingHours`, no `hasMap`, no `sameAs` (no social URLs exist yet), and no link to a Google Business Profile.

**Effect:** for local-pack ranking and for AI assistants answering "digital agency near Syokimau", these are the fields that matter most and they are all absent.

### E-11 · No service × location pages — P2
You have 7 services and 4 priority counties and target 28 combinations of intent — but only 11 pages. "SEO services in Nairobi" has no page.

**Fix:** start with the 6–8 highest-intent combinations, written individually. **Do not generate all 28** — that is the doorway-page pattern that gets sites penalised, and the existing location pages show you know how to write genuinely distinct local copy.

### E-12 · Sitemap priorities are inverted and static routes have no `lastmod` — P2
The homepage is priority **0.8** while service pages are **0.9**. All four legal pages are also 0.8. No static route carries `lastmod`. Plus the empty `/case-studies/` and three empty categories (S-05, S-06).

### E-13 · No author E-E-A-T — P2
`BlogPosting.author` is `{"@type":"Person","name":"..."}` with no `url`. No `Person` schema on the author page. No author bio box on posts. The `User` model has `bio`, `headshot`, `job_title`, `facebook` and `instagram` fields — **the templates use `bio` and `headshot` only on the author page, and ignore `job_title` links and both socials entirely.**

**Effect:** for a site whose blog gives financial advice ("KES 30,000 is a realistic starting point"), Google's helpful-content signals want to know who is saying it.

### E-14 · `BlogPosting` has no `image` and no `publisher.logo` — P2
Google's article rich results expect both. Currently no post has a featured image either (see below).

---

## 7. Images

### I-01 · The site contains no content images at all — P1
Verified across all 10 rendered pages: the **only** `<img>` elements are the 34×34 logo in the header and footer, and the 64×64 preloader logo. No hero image, no service images, no blog featured images, no author headshot, no OG image.

**Effect:**
- Every social share is a bare link (see the summary, item 2).
- Blog cards are text-only, which makes the blog listing look unfinished.
- The design leans entirely on type and CSS gradients. That is a defensible aesthetic and it currently holds together — but "premium agency" is a claim that visitors partly judge on visual richness.

**Fix, in priority order:** (1) an OG image, (2) blog featured images, (3) a headshot, (4) optional hero imagery.
*The Pillow downscale-on-upload pipeline is already built and tested, so the infrastructure is ready.*

### I-02 · Image dimensions are not reserved — P2
`templates/blog/post_detail.html` and `templates/blog/author_detail.html` render images with no `width`/`height`.

**Effect:** cumulative layout shift as soon as images are added — a Core Web Vitals penalty and a visibly janky page.
**Fix:** set explicit dimensions or an `aspect-ratio`. Cheap now, annoying later.

### I-03 · A 512×512 logo renders at 34×34 — P3
`static/img/vee-logo.png` is 512×512 (14.8 KB), used at 34px in the header and footer and 64px in the preloader.

---

## 8. Animations, transitions and performance

### P-01 · A full-screen splash blocks every page view — P1
`static/css/main.css:2145`: `animation: preloader-out 0.45s var(--ease) 1.8s forwards`.

The preloader is an **opaque, full-viewport overlay**. CSS holds it for **1.8s** then fades for **0.45s** — up to **2.25 seconds**. JS can dismiss it earlier (on `load` + 200ms), so on a fast connection it clears in ~0.6s. On a slow Kenyan mobile connection, the CSS timer governs.

**Effect:** it runs on **every navigation**, not just the first visit. A visitor moving home → services → packages sits through it three times. It covers the hero during the window Chrome measures Largest Contentful Paint. Splash screens are one of the most reliably conversion-negative patterns in frontend practice, and this one is on a site whose own blog argues that speed matters.

*Credit: the engineering is careful — it is CSS-driven so a JS failure cannot trap the page, and it is skipped entirely under reduced motion and with JS disabled. The problem is that it exists, not how it is built.*

**Fix:** show it on first visit only (a `sessionStorage` flag), cut the CSS delay to ~600ms, or remove it.
**Benefit:** roughly 1.5–2 seconds returned on every repeat pageview, and a real LCP improvement.

### P-02 · Fonts load from a third party on the critical path — P1
`templates/base.html` loads Inter (400/500/600) and Space Grotesk (500/600/700) from `fonts.googleapis.com` — **6 font files across 2 extra origins**, with a render-blocking stylesheet.

Even with the `preconnect` hints present, this costs two additional DNS + TLS handshakes before any text can render in the intended face. On Kenyan mobile latency that is significant. There is also no `preload` for the font files themselves, so a flash of fallback text happens on every first visit.

**And it is a privacy question:** Google Fonts transmits the visitor's IP to Google on every page load — before any consent, and the Privacy Policy does not mention it (see **L-03**).

**Fix:** self-host the two families, subsetted to Latin, with `font-display: swap` and a `preload` for the two most-used weights.
**Benefit:** removes two third-party round trips from the critical path, removes the privacy disclosure problem entirely, and removes a dependency on a service outside your control.

### P-03 · Reduced-motion handling is good — no action
Checked and confirmed: `prefers-reduced-motion` disables smooth scrolling, removes the preloader, neutralises all transitions, forces reveals visible, disables hover transforms, and both carousels check the flag before autoplaying. This is done properly.

One small gap (**P-03a, P3**): `reduceMotion` is read once at load with no `change` listener, so toggling the OS setting mid-session has no effect until reload.

### P-04 · The reveal safety net is well designed — no action
`.reveal` styles are only armed *after* JS confirms it can disarm them, plus a 4-second hard deadline. Content can never be permanently hidden by a JS failure. This is the right pattern.

### P-05 · No caching layer — P3
No `CACHES` configured. `SiteSettings.load()` runs a query on **every request** via the context processor. No template fragment caching on the services/packages/blog listings.

At current traffic this is invisible. On a SQLite-backed production site it is worth doing before traffic arrives, not after.

---

## 9. Forms

### F-01 · `novalidate` with nothing to replace it — P1
`templates/contact/contact.html:19` sets `novalidate`. Verified: the rendered inputs **do** carry `required` and `type="email"` — so the browser could validate for free — and `static/js/main.js` contains **no form validation code at all** (only the newsletter AJAX handler).

**Effect:** `novalidate` strictly removes protection and adds nothing. Every mistake — a blank name, a typo'd email — costs a full page round trip on mobile data.
**Fix:** either remove `novalidate` and style `:user-invalid`, or add the JS layer that `novalidate` implies.
**Benefit:** errors surface instantly and free, on the highest-value form on the site.

### F-02 · Failed submissions reload to the top with no summary — P1
Verified by submitting an invalid form: field errors render correctly inline, but there is **no error summary at the top of the form** (`.form__errors` is only used for non-field errors) and **no focus is moved** to the first invalid field.

**Effect:** the user lands back at the page header — "Free audit · No obligation" — with no indication anything went wrong, and must scroll and hunt.
**Fix:** an error summary above the form, linked to each invalid field, focused on render.
**Benefit:** recovers submissions that currently get abandoned.

### F-03 · The newsletter form has no spam protection — P2
`apps/contact/views.py:newsletter_subscribe` has **no honeypot and no rate limit**, while the contact form has both. It is `@require_POST` and CSRF-protected, which is meaningful but not sufficient.

**Effect:** the `NewsletterSubscriber` table can be filled with junk; because it uses `update_or_create` on a unique email, each junk address is a permanent row.

### F-04 · Unvalidated redirect via the Referer header — P2
`apps/contact/views.py`, non-AJAX newsletter fallback: `redirect(request.META.get("HTTP_REFERER") or reverse("core:home"))`.

`HTTP_REFERER` is attacker-influenced and is passed to `redirect()` without validation. CSRF protection makes this hard to exploit, so the severity is low — but it is a genuine open-redirect shape and the fix is one call to `url_has_allowed_host_and_scheme()`.

### F-05 · The rate limit is trivially bypassable, and can block real customers — P2
`apps/contact/utils.py:get_client_ip` takes the first value of `X-Forwarded-For` with **no trusted-proxy check**. Anyone can set that header to a random value per request and bypass the 3/hour limit entirely.

**The mirror-image risk matters more here:** Kenyan mobile carriers use carrier-grade NAT, so many legitimate users share one public IP. Three enquiries per hour from a shared Safaricom IP is plausible, and the fourth real customer is told to "call or WhatsApp us instead."

**Fix:** derive the client IP from a known proxy depth, and consider raising the limit or keying on IP + email.

### F-06 · Arrival from a package CTA is not acknowledged — P2
See **J-2**. The prefill works; the page doesn't say so.

---

## 10. Email and reliability

### R-01 · Enquiry emails are sent synchronously with no timeout — P1
`apps/contact/services.py` sends **two SMTP messages inside the request cycle**, and `veeagency/settings/prod.py` sets no `EMAIL_TIMEOUT`. Python's default socket timeout is `None` — infinite.

**Effect, concretely:** if the SMTP host is slow or hanging (common with shared hosting, and HostAfrica's mail service is the target), the request blocks until Gunicorn's worker timeout kills it. The visitor's enquiry **has already been saved**, but they see a 502 instead of the thank-you page. They will assume it failed and either resubmit or leave. You lose the conversion you already won, and you never find out.

**Fix:** set `EMAIL_TIMEOUT` (10s), and move sending off the request path — a thread is sufficient at this volume. The code already correctly treats the database row as the primary record and flags `notification_sent`, so the groundwork is there.
**Benefit:** removes the one failure mode that can lose a captured lead at the moment of conversion.

---

## 11. Legal and trust

### L-01 · Every legal page claims to have been updated today — P1
`templates/core/legal/_base_legal.html:12`:
```
Last updated: {% now "j F Y" %}
```
This renders **the current date on every page load**. The Privacy Policy, Terms, Cookie Policy and Disclaimer all claim to have been revised today, every day, forever.

It is also self-contradicting: the Privacy Policy states *"The date at the top shows when it was last changed."* It does not.

**Effect:** a false statement on a legal page, on a site whose entire positioning is honesty. If a dispute ever turned on which version of the Terms a client agreed to, this is the field that would be examined.
**Fix:** a real `updated_at` per document, edited when the document is edited.
**Benefit:** removes a factual falsehood and makes the legal pages actually defensible.

### L-02 · The Meta Pixel is presented as an analytics cookie — P1
The banner offers **"Accept analytics"** and says *"We'd also like to use analytics cookies to understand which pages people find useful."* The same accept action loads the **Meta Pixel**, which is advertising and retargeting infrastructure, not analytics.

**Effect:** consent must be informed and specific. Describing retargeting as "understanding which pages people find useful" is not accurate, and the Cookie Policy repeats the framing.
**Fix:** name both purposes ("analytics and advertising"), or split them into two toggles.
**Benefit:** the consent mechanism becomes as honest as the rest of the site — and the existing implementation is otherwise genuinely well built, so this is a copy fix, not a rebuild.

### L-03 · The Privacy Policy has real gaps — P1 (for the lawyer review already scheduled)
Against Kenya's Data Protection Act 2019, the current text is missing:

1. **The data controller's identity** — no registered name or ODPC registration.
2. **The right to lodge a complaint with the Data Commissioner** — the rights list omits it.
3. **Cross-border transfer disclosure** — hosting, email and (once enabled) Google/Meta involve transfers outside Kenya; DPA ss.48–49 govern this and it is not mentioned.
4. **Google Fonts** — the visitor's IP goes to Google on every page load, before consent. The "Sharing" section claims to cover service providers and does not mention it.
5. **Analytics and the Pixel** — neither is named as a recipient, and "Information we collect" does not mention analytics data at all.
6. **A concrete retention period** — "as long as needed" is not a period.

**Fix:** hand this list to the lawyer alongside the draft. *(Self-hosting the fonts per **P-02** removes item 4 entirely rather than disclosing it.)*

### L-04 · The Cookie Policy names no cookies — P2
It explains the categories well but never lists a single cookie name, provider or duration.

### L-05 · The newsletter signup has no privacy notice — P2
The footer form collects an email address with no link to the Privacy Policy and no consent statement. The contact form does this correctly — the newsletter does not.

---

## 12. Security and configuration

Baseline is good: prod sets SSL redirect, HSTS, secure cookies, nosniff, `X-Frame-Options: DENY`, a referrer policy, and secrets come from the environment. 63 tests pass. The SQLite-outside-the-web-root requirement is documented and enforced by configuration.

Remaining items:

### X-01 · No Content-Security-Policy or Permissions-Policy — P2
Neither header is set. Given the site deliberately injects third-party scripts after consent, a CSP is the control that would guarantee nothing *else* ever gets injected.

### X-02 · HSTS preload on a staging subdomain — P3
`SECURE_HSTS_PRELOAD = True` with `includeSubDomains` is applied on `*.onrender.com`, a domain you do not control. Harmless in practice; worth scoping to production.

### X-03 · Unvalidated redirect and spoofable rate limit — see **F-04**, **F-05**.

---

## Remediation plan

Sequenced so each phase makes the next one measurable.

### Phase 0 — Before HostAfrica launch (blocking)

Nothing here is optional. The site should not go live without these.

| # | Item | Findings | Effort |
|---|---|---|---|
| 1 | Fix the legal "Last updated" date | L-01 | 15 min |
| 2 | Create and wire an Open Graph image | I-01 | 1 hr |
| 3 | Configure GA4 + Search Console; add conversion events for form submit, thank-you, WhatsApp, click-to-call, newsletter | Summary 1 | 3 hr |
| 4 | Set `EMAIL_TIMEOUT` and move sending off the request path | R-01 | 1 hr |
| 5 | Fix the focus indicator on both backgrounds | A-01 | 30 min |
| 6 | Raise control-boundary contrast to ≥3:1 | A-02 | 30 min |
| 7 | Define `--brand-hover`; replace the five `--brand`-as-text uses | S-01, C-01 | 20 min |
| 8 | Correct the consent copy to name advertising | L-02 | 20 min |
| 9 | Remove `/case-studies/` and empty categories from the sitemap; `noindex` while empty | S-05, S-06 | 45 min |
| 10 | Give the lawyer the L-03 gap list | L-03 | — |
| 11 | Supply Facebook + Instagram URLs, bio and headshot | A-03 (content) | owner |

### Phase 1 — First two weeks after launch (conversion)

Where the revenue is.

| # | Item | Findings | Effort |
|---|---|---|---|
| 12 | Package comparison table | U-01 | 4 hr |
| 13 | Pricing FAQ with FAQ schema | U-02, E-06 | 3 hr |
| 14 | Resolve or date the struck-through prices | U-03 | owner decision |
| 15 | Acknowledge `?service=` on the contact page | J-2, F-06 | 1 hr |
| 16 | Per-type CTAs on the website mockups | J-3, U-05 | 1 hr |
| 17 | Remove `novalidate`; add inline validation | F-01 | 2 hr |
| 18 | Error summary + focus management on failed submit | F-02 | 2 hr |
| 19 | Preloader: first visit only, or remove | P-01 | 1 hr |
| 20 | Pause/play controls on both carousels | A-04 | 2 hr |
| 21 | Enlarge carousel dot hit areas | A-03 | 30 min |
| 22 | Response-time promise near the submit button | U-10 | owner decision |

### Phase 2 — Weeks 3–6 (search)

The slowest-compounding work, so it should start early.

| # | Item | Findings | Effort |
|---|---|---|---|
| 23 | Render blog bodies as sanitised Markdown | E-02 | 3 hr |
| 24 | Rewrite all 7 service pages to 600–900 words + FAQs | E-01, E-06 | 2 days |
| 25 | Expand location pages to 400–600 words + local FAQs | E-03 | 1 day |
| 26 | Expand the 3 blog posts; add featured images | E-03, E-14 | 1 day |
| 27 | Write meta descriptions for every service and post; trim the 4 long ones | E-04 | 3 hr |
| 28 | Add `OfferCatalog` schema to `/packages/` | E-07 | 2 hr |
| 29 | Add `BreadcrumbList` schema | E-05 | 2 hr |
| 30 | Consolidate the business entity behind one `@id` | E-08 | 1 hr |
| 31 | Add geo coordinates, opening hours, `sameAs`, GBP link | E-10 | 1 hr |
| 32 | Author bio box + `Person` schema | E-13 | 3 hr |
| 33 | Fix heading hierarchy on `/blog/` and `/services/` | A-06 | 30 min |

### Phase 3 — Polish and consistency

| # | Item | Findings | Effort |
|---|---|---|---|
| 34 | Replace the four remaining letter-initial icons | S-03 | 2 hr |
| 35 | Fix home section numbering | S-02 | 10 min |
| 36 | Reconcile desktop / mobile / footer navigation | S-04 | 30 min |
| 37 | Show all 7 services on the home page | S-07 | 10 min |
| 38 | Self-host and subset the fonts | P-02 | 2 hr |
| 39 | CTA band variants | U-05 | 3 hr |
| 40 | CTAs on category and author pages | J-5, U-07 | 1 hr |
| 41 | Guard `matchMedia.addEventListener`; wrap inits in try/catch | S-08 | 30 min |
| 42 | Forced-colors fallback for `.accent` and focus rings | A-08 | 45 min |
| 43 | Focus the cookie banner on appearance | A-09 | 20 min |
| 44 | Associate field hints via `aria-describedby` | A-10 | 30 min |
| 45 | Fix the ARIA tab pattern on the hero carousel | A-05 | 30 min |
| 46 | Image dimensions on blog and author images | I-02 | 20 min |
| 47 | Safe-area insets on floating buttons | A-11 | 10 min |
| 48 | Newsletter honeypot + rate limit + privacy notice | F-03, L-05 | 1 hr |
| 49 | Validate the newsletter redirect | F-04 | 15 min |
| 50 | Fix client-IP derivation; review the rate limit for CGNAT | F-05 | 1 hr |
| 51 | Single source of truth for the canonical base URL | S-09 | 30 min |
| 52 | Sitemap priorities and `lastmod` | E-12 | 30 min |
| 53 | Add CSP and Permissions-Policy | X-01 | 2 hr |
| 54 | Caching for `SiteSettings` and listing fragments | P-05 | 2 hr |
| 55 | Remove unused dependencies (after E-02 confirms Markdown use) | S-10 | 10 min |
| 56 | Cookie Policy: name cookies, providers, durations | L-04 | 1 hr |

### Phase 4 — Growth (after the above is measured)

- Service × location pages for the 6–8 highest-intent combinations — written individually, **never generated** (E-11).
- Real content imagery (I-01).
- Case studies and testimonials as clients approve them — the CMS is ready and correctly refuses to fake them.
- Revisit the service-vs-package pricing architecture (U-04).

---

## What is already right

An audit that only lists problems misrepresents the work. These were checked and are genuinely well done:

- **Progressive enhancement is real, not claimed.** Reveal animations are only armed after JS proves it can disarm them, with a 4-second deadline on top. The carousel degrades to a readable stack. The preloader clears from CSS so a JS failure cannot trap the page. Very few sites get this right.
- **Consent gating is correctly implemented.** No tracker is rendered server-side; IDs are published as JSON config and scripts are injected only after acceptance. Decline is equally prominent, Escape declines rather than dismisses, and withdrawal clears the cookies. The copy needs fixing (L-02); the mechanism does not.
- **The empty-state rule holds everywhere.** Testimonials, case studies and social icons all disappear rather than showing invented proof. That discipline is visible throughout and is worth protecting.
- **The text colour palette is measurably sound** — every text pair tested passes AA, most comfortably.
- **Reduced motion is handled properly**, including in JavaScript, not just CSS.
- **The security baseline is right** — HSTS, secure cookies, SSL redirect, environment secrets, honeypot, rate limiting, and the SQLite-outside-the-web-root requirement enforced by configuration.
- **63 tests pass**, and they cover real behaviour including email failure and image-processing failure.
- **The written content is good.** The location pages are genuinely differentiated per county rather than templated — which is the difference between local landing pages and doorway pages. The problem is depth, not quality.

The foundations are sound. Most of this list is about making the site *earn* from those foundations — and about being able to see whether it does.

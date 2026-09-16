# VEE Agency Website — Master Product & Build Specification

**Project:** `veeagency.co.ke`  
**Brand:** VEE Agency  
**Primary purpose:** Convert qualified visitors into enquiries while establishing VEE Agency as a credible digital growth partner for Kenyan businesses.

> This document is the highest-level source of truth for the build. When another note, mockup, or AI-generated suggestion conflicts with this document, use the latest confirmed client decisions recorded here.

---

## 1. Confirmed Business Information

| Item | Final value |
|---|---|
| Brand | VEE Agency |
| Website | `https://veeagency.co.ke/` |
| Base location | Syokimau, Machakos County, Kenya |
| Primary service areas | Nairobi, Machakos, Kajiado, Kiambu |
| Coverage | All counties in Kenya; the four named counties receive stronger local-search emphasis |
| Primary phone/WhatsApp | 0759 643 882 |
| WhatsApp international | +254 759 643 882 |
| Public email | hello@veeagency.co.ke |
| Social platforms | Facebook, Instagram |
| Hosting | HostAfrica |
| Blog | Fully live at launch |
| Testimonials/case studies | CMS-ready and added later through Django Admin |

### Positioning

VEE Agency helps businesses **get found, build trust and grow online** through connected digital services rather than isolated marketing activities.

Core service areas:

- Website design & development
- Website audit & revamp
- Website management
- Google Business Profile optimization
- SEO
- SEO + AEO
- Social media management
- Digital advertising
- Competitor analysis
- Digital growth strategy

---

## 2. Business Goals

The website must support these outcomes, in this order:

1. **Generate qualified enquiries.**
2. **Make VEE Agency immediately understandable.** A visitor should understand what VEE does within seconds.
3. **Show the relationship between services.** Website, Google visibility, SEO/AEO, social media and advertising should feel like one system.
4. **Build trust without inventing proof.** No fake testimonials, fake client logos, fake results or fake statistics.
5. **Support local discovery.** Strong relevance for Nairobi, Machakos, Kajiado and Kiambu while preserving nationwide Kenya positioning.
6. **Create an expandable content platform.** Blog, locations, services, packages, testimonials and case studies must be manageable through Admin.

---

## 3. Primary User Journeys

### Journey A — Service buyer

`Home → Service → Package/CTA → Contact → Thank You → WhatsApp option`

### Journey B — Package buyer

`Home → Packages → Choose Plan → Contact form prefilled with selected package → Thank You`

### Journey C — Search visitor

`Google/AI Search → Service or Location page → Relevant internal links → Contact/WhatsApp`

### Journey D — Content visitor

`Blog → Article → Quick Answer → Related service → Related article → CTA`

### Journey E — High-intent direct visitor

`Landing page → Contact/WhatsApp`

Every important page must provide at least one obvious next step.

---

## 4. Information Architecture

### Main navigation

- Home
- Services
- Packages
- Web Development
- About
- Blog
- Contact

### Utility CTA

- **Chat on WhatsApp** — `https://wa.me/254759643882`
- **Book Free Audit** — points to the contact flow.

### Main URL architecture

```text
/
/about/
/services/
/services/<service-slug>/
/packages/
/web-development/
/blog/
/blog/<slug>/
/blog/category/<slug>/
/blog/author/<username>/
/locations/
/locations/<slug>/
/contact/
/contact/thank-you/
/legal/privacy/
/legal/terms/
/legal/cookies/
/legal/disclaimer/
/sitemap.xml
/robots.txt
/admin/
```

Use lowercase, hyphenated slugs. Never place database IDs in public URLs.

---

## 5. Home Page Story

The home page is not a service catalogue. It should tell a clear story.

### Section 1 — Hero

Suggested direction:

**Eyebrow:** DIGITAL GROWTH AGENCY

**Headline:**

> Get found. Build trust. Grow online.

**Supporting message:**

> VEE Agency helps Kenyan businesses build stronger websites, search visibility, Google presence, social media and digital campaigns — all working together around your business goals.

**Primary CTA:** Book Your Free Audit

**Secondary CTA:** Chat on WhatsApp

The final copy can evolve during content refinement, but the proposition must remain clear and business-focused.

### Section 2 — Problem / opportunity

Show the gap between **being online** and having a digital presence that actually helps a business.

### Section 3 — Services

Feature the key VEE services with short, benefit-led descriptions. Avoid long sales paragraphs.

### Section 4 — The VEE Digital Growth System

Visualise the connected system:

1. Get Found
2. Look Professional
3. Stay Visible
4. Reach More People
5. Turn Interest Into Action

### Section 5 — Packages

Show Essential, Standard and Premium clearly. Use the confirmed prices from the package source of truth below.

### Section 6 — Website development banner

Promote custom website creation as a standalone capability.

### Section 7 — Proof / trust

CMS-ready testimonials and case studies. At launch, if there are no approved records, the section must not fabricate content. Either hide empty proof sections or replace them with a truthful trust section.

### Section 8 — Blog / insights

Show recent published posts.

### Section 9 — Final CTA

Strong, simple CTA leading to contact and WhatsApp.

---

## 6. Package Source of Truth

### Essential Growth Package

**Current:** KES 15,000/month  
**Original/reference price:** KES 18,000/month

Includes:

- Google Business Profile audit & optimization
- Social media profile optimization
- 3 posts/week on TikTok, Facebook & Instagram
- Content creation

### Standard Growth Package

**Current:** KES 25,000/month  
**Original/reference price:** KES 30,000/month

Includes:

- Google Business Profile audit & optimization
- Social media profile optimization
- 3 posts/week on TikTok, Facebook & Instagram
- Basic website audit
- SEO optimization
- Ads management — 1 platform
- Competitor analysis
- Linktree creation & optimization

### Premium Growth Package

**Current:** KES 45,000/month  
**Original/reference price:** KES 55,000/month

Includes:

- Google Business Profile audit & optimization
- Social media profile optimization
- 5 posts/week across TikTok, Facebook, Instagram, X & LinkedIn
- Full website audit & revamp plan
- Expert ads campaign management across platforms
- Full competitor analysis + remediation plan
- Full SEO & AEO optimization

**Important:** Advertising media spend is billed separately from VEE Agency's management fee.

### Presentation rule

The website is a sales website, not a rate-card poster. Show enough information to understand the difference between plans, then provide a clear path to enquire. Detailed scope can live behind an accordion/modal or on the package page.

---

## 7. Standalone Website Services

### Website Creation

**From KES 30,000**

Custom website design and development, mobile-friendly, SEO/AEO-ready, with clear enquiry or booking paths.

### Website Audit & Full Revamp

**From KES 15,000 for existing VEE clients**  
**From KES 25,000 for new clients**

Audit, structure review, content and UX improvements, stronger calls-to-action and clearer enquiry paths.

### Website Management

**From KES 5,000/month**

Regular content updates, maintenance, monitoring, broken-link and performance checks.

### Full SEO Optimization

**From KES 10,000**

On-site SEO including keyword, page structure and technical improvements.

### Full SEO & AEO Optimization

**From KES 15,000**

SEO plus AEO-oriented structuring for AI-driven search and answer experiences.

### Competitor Analysis

**From KES 5,000**

Comparison against five competitors as the base scope, with findings across website, Google presence and social media.

### Digital Ads Management

**KES 5,000/platform/campaign**

Campaign management on supported ad platforms; advertising spend billed separately.

---

## 8. Content Rules

### Do

- Write for business owners and decision-makers.
- Lead with business outcomes and useful clarity.
- Keep language natural and specific.
- Use examples, checklists, comparisons and practical advice.
- Make service descriptions distinct from one another.
- Write Kenyan location content naturally rather than repeating county names unnaturally.

### Do not

- Claim guaranteed rankings, guaranteed leads or guaranteed sales.
- Invent clients, testimonials, case-study metrics or awards.
- State that a business is “losing customers” unless there is evidence.
- Stuff pages with location names.
- Use generic AI filler such as “in today's fast-paced digital world” repeatedly.
- Treat social likes as the main business outcome.

---

## 9. CMS / Admin Principle

The site should be designed so VEE can manage content without code changes.

Admin-manageable content should include:

- Services
- Packages
- Blog categories
- Blog posts
- Blog authors
- Location pages
- Testimonials
- Case studies
- Site settings
- Contact submissions
- Newsletter subscribers

Every CMS-managed content type needs predictable ordering, active/published status, search/filtering, and useful field help text.

---

## 10. Empty-State Rule

A content section must never display broken cards, placeholder lorem ipsum, empty image boxes or fake sample records on the production site.

Examples:

- No testimonials → hide the carousel or show a truthful alternative.
- No case studies → hide that section.
- No blog posts → show a clean “Insights coming soon” state or remove the module.
- Missing social URL → do not render an empty icon.

---

## 11. Conversion Rules

At least one primary CTA must appear in the hero. Important pages should also include a CTA near the end.

WhatsApp should always be one click away on mobile and desktop without obscuring content or colliding with other floating controls.

Contact form must preserve entered values when validation fails.

Package “Choose Plan” buttons should prefill the contact form with the selected package.

---

## 12. Quality Bar

A release is not complete until:

- No broken links
- No placeholder text
- No missing alt text on meaningful images
- No console errors caused by the site
- No horizontal overflow on mobile
- Forms work end-to-end
- Admin content renders correctly
- SEO metadata exists and is unique where required
- Sitemap and robots work
- Analytics events are verifiable
- WhatsApp links work
- Error pages are usable
- Backup/restore procedure is tested
- Production configuration is separated from development configuration

---

## 13. Source Notes

The original DeepSeek material proposed a Django architecture, component system, service/package/blog/location CMS, contact workflow, SEO/AEO layer, GSAP/ScrollTrigger/Lenis motion, analytics, reCAPTCHA, SMTP, backups and uptime monitoring. Those ideas are retained where useful, but confirmed VEE business details in this document override earlier contradictory values such as a Nairobi-only location label and extra social platforms. fileciteturn4file5L107-L112

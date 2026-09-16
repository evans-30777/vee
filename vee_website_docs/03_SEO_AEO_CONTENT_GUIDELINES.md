# VEE Agency Website — SEO, AEO, Local Search & Content Guidelines

## 1. SEO Objective

The website should be discoverable for people searching for digital services in Kenya while establishing strong topical relevance around:

- website development
- SEO
- AEO
- Google Business Profile
- social media management
- digital advertising
- digital growth strategy
- website management

SEO must support the commercial goal: **qualified visibility → useful page → enquiry**.

---

## 2. Primary Geography

VEE Agency is based in **Syokimau, Machakos County** and serves businesses throughout Kenya.

Local SEO emphasis should be strongest for:

1. Nairobi
2. Machakos
3. Kajiado
4. Kiambu

Do not describe VEE as a Nairobi-only agency.

Do not imply VEE only serves the four counties.

The positioning should consistently be:

> Based in Syokimau, Machakos County, serving businesses across Kenya, with a strong focus on Nairobi, Machakos, Kajiado and Kiambu.

---

## 3. Metadata

Every indexable page should have:

- unique `<title>`
- unique meta description
- canonical URL
- robots directive where appropriate
- Open Graph title/description/image
- social sharing image where appropriate

Do not use the same generic description on every page.

The original specification explicitly included title, description, canonical, robots, Open Graph and social-card metadata. fileciteturn4file9L6005-L6242

---

## 4. Recommended Page-Level Intent

### Home

Intent: broad digital growth / agency / Kenya.

### Services

Intent: discover VEE's full range of services.

### Service detail pages

Intent: one clearly defined service per page.

### Packages

Intent: evaluate ongoing digital growth support and commercial fit.

### Web Development

Intent: dedicated website creation service page.

### Blog

Intent: educational search demand and authority.

### Location pages

Intent: local discovery with genuinely useful local context.

---

## 5. AEO / Answer-Engine Structure

Every strong information page should make the main answer easy to extract.

For blog posts, use:

### H1

Specific topic.

### Quick Answer

1–3 sentences answering the question immediately.

### H2 sections

Prefer question or problem-based headings where natural.

### Lists

Use lists for steps, comparisons, requirements and checklists.

### Tables

Use tables where a comparison is actually useful.

### FAQs

Use real questions customers ask. Do not create FAQs purely to insert keywords.

The source specifically proposed a `quick_answer` block, question-based H2s, lists/tables and FAQ schema. fileciteturn4file9L7092-L7094

---

## 6. Structured Data

Use schema where it accurately describes the page.

Potential schemas:

- Organization
- WebSite where useful
- Service
- BlogPosting
- BreadcrumbList
- FAQPage only when the visible page contains qualifying FAQ content
- LocalBusiness only where the page genuinely represents a local-business context

Never mark up content that is not visible to users.

### Organization baseline

- name: VEE Agency
- URL: `https://veeagency.co.ke/`
- email: `hello@veeagency.co.ke`
- telephone: `+254759643882`
- address locality: Syokimau
- address region: Machakos County
- country: KE
- area served: Nairobi, Machakos, Kajiado, Kiambu, Kenya
- sameAs: official Facebook and Instagram URLs only when confirmed

The original schema draft used the same core address and area-served pattern but included social platforms that have since been narrowed by the confirmed business setup. fileciteturn4file7L147-L153

---

## 7. Internal Linking

Every page should have a logical next step.

### Blog posts

Link to:

- at least one relevant VEE service
- at least one related article when available

### Service pages

Link to:

- relevant package(s)
- contact page
- related service(s)

### Location pages

Link naturally to:

- relevant services
- relevant articles
- contact

Do not create forced “SEO links” simply to satisfy a checklist.

The original internal-linking rules followed this structure. fileciteturn4file9L7151-L7156

---

## 8. Location Page Standards

Each county page must be genuinely useful.

Include:

- what VEE offers there
- who VEE serves
- relevant local business context
- key services
- how engagement works
- clear CTA
- internal links

Avoid:

> “VEE Agency is the best digital agency in Nairobi… VEE Agency is the best digital agency in Nairobi…”

Instead, create different copy and useful local relevance for each page.

The goal is not four versions of one keyword-stuffed page.

---

## 9. Blog Strategy

Blog categories from the earlier specification can be retained:

- SEO & AEO
- Ads & Performance
- Social Media
- Web Development
- Case Studies

The blog should be used to answer real business questions.

Examples of useful editorial themes:

- how local businesses improve Google Maps visibility
- what a business website should include before spending on ads
- SEO vs paid ads for Kenyan businesses
- when a website needs a revamp rather than a rebuild
- how to structure a Google Business Profile
- practical digital marketing budgets and trade-offs
- website conversion mistakes
- AI search / answer-engine visibility explained for business owners

Do not publish thin “AI-generated SEO articles” for the sake of filling the blog.

---

## 10. Case Studies

Case studies must follow:

**Challenge → Work done → Result → Evidence**

Good case-study metrics:

- traffic change
- enquiry change
- ranking change
- conversion change
- engagement change
- delivery/time improvements

Only report numbers VEE can document.

If no verified case studies exist at launch, do not create fictional examples.

---

## 11. Testimonials

Each testimonial must have:

- real client name
- business name when permitted
- exact approved quote
- approved logo/headshot if used

Do not paraphrase a testimonial into a stronger claim without approval.

---

## 12. Search Snippet Writing

Titles:

- specific
- readable
- commercially relevant
- naturally keyword-informed

Descriptions:

- explain the page
- show the benefit
- avoid keyword stuffing
- avoid fake claims

Do not repeat “best”, “leading”, “number one” without objective basis.

---

## 13. Image SEO

Every meaningful image should have:

- accurate alt text
- sensible filename
- optimized format
- dimensions

Alt text should describe the image or its function rather than insert keywords.

Decorative graphics should be empty-alt or handled appropriately.

---

## 14. Sitemap / Robots

Use Django's built-in sitemap framework.

Include:

- public static pages
- active service pages
- published blog posts
- active location pages

Do not include:

- admin
- unpublished drafts
- thank-you pages if intentionally noindex
- private/admin-only routes

The original sitemap architecture followed these same content classes. fileciteturn4file9L6751-L7092

---

## 15. Search Console / Analytics

Before launch:

- verify domain in Google Search Console
- submit sitemap
- verify indexability
- verify canonical URLs
- verify important rich-result eligibility

Use GA4 and Meta Pixel only after the site's consent implementation is ready.

Recommended events:

| Event | Trigger |
|---|---|
| `whatsapp_click` | WhatsApp CTA click |
| `cta_click` | important CTA clicks |
| `form_submit` | successful contact form submission |
| `generate_lead` | successful conversion / thank-you page |
| `scroll_depth` | 25 / 50 / 75 / 100% |

The original feature implementation listed these events. fileciteturn4file9L8785-L8953

---

## 16. Cookie / Consent Rules

Do not load marketing/analytics tracking blindly if the chosen consent policy requires prior consent.

The implementation should support:

- not yet chosen
- accepted
- rejected

The original specification proposed storing the choice locally and using Google Consent Mode. fileciteturn4file9L9206-L9222

---

## 17. Email / Deliverability

Public email:

`hello@veeagency.co.ke`

The source specification proposed Google Workspace SMTP with TLS on port 587 and recommended SPF, DKIM and DMARC setup. fileciteturn4file9L9222-L9283

The final implementation must test:

- admin notification email
- customer auto-reply
- SPF
- DKIM
- DMARC
- spam placement

Do not claim a deliverability score until it has actually been tested.

---

## 18. SEO Acceptance Checklist

Before release:

- all key pages indexable
- unique metadata
- canonical URLs correct
- no accidental `noindex`
- no orphaned important pages
- sitemap valid
- robots valid
- meaningful internal linking
- structured data passes validation where applicable
- mobile layout usable
- images optimized
- blog posts have author/date information where intended
- location pages are unique and useful
- contact CTAs work

---

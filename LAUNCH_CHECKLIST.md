# Launch Checklist — What Evans Needs to Provide

Everything below is owner-supplied. The code side is done; these are the inputs
it needs. Ordered by what blocks launch.

Nothing here is invented on your behalf: testimonials, case studies, statistics
and team members are never fabricated, so any section without real content stays
hidden rather than showing filler.

---

## 1. Credentials — blocking

- [ ] **SMTP details for `hello@veeagency.co.ke`** — host, port, username, password
      (HostAfrica provides these with the mailbox). Without them enquiries are still
      saved to the database, but no notification email reaches you.
- [ ] **Hosting access** — cPanel or SSH login for the HostAfrica account.
- [ ] **Domain control** — ability to point DNS and install the SSL certificate.

## 2. Site settings — one record in `/admin/`

Defaults already carry your confirmed details. **Verify** these rather than retype:

- [ ] Tagline — currently *"Let's grow your brand online together."*
- [ ] Calls number — `0717115737`
- [ ] WhatsApp number — `254759643882`
- [ ] Email — `hello@veeagency.co.ke`
- [ ] Location label — `Syokimau, Machakos County, Kenya`
- [ ] Service counties — Nairobi, Machakos, Kajiado, Kiambu

Still blank, and needed:

- [ ] **Facebook URL** — the field exists; the icon stays hidden until it's filled
- [ ] **Instagram URL** — same
- [ ] **Default social image** — what shows when someone shares a link on WhatsApp
      or Facebook. Supply at **1200 × 630**.

Optional, whenever you're ready:

- [ ] Google Search Console verification token
- [ ] GA4 measurement ID (`G-XXXXXXXXXX`) — paste it in and the cookie banner
      switches itself on automatically
- [ ] Meta Pixel ID

## 3. Packages — blocking

The prices are locked and already correct. What's missing is **what each package
actually includes**.

- [ ] **Essential Growth — KES 15,000/month** → feature list
- [ ] **Standard Growth — KES 25,000/month** → feature list
- [ ] **Premium Growth — KES 45,000/month** → feature list
- [ ] **Website Development — from KES 30,000** → feature list

Copy these from your real rate card. **The ones in the local development database
are placeholders I wrote to check the layout — they are not your offering and must
be replaced.**

For each, optionally: a one-line description, an "ideal for" line, and which one
to mark as most popular.

> ⚠️ **Keep the slugs exactly** `essential`, `standard`, `premium`, `website`.
> The "Choose Plan" buttons pass the slug to the contact form to pre-select what
> the visitor was looking at. A different slug silently breaks that pre-fill.

## 4. Services — blocking

For each service you want listed:

- [ ] Name
- [ ] Short description (one or two sentences — used on cards)
- [ ] Full description (optional, for the service's own page)
- [ ] What's included — a list of deliverables (optional)
- [ ] Starting price (optional; omit and the card reads "Learn more")

Expected from the rate cards: Website Design & Development, SEO & AEO, Google
Business Profile, Social Media Management, Digital Ad Campaigns, Website Audits
& Revamps. **Confirm this list is right** — it was inferred, not given.

## 5. Location pages — blocking for local SEO

One per county: **Nairobi, Machakos, Kajiado, Kiambu**. For each:

- [ ] Hero headline (e.g. *"Digital Growth Agency in Nairobi"*)
- [ ] Intro — 2–3 sentences
- [ ] Body — a few paragraphs (optional but valuable; this is what ranks locally)

Write these in your own words. Genuinely local, specific detail is what makes
these pages rank, and near-identical pages across counties can be treated as
duplicate content.

## 6. Blog — at least one post at launch

The spec has the blog fully live at launch, with weekly posts after.

Per post:

- [ ] Title
- [ ] Excerpt (one or two sentences — used on cards)
- [ ] Body
- [ ] **Quick Answer** (optional but recommended — a direct 1–2 sentence answer;
      this is what gets pulled into featured snippets and AI answers)
- [ ] FAQs (optional — each becomes FAQ schema)
- [ ] Featured image + its alt text (optional)
- [ ] Category

- [ ] **2–3 post topics to start with**

## 7. About you — the author byline

- [ ] First and last name (blog posts are attributed to this)
- [ ] Job title
- [ ] Short bio
- [ ] Headshot — at least **800 × 800**

## 8. Images — sizes

Uploads are downscaled automatically, so don't shrink anything by hand. They are
never *enlarged*, so supply at least:

| Image | Minimum |
|---|---|
| Social sharing image | 1200 × 630 |
| Blog featured image | 1200 wide |
| Author headshot | 800 × 800 |
| Client logo | 400 wide, transparent PNG |

## 9. Proof — whenever it's real

Not needed for launch. These sections stay hidden until there's something real.

- [ ] **Testimonials** — client name, their business, and the quote. Get permission first.
- [ ] **Case studies** — client label, industry, the challenge, what you did, the
      result. Only include metrics you can actually evidence.

---

## Not needed from you

Already handled: all page copy and structure, legal pages, SEO/schema markup,
the website-type example layouts, the cookie banner, and the whole design.

**Two things worth a second look before launch:**

- **The legal pages are a first draft.** Privacy, Terms, Cookies and Disclaimer are
  written and reference Kenya's Data Protection Act 2019, but they have not been
  reviewed by a lawyer. Worth doing before any serious ad spend.
- **All marketing copy is mine, not yours.** It's written to convert and is
  factually grounded, but read it in your own voice and change anything that
  doesn't sound like you. You're the one who has to live up to it on a call.

## Deferred by agreement — don't worry about these yet

Templates marketplace, payments (M-Pesa → Stripe → PayPal), and the light-mode
theme toggle are Phase 2. Tawk.to live chat and reCAPTCHA were decided against;
see `CLAUDE.md`.

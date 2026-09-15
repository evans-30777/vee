You are an expert Django developer and frontend designer. Build a premium, dark-mode, motion-driven website for VEE Agency using Django (Python), HTML, CSS, and vanilla JavaScript (with GSAP and Lenis via CDN). The site must be fully responsive, accessible (WCAG 2.1 AA), and optimized for mobile-first performance.

## Brand & Design System
- **Name:** VEE Agency
- **Tagline:** "Let's grow your brand online together."
- **Tone:** Authoritative & Bold, with data-driven service descriptions.
- **Colors:**
  - Base: #0A0A0A (charcoal)
  - Primary Accent: #FF4500 (ember orange)
  - Secondary Accent: #8B0000 (deep red)
  - Text: #FFFFFF (white), #A1A1A1 (light grey)
  - WhatsApp CTA: #25D366 (green)
- **Typography:** Space Grotesk (headings), Inter (body). No script fonts.
- **Motion:** Use Lenis for smooth scroll. GSAP ScrollTrigger for text reveals, staggered cards, parallax. Disable heavy animations on mobile. Respect `prefers-reduced-motion`.
- **Preloader:** Minimal, glowing V logo + progress bar, fades out.
- **Page Transitions:** GSAP fade/slide between pages.
- **Custom 404/500:** Branded with CTA back to Home.
- **Back-to-top:** Floating orange arrow, appears after scroll. Ensure it doesn't collide with WhatsApp/Tawk.to buttons.

## Site Architecture (Django Apps)
- `core`: Home, About, Contact, Thank You, Legal pages, 404/500.
- `services`: Service list, detail pages (SEO, Ads, Social, Competitor Analysis, Website Audit).
- `packages`: Pricing packages (Essential, Standard, Premium) + Web Development service.
- `blog`: Posts, categories, author page.
- `locations`: County pages (Nairobi, Machakos, Kajiado, Kiambu, Kenya).
- `accounts`: Custom user model for author (you).

## Pages & Features

### 1. Home
- **Hero:** Full-screen abstract tech video (dark server lights/data streams) with dark overlay. Headline: "Digital Dominance for Kenyan Brands". Two CTAs: "Grow My Brand" (scroll to packages) and "Build My Website" (scroll to web dev). On mobile, replace video with static image.
- **Services Grid:** 3x2 interactive icon grid. On hover, card lifts/glows. On click, expands to modal with deliverables (SEO, Ads, Social, Competitor Analysis, Website Audit).
- **Packages:** Three GSAP tilt cards (Essential KES 15k, Standard KES 25k, Premium KES 45k). Premium highlighted. Hover tilt disabled on mobile.
- **Web Dev Section:** Full-width interstitial banner with glowing MacBook mockup, KES 30,000, CTA "Get Your Website". Link to dedicated Web Dev page.
- **Testimonials Carousel:** Auto-playing, slick quotes with client names/logos (data from DB).
- **CTA Footer:** "Ready to dominate?" + WhatsApp button + minimal footer links.

### 2. Services
- Grid of all services. Each links to a detail page with deliverables and a CTA.

### 3. Packages
- Detailed comparison table. All three tiers + Web Dev one-time.
- CTA for each: "Choose Plan" → contact form pre-filled.

### 4. Web Development
- Dedicated page: mockups, process, pricing (KES 30,000), features (custom design, SEO/AEO ready, responsive, e-commerce), CTA.

### 5. About
- Growth Story narrative. Team (optional). Author bio + headshot. CTA.

### 6. Blog
- Category filters (SEO & AEO, Ads, Social, Web Dev, Case Studies).
- Post template with "Quick Answer" box, structured H2/H3, FAQ schema, CTA.
- Author page: bio, headshot, all posts.
- Weekly posts. You write them.

### 7. Locations
- Dynamic pages for Nairobi, Machakos, Kajiado, Kiambu, Kenya.
- Each page: localized content, specific services, CTA. Note: "We also serve clients across Kenya remotely."

### 8. Contact
- WhatsApp button (green, large).
- "Book a Free Audit" form: Name, Email, Phone, Service Interest (dropdown), Budget Range (dropdown), Message. Save to DB, email hello@veeagency.co.ke, auto-reply to user. Redirect to Thank You page.
- Phone: 0759643882 (click-to-call).
- Email: hello@veeagency.co.ke
- Location: "Nairobi, Kenya" (no map).
- Social links: Facebook, TikTok, Instagram, LinkedIn, X.
- Tawk.to live chat widget.

### 9. Legal Pages
- Privacy Policy, Terms of Service, Cookie Policy, Disclaimer.
- "Do Not Sell My Personal Information" link.
- Cookie consent banner linking to policies.

## Technical Requirements
- **Django 4+**, PostgreSQL database.
- **Static files:** Serve via Whitenoise.
- **Media:** Local storage for now (blog images, author headshot).
- **Forms:** Django forms with reCAPTCHA v3 (invisible).
- **SEO:** Semantic HTML5, schema markup (Organization, Service, FAQ, BlogPosting, LocalBusiness), XML sitemap, robots.txt, meta tags (OG, Twitter Cards), clean URLs.
- **Analytics:** GA4, Google Search Console, Meta Pixel (client-side only for now; server-side phase 2).
- **Performance:** Lazy-load images, compress video, use CDN for GSAP/Lenis. Aim for 90+ PageSpeed.
- **Accessibility:** WCAG 2.1 AA, keyboard navigation, focus states (orange glow), alt text (AI-generated, reviewed), font size adjuster, `prefers-reduced-motion` fallbacks.
- **Backups:** Daily DB, weekly full-site. Uptime monitoring (UptimeRobot). Staging environment (staging.veeagency.co.ke). Maintenance mode page.
- **Hosting:** HostAfrica shared hosting. Ensure Python 3.10+, WSGI, SSH, PostgreSQL, cron jobs.

## Content & Data
- **Packages:** Essential KES 15,000 (GBP Audit, 3x/week posts, profile optimization, content creation). Standard KES 25,000 (everything in Essential + website audit, SEO, ads management 1 platform, competitor analysis, Linktree). Premium KES 45,000 (everything in Standard + 5 posts/week + X & LinkedIn, full SEO & AEO, expert ads all platforms, full competitor analysis + remediation, full website audit & revamp plan).
- **Web Dev:** KES 30,000 (custom design, SEO/AEO/GEO ready, clear paths for enquiries/bookings, responsive & mobile design).
- **Author:** Your name, bio, headshot (provided during build).
- **Testimonials:** Placeholder data; you will fill in.
- **Blog:** Start with 2 seed posts. You will write weekly.
- **Location content:** You will provide localized text; template ready.

## Deliverables
- Complete Django project with apps, templates, static files, and DB models.
- Admin panel configured for easy content management (blog, testimonials, packages, locations).
- README with setup instructions for HostAfrica.
- All code commented and organized.

Build this step by step. Start with project setup, then core models, then templates, then frontend styling, then GSAP/Lenis integration, then forms, then SEO, then testing.



##Color  
:root {
  --color-bg: #0A0A0A;
  --color-surface: #111111;
  --color-primary: #FF4500;
  --color-secondary: #8B0000;
  --color-text: #FFFFFF;
  --color-text-muted: #A1A1A1;
  --color-whatsapp: #25D366;
  --font-heading: 'Space Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --radius: 12px;
  --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

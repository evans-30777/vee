# VEE Agency Website — Django Technical Implementation Guide

## 1. Architecture

Build the website as a conventional Django server-rendered application with PostgreSQL in production.

Recommended application boundaries:

```text
veeagency/
├── manage.py
├── veeagency/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── core/
│   ├── services/
│   ├── packages/
│   ├── blog/
│   ├── locations/
│   ├── accounts/
│   └── contact/
├── templates/
├── static/
├── media/
├── docs/
├── requirements.txt
├── .env.example
└── README.md
```

The original specification uses these same application boundaries: core, services, packages, blog, locations, accounts and contact. fileciteturn4file5L107-L112

---

## 2. Settings

Use a split settings structure:

### base.py

Shared:

- installed apps
- middleware
- templates
- static/media
- internationalization
- logging defaults
- shared security configuration

### dev.py

- local development configuration
- local database where appropriate
- console email backend
- debug tooling

### prod.py

- `DEBUG=False`
- PostgreSQL via environment variable
- secure cookies
- HTTPS-related security settings
- allowed hosts
- static-file handling
- structured logging

Do not commit secrets. Never put passwords, API keys, reCAPTCHA secrets, SMTP app passwords or analytics identifiers directly into source files.

The original specification proposed environment variables for Django, PostgreSQL, Google Workspace SMTP, reCAPTCHA, GA4, Meta Pixel and Backblaze B2. fileciteturn4file0L9-L10

---

## 3. Dependencies

Use a supported Django release appropriate for the deployment environment and lock the exact versions in `requirements.txt` after installation/testing.

The original conversation used Django, PostgreSQL driver, WhiteNoise, Pillow, django-recaptcha, taggit, Gunicorn, slugify, Markdown and Bleach. Those are implementation candidates, not immutable version requirements.

Prefer standard Django features where possible. For example, use Django's built-in sitemap framework rather than adding a third-party sitemap dependency. fileciteturn4file9L177-L179

---

## 4. Core Models

### 4.1 Abstract timestamp model

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### 4.2 accounts.User

Custom user model for blog authors and future editorial needs.

Suggested fields:

- `bio`
- `headshot`
- `facebook`
- `instagram`
- `linkedin`
- `website`

Only expose social profile fields that VEE actually intends to use publicly.

### 4.3 services.Service

Fields:

- `name`
- `slug`
- `icon`
- `tagline`
- `short_description`
- `full_description`
- `deliverables` JSON list
- `order`
- `is_active`

The original model uses these fields and ordered active services. fileciteturn5file0L147-L153

### 4.4 packages.Package

Use a model capable of representing:

- monthly retainers
- one-time services
- display price
- previous/reference price
- short description
- feature list
- “ideal for” copy
- ordering
- active status

Do not hard-code package prices in templates if they are expected to be editable through Admin.

### 4.5 Blog

At minimum:

**Category**

- name
- slug
- description
- active flag where useful

**BlogPost**

- title
- slug
- excerpt
- body
- featured image
- author
- category(s)
- published_at
- is_published
- quick_answer
- FAQ JSON
- SEO title
- SEO description
- updated timestamp

The original direction explicitly called for a `quick_answer` field, FAQ data and an author relationship. fileciteturn4file9L7092-L7094

### 4.6 locations.LocationPage

Fields:

- county
- slug
- hero_headline
- intro
- body/content
- featured_services
- meta_title
- meta_description
- order
- is_active

Seed pages for:

- Nairobi
- Machakos
- Kajiado
- Kiambu
- Kenya / nationwide page if used in the architecture

The service area is nationwide even though four counties receive stronger local emphasis.

### 4.7 Testimonials

Fields:

- client_name
- business
- quote
- logo
- is_featured
- order
- is_active

Never seed fake testimonials.

### 4.8 CaseStudy

Fields:

- client_label
- slug
- industry
- challenge
- solution
- result
- metrics JSON
- featured image
- order
- is_active

Only publish metrics that VEE can verify.

### 4.9 SiteSettings

Singleton fields should include:

- phone = `0759643882`
- whatsapp_number = `254759643882`
- email = `hello@veeagency.co.ke`
- location_label = `Syokimau, Machakos County, Kenya`
- service_counties = `["Nairobi", "Machakos", "Kajiado", "Kiambu", "Kenya"]`
- facebook_url
- instagram_url
- site tagline
- default social image

Do not include TikTok, LinkedIn or X unless those accounts are later confirmed as official VEE Agency channels. Earlier source material included additional platforms, but the current confirmed social scope is Facebook and Instagram. 

### 4.10 ContactSubmission

Fields:

- name
- email
- phone
- service
- budget
- message
- ip_address
- user_agent
- is_processed
- timestamps

Useful service choices:

- Essential Growth
- Standard Growth
- Premium Growth
- Website Development
- Something else

Useful budget ranges:

- Under KES 15,000
- KES 15,000–25,000
- KES 25,000–45,000
- KES 45,000+
- Not sure yet

---

## 5. Views and URL Contracts

Use named URL namespaces:

```text
core:
services:
packages:
blog:
locations:
contact:
```

### Core pages

- Home
- About
- Legal pages
- custom 404/500

### Service views

Use a list view and a detail view. Only active services should be publicly exposed.

### Package views

Show active packages in display order. “Choose Plan” sends the selected package slug to contact, for example:

```text
/contact/?service=standard
```

The contact view must validate that incoming service values are legitimate choices rather than blindly storing arbitrary query-string values.

### Blog

- list
- category list/filter
- post detail
- author detail
- pagination
- RSS feed

The original design called for nine blog posts per page. Preserve that unless testing indicates a better UX. 

### Location pages

Each active location page should have its own canonical URL and metadata.

---

## 6. Template Architecture

Base template:

```text
base.html
├── partials/head.html
├── partials/preloader.html
├── partials/header.html
├── main block
├── partials/footer.html
├── partials/floating_buttons.html
├── partials/cookie_banner.html
└── partials/scripts.html
```

Reusable partials:

- service card
- package card
- post card
- location card
- testimonial item
- CTA block
- breadcrumbs
- pagination
- social links

Do not duplicate repeated HTML across templates when a partial makes the responsibility clearer.

---

## 7. Context Contract

Every public view should provide predictable metadata:

```python
meta = {
    "title": "...",
    "description": "...",
}
canonical_url = "https://veeagency.co.ke/..."
page_class = "..."
```

The original specification explicitly established this page-level context contract. fileciteturn5file0L4666-L4681

---

## 8. Contact Form Implementation

Requirements:

- server-side validation is authoritative
- client-side validation improves UX but never replaces server validation
- valid submissions save to database
- admin email is sent to `hello@veeagency.co.ke`
- customer receives confirmation email where SMTP is configured
- successful submission redirects to `/contact/thank-you/`
- failure preserves form values
- include honeypot
- add rate limiting
- validate reCAPTCHA server-side

The original implementation specified three submissions per IP per hour and a honeypot field. fileciteturn5file1L5354-L5383

### Important resilience rule

Do not make the website appear broken just because email delivery temporarily fails. The database submission should be treated as the primary record of the enquiry. Email delivery should be logged and monitored separately.

---

## 9. WhatsApp

Generate the WhatsApp URL centrally from SiteSettings or a dedicated helper/context processor.

Canonical number:

```text
254759643882
```

Example:

```text
https://wa.me/254759643882?text=<encoded-message>
```

Buttons should open in a new tab/window with `rel="noopener"`.

Track WhatsApp clicks in analytics, including the CTA's placement where practical.

---

## 10. Newsletter

Django-only implementation is sufficient.

Model:

- email
- is_active
- source
- timestamps

UX:

- inline success message
- no full page redirect
- duplicate subscriptions handled gracefully
- admin CSV export

---

## 11. Admin Standards

Every admin-managed model should have:

- useful `list_display`
- `search_fields`
- relevant `list_filter`
- ordering
- slug prepopulation where applicable
- sensible fieldsets where the model is larger
- thumbnail/previews for images where useful

SiteSettings must behave as a singleton; there should never be multiple active site-settings rows.

Add admin actions carefully. Destructive actions should not be one-click operations unless there is a confirmation mechanism.

---

## 12. Media Handling

For uploaded images:

- validate file types
- constrain dimensions where appropriate
- create responsive renditions when needed
- use modern formats where supported
- add explicit width/height attributes to rendered images to reduce layout shift
- provide meaningful alt text

The original design also called for explicit image dimensions and lazy-loading except for hero assets. fileciteturn4file9L7156-L7182

---

## 13. Security

Required baseline:

- `DEBUG=False` in production
- secrets in environment variables
- secure cookie settings
- CSRF protection
- clickjacking protection
- content-type sniffing protection
- secure session configuration
- rate limits on public forms
- upload validation
- escape/sanitize rich HTML content before rendering
- admin protected by strong authentication

Do not expose raw exception details on production 500 pages.

---

## 14. Error Handling

Provide custom:

- 404 page
- 500 page

These must preserve VEE branding and offer a practical route back to Home or Contact.

---

## 15. Performance

Primary web performance objectives:

- fast first render
- low layout shift
- limited JavaScript execution
- responsive images
- deferred non-critical scripts
- no unnecessary third-party scripts

The original targets were:

- LCP < 2.5s
- INP < 200ms
- CLS < 0.1

Treat these as targets, then verify with Lighthouse/PageSpeed and real-user data rather than assuming them. fileciteturn4file9L7156-L7182

---

## 16. Deployment to HostAfrica

The final deployment guide must contain the exact HostAfrica environment once the hosting account and server type are confirmed.

Do not invent control-panel paths or server commands.

Deployment checklist:

1. Configure production environment variables.
2. Provision PostgreSQL and credentials where applicable.
3. Configure static collection and media storage.
4. Configure WSGI/ASGI application server as appropriate to HostAfrica's supported environment.
5. Configure domain and HTTPS.
6. Configure email DNS records after mailbox setup.
7. Run migrations.
8. Create the admin account.
9. Create/verify SiteSettings.
10. Run seed data only for genuine business content.
11. Submit sitemap in Google Search Console.
12. Verify analytics and form events.
13. Verify email and WhatsApp.
14. Test mobile and desktop.
15. Verify backup and restore.

Never put deployment credentials into Git.

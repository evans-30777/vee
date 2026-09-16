# VEE Agency Website

Django application for [veeagency.co.ke](https://veeagency.co.ke) — a digital growth agency based in Syokimau, Machakos County, serving Nairobi, Machakos, Kajiado, Kiambu and all of Kenya.

## Stack

- Django 5.2 (LTS), Python 3.11
- PostgreSQL in production, SQLite in local development
- WhiteNoise for static files, Gunicorn as the WSGI server

## Project layout

```
veeagency/settings/     base.py, dev.py, prod.py
apps/
├── accounts/           custom User (author profile)
├── core/               SiteSettings, Testimonial, CaseStudy, Newsletter, SEO helpers, sitemaps
├── services/           Service catalogue
├── packages/           Growth packages and one-time services
├── blog/               Categories and posts (Quick Answer + FAQ schema)
├── locations/          County landing pages
└── contact/            Enquiry form, notifications, newsletter signup
templates/              Server-rendered templates
static/
├── css/main.css        Design system + all components (no framework)
├── js/main.js          Progressive-enhancement behaviours
└── img/                Logo and favicons
```

## Front end

Dark-mode only at launch. Brand tokens are sampled from the real logo
(`#880000` dark red, `#E64A1A` orange); everything else is derived from the
tokens at the top of `static/css/main.css`.

There is no CSS framework and no JavaScript dependencies — motion is CSS
transitions driven by `IntersectionObserver`. This was chosen over GSAP/Lenis
deliberately: the effects the design calls for are native CSS, and the design
guide's own performance rules say to avoid large animation bundles where simple
CSS works. That matters on Kenyan mobile data.

**Everything in `main.js` is an enhancement.** The site is fully readable and
usable with JavaScript disabled or if the script fails to load:

- the preloader clears on a CSS timer, so it can never trap the page
- scroll reveals are only armed once JS confirms it can un-arm them, and have a
  4-second deadline as a second safety net
- the hero carousel renders its first slide from the server

If you change any of those, re-check both paths — there are tests covering them
in `apps/core/tests.py` (`test_first_hero_slide_is_active_without_javascript`).

## Local setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in values; dev works without it
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Development uses `veeagency.settings.dev` (SQLite, console email backend). Emails print to the terminal rather than sending.

## Running checks

```bash
python manage.py test          # full test suite
python manage.py check         # system checks
python manage.py check --deploy --settings=veeagency.settings.prod
```

## First-run configuration

1. Log into `/admin/`.
2. Open **Site settings** and create the single settings record. Defaults already carry the confirmed contact details:
   - Calls: `0717115737`
   - WhatsApp: `254759643882`
   - Email: `hello@veeagency.co.ke`
3. Add the Facebook and Instagram URLs once available. While blank, those icons are not rendered.
4. Add Services, Packages, Location pages, Blog categories and posts.

Testimonials and case studies stay hidden until real records are added — nothing is fabricated to fill space.

## Environment variables (production)

See `.env.example`. Required in production: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `POSTGRES_*`, and the `EMAIL_*` SMTP settings for enquiry notifications.

Never commit `.env`.

## Deployment to HostAfrica

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the full stage-by-stage guide.

Two things to know before you start:

- `manage.py` defaults to *development* settings, so every command on the server
  needs `--settings=veeagency.settings.prod` or it will use SQLite instead of
  PostgreSQL.
- Install SSL before pointing traffic at the site — production forces an HTTPS
  redirect and sends HSTS.

### Enquiry resilience

Enquiries are written to the database **before** email is attempted. If SMTP fails, the lead is still captured — the submission is flagged `notification_sent = False` in admin and the failure is logged. Check that flag if email delivery is ever interrupted.

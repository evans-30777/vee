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
```

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

The exact control-panel steps depend on the HostAfrica plan and are confirmed during deployment. The application-level checklist:

1. Set production environment variables.
2. Provision PostgreSQL and set `POSTGRES_*`.
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput`
5. Serve via Gunicorn with `DJANGO_SETTINGS_MODULE=veeagency.settings.prod`.
6. Configure HTTPS for the domain (production settings force SSL redirect and HSTS).
7. Create the superuser and the Site settings record.
8. Verify the enquiry form end-to-end, including email delivery.
9. Submit `/sitemap.xml` in Google Search Console.

### Enquiry resilience

Enquiries are written to the database **before** email is attempted. If SMTP fails, the lead is still captured — the submission is flagged `notification_sent = False` in admin and the failure is logged. Check that flag if email delivery is ever interrupted.

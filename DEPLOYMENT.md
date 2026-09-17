# Deployment

Two environments:

| | Where | Purpose |
|---|---|---|
| **Staging** | Render (`*.onrender.com`) | Test everything before launch — see [Staging on Render](#staging-on-render) |
| **Production** | HostAfrica + `veeagency.co.ke` | The live site — the rest of this document |

Both run the **same settings module** (`veeagency.settings.prod`), so what you
test on Render is what ships. The only differences come from the environment.

---

## Staging on Render

### The live staging service

| | |
|---|---|
| **URL** | https://vee-agency-staging.onrender.com |
| Service | `vee-agency-staging` (`srv-dalqptad0e5s738aseqg`), Frankfurt, free plan |
| Deploys | Automatically on every push to `main` |

> **Free plan, so there is no persistent disk.** The database and uploaded media
> live on an ephemeral filesystem and are **wiped on every deploy and restart**.
> Since auto-deploy is on, any content entered in the admin is lost the next time
> code is pushed. To keep content between deploys, upgrade the service to
> `starter` and add a disk mounted at `/var/data`, then set `SQLITE_PATH` to
> `/var/data/db.sqlite3` and `MEDIA_ROOT` to `/var/data/media`.
>
> The free plan also spins the service down when idle, so the first request after
> a quiet period takes about a minute.

### Creating the admin account

The free plan has no shell, so `createsuperuser` cannot be run interactively.
Instead, set these in the Render dashboard under **Environment**, then redeploy —
`render-build.sh` picks them up and creates the account:

```
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

Use a strong password: `/admin/` is reachable from the public internet. Remove
`DJANGO_SUPERUSER_PASSWORD` once the account exists.

### Deploying it from scratch

1. In Render, **New → Blueprint**, and point it at this repository. It reads
   `render.yaml`; there is nothing to configure by hand.
2. Wait for the first build. `render-build.sh` installs, runs `collectstatic`
   and applies migrations.
3. Open the `.onrender.com` URL. You should see an orange **STAGING** bar across
   the top.

`ALLOWED_HOSTS`, the CSRF origin and `SITE_BASE_URL` are all derived from
`RENDER_EXTERNAL_HOSTNAME`, which Render sets itself — so the site comes up on
its own URL with no host configuration.

### First run

The database starts empty, so parts of the site will be missing until you fill
it in — that is the empty-state rule working, not a fault. The WhatsApp button
and contact details stay hidden until Site settings exists.

Create the admin account as described above, then log in at `/admin/` and create
the **Site settings** record first.

### What staging mode changes

`SITE_IS_STAGING=true` is set in `render.yaml`, which:

- sends `noindex, nofollow` on **every** page
- serves a `robots.txt` that disallows everything and advertises no sitemap
- shows the STAGING bar

> **Do not remove this on a public test URL.** Without it Google indexes the
> staging site as a duplicate of `veeagency.co.ke`, the two compete, and it is
> slow and awkward to undo once indexed.

Canonical URLs also point at the staging host rather than the live domain, so a
staging page never claims a live URL as its canonical.

### Staging is not a rehearsal for the HostAfrica specifics

It genuinely tests the application, the production settings, the templates and
the content. It does **not** test HostAfrica's Passenger setup, its filesystem
layout, or the `/media/` serving rule — those are only exercised on the real
host.

---

# Production: HostAfrica

Application-level deployment steps for [veeagency.co.ke](https://veeagency.co.ke).

Control-panel labels vary by plan, so this document describes *what* each stage
has to achieve rather than guessing at menu names. Confirm the specifics against
your own HostAfrica plan as you go.

---

## Before you start: which plan?

This is the fork that changes the most steps.

| Plan type | How the app runs |
|---|---|
| **Shared / cPanel** | cPanel's Python app tool (usually "Setup Python App") creates the virtualenv and runs the WSGI app under Passenger. You do *not* start Gunicorn yourself. |
| | *With SQLite, keep the worker count low — SQLite serialises writes, so many workers gain you nothing on writes and raise the chance of lock contention.* |
| **VPS** | You run Gunicorn yourself (systemd service) with Nginx in front. |

`gunicorn` is already in `requirements.txt` for the VPS case. On shared cPanel
hosting it is simply unused.

---

## Read this first — two things that will bite you

### 1. `manage.py` defaults to **development** settings

```python
# manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "veeagency.settings.dev")
```

Every management command you run on the server must say otherwise:

```bash
python manage.py migrate --settings=veeagency.settings.prod
```

**Now that both environments use SQLite, this trap is quieter and worse.** Dev
settings write to `db.sqlite3` inside the project directory; production writes to
`SQLITE_PATH` outside the web root. Forget `--settings` and nothing errors — you
just migrate the wrong file, and create a stray `db.sqlite3` *inside the web root*
that the live site never reads.

If you find an unexpected `db.sqlite3` in the project directory on the server,
that is what happened. Delete it (it is also publicly downloadable) and re-run the
command with `--settings`.

Alternatively, export it once per shell (or in the deploy user's profile):

```bash
export DJANGO_SETTINGS_MODULE=veeagency.settings.prod
```

Putting `DJANGO_SETTINGS_MODULE` in `.env` does **not** work for management
commands — `manage.py` reads it before `.env` is loaded.

The web process is fine either way: `veeagency/wsgi.py` already defaults to
production settings.

### 2. Install SSL *before* pointing traffic at the site

Production settings force an HTTPS redirect and send HSTS for one year with
`includeSubDomains` and `preload`:

```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

Without a working certificate you get a redirect loop — and HSTS means browsers
will *remember* to force HTTPS, so the mistake outlives the fix. Get the
certificate working first.

---

## Stage 1 — Provision

1. Point `veeagency.co.ke` and `www.veeagency.co.ke` DNS at the HostAfrica server.
2. Install and verify the SSL certificate for both hostnames.
3. Create the directory that will hold the database — **outside the web root**
   (see below).

### The database is SQLite

HostAfrica does not offer PostgreSQL, so production runs on SQLite. For this site
that is a reasonable fit: writes are limited to enquiries, newsletter signups and
your own admin edits, which is well within what SQLite handles. `prod.py` enables
WAL mode so a write never blocks page views, and sets a 20-second lock timeout.

> ### ⚠️ Put the database file outside `public_html`
>
> This is the one mistake that turns SQLite into a breach. If the file sits inside
> the web root, **anyone can download your entire database** by guessing the URL —
> every contact enquiry, every email address, and your admin password hash.
>
> Create a directory *beside* the web root, not inside it:
>
> ```bash
> mkdir -p ~/vee-data
> chmod 700 ~/vee-data
> ```
>
> Then point `SQLITE_PATH` at it:
>
> ```
> SQLITE_PATH=/home/<cpanel-user>/vee-data/db.sqlite3
> ```
>
> Verify after going live — this must **not** return 200:
>
> ```bash
> curl -I https://veeagency.co.ke/db.sqlite3
> ```

**Back it up yourself.** The database is a single file, which makes this easy —
but nobody else is doing it. A scheduled copy is enough:

```bash
sqlite3 ~/vee-data/db.sqlite3 ".backup '~/vee-backups/db-$(date +%F).sqlite3'"
```

Use `.backup` rather than `cp` — it is safe to run while the site is serving.
Keep the backups off the server as well, and remember they are as sensitive as the
live database.

### Back up the media directory too

A database backup alone is **not** a full backup. Uploaded files — blog featured
images, testimonial logos, author headshot, the social sharing image — live on the
filesystem, not in the database. Restoring one without the other leaves you with
posts whose images 404.

```bash
tar -czf ~/vee-backups/media-$(date +%F).tar.gz -C /path/to/project media
```

Take both together, on the same schedule, and copy them off the server.

**If you outgrow SQLite** — sustained concurrent writes causing `database is
locked` errors under normal traffic — that is the signal to move to PostgreSQL.
At this data volume the migration is a `dumpdata` / `loaddata` round trip.

## Stage 2 — Get the code onto the server

```bash
git clone https://github.com/evans3077/vee.git
cd vee
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On cPanel, create the Python application first and install into the virtualenv
it provisions, rather than making your own.

## Stage 3 — Environment variables

Copy `.env.example` to `.env` in the project root and fill it in. Settings load
it automatically via `load_dotenv(BASE_DIR / ".env")`.

```
DJANGO_SECRET_KEY=<fresh 50+ character key>
DJANGO_ALLOWED_HOSTS=veeagency.co.ke,www.veeagency.co.ke
DJANGO_CSRF_TRUSTED_ORIGINS=https://veeagency.co.ke,https://www.veeagency.co.ke
SITE_BASE_URL=https://veeagency.co.ke

# Database — SQLite. MUST be outside the public web root.
SQLITE_PATH=/home/<cpanel-user>/vee-data/db.sqlite3

EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=hello@veeagency.co.ke
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=hello@veeagency.co.ke
ENQUIRY_NOTIFICATION_EMAIL=hello@veeagency.co.ke
```

Generate the secret key — never reuse the development one:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**`.env` is gitignored and must stay that way.** Never commit it, and never put
the database password or SMTP password anywhere in the repository.

Restrict the file so other accounts on a shared server cannot read it:

```bash
chmod 600 .env
```

## Stage 4 — Build

All three commands need production settings:

```bash
python manage.py migrate --settings=veeagency.settings.prod
python manage.py collectstatic --noinput --settings=veeagency.settings.prod
python manage.py createsuperuser --settings=veeagency.settings.prod
```

`collectstatic` must succeed. Production uses WhiteNoise's
`CompressedManifestStaticFilesStorage`, which builds a hashed manifest — if a
template references a static file that does not exist, the page raises an error
at render time rather than degrading quietly.

## Stage 5 — Serve

**Shared / cPanel:** set the application root to the project directory, the
application URL to the domain, and the WSGI entry point to `veeagency/wsgi.py`
(callable `application`). Restart the app.

**VPS:** run Gunicorn under systemd and put Nginx in front:

```bash
gunicorn veeagency.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

**Static and media files.** WhiteNoise serves `/static/` from inside the
application, so no web-server rule is needed for it. It does **not** serve
`/media/`. Uploaded files — blog featured images, testimonial logos, author
headshots, the social sharing image — need the web server to serve `MEDIA_ROOT`
at `/media/`, or those images will 404 while the rest of the site works.

## Stage 6 — Configure content

Log in at `/admin/` and:

1. **Create the Site settings record first.** Contact details, WhatsApp links and
   schema markup all read from it, and sections that depend on it stay hidden
   until it exists. Defaults already carry the confirmed numbers:
   - Calls: `0717115737`
   - WhatsApp: `254759643882`
   - Email: `hello@veeagency.co.ke`
2. Add the Facebook and Instagram URLs once available. While blank, those icons
   are deliberately not rendered.
3. Add Services, Packages, Location pages, Blog categories and posts.

Testimonials and case studies stay hidden until real records exist. Nothing is
fabricated to fill space — that is intentional, not an unfinished state.

## Stage 7 — Verify live

```bash
python manage.py check --deploy --settings=veeagency.settings.prod
```

Expect `System check identified no issues`.

Then check by hand:

- [ ] `https://veeagency.co.ke` loads over HTTPS, and `http://` redirects to it
- [ ] `www` resolves to the same site
- [ ] Submit a real enquiry end to end and confirm **both** emails arrive (your notification and the sender's acknowledgement)
- [ ] `/sitemap.xml` and `/robots.txt` load
- [ ] An uploaded image renders (confirms `/media/` is served)
- [ ] `/admin/` is reachable and login works
- [ ] A missing URL returns the styled 404 page
- [ ] The site is readable with JavaScript disabled

Finally, submit `https://veeagency.co.ke/sitemap.xml` in Google Search Console.

---

## If enquiry emails stop arriving

Enquiries are written to the database **before** email is attempted, so an SMTP
outage does not lose the lead.

Check the `notification_sent` flag on Contact submissions in the admin. Records
with it unset were captured successfully but never emailed — the failure is also
written to the application log. Fix the SMTP credentials and follow up on those
leads manually; the data is intact.

---

## Redeploying after a change

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt                                    # only if it changed
python manage.py migrate --settings=veeagency.settings.prod
python manage.py collectstatic --noinput --settings=veeagency.settings.prod
```

Then restart the application (cPanel: restart the Python app; VPS:
`sudo systemctl restart gunicorn`). Static file changes will not appear until
both `collectstatic` and the restart have run.

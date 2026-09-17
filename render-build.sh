#!/usr/bin/env bash
# Render build step. Exit on any failure so a broken build never goes live.
set -o errexit

# Deliberately no `pip install --upgrade pip`: it can fail on a
# distribution-managed pip and, under errexit, would abort the whole build for
# no benefit.
pip install -r requirements.txt

# Create the data directories before migrate runs. Needed when SQLITE_PATH and
# MEDIA_ROOT point at a mounted disk: the mount point exists but the tree under
# it does not, and migrate would fail trying to open the database.
if [ -n "${SQLITE_PATH:-}" ]; then mkdir -p "$(dirname "$SQLITE_PATH")"; fi
if [ -n "${MEDIA_ROOT:-}" ]; then mkdir -p "$MEDIA_ROOT"; fi

# Must run with production settings: the manifest static storage is only built
# here, and without it every page raises at render time.
python manage.py collectstatic --no-input
python manage.py migrate

# Optional superuser bootstrap.
#
# Render's free tier provides no shell, so there is otherwise no way to create
# the first admin account. Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL
# and DJANGO_SUPERUSER_PASSWORD in the Render dashboard (never in this repo) and
# the account is created on the next build.
#
# `|| true` because this reruns on every build and errors once the user exists;
# an existing account is the expected case, not a build failure.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    python manage.py createsuperuser --noinput || true
fi

# Optional content seeding.
#
# Staging has no persistent disk, so the database is rebuilt on every deploy.
# This repopulates it from the master spec so there is always something to
# review. Gated on SEED_CONTENT so it can never run against production, and the
# command itself leaves existing records alone unless passed --update.
if [ "${SEED_CONTENT:-}" = "true" ]; then
    python manage.py seed_content --with-posts
fi

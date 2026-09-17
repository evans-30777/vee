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

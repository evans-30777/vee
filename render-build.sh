#!/usr/bin/env bash
# Render build step. Exit on any failure so a broken build never goes live.
set -o errexit

# Deliberately no `pip install --upgrade pip`: it can fail on a
# distribution-managed pip and, under errexit, would abort the whole build for
# no benefit.
pip install -r requirements.txt

# Must run with production settings: the manifest static storage is only built
# here, and without it every page raises at render time.
python manage.py collectstatic --no-input
python manage.py migrate

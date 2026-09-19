"""
Seed the owner's profile and site settings with real data.

Run with:
    venv\Scripts\python.exe tools/seed_owner_profile.py

This script is safe to re-run — it updates, never duplicates.
"""
import os
import sys
import django

# Ensure project root is on the path and use dev settings for local execution.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "veeagency.settings.dev")
django.setup()

from django.contrib.auth import get_user_model
from django.core.files import File
from apps.core.models import SiteSettings

User = get_user_model()

# ------------------------------------------------------------------ Bio text
# Crafted from Evans' own words, keeping his direct voice.
BIO = (
    "I'm Evans Ngumbau — the founder and the person who does the work at VEE Agency. "
    "My background is in web development, digital marketing and data analysis, "
    "but what pulls it all together is a straightforward approach: understand the "
    "business first, find the real opportunity, then build and execute with purpose. "
    "I started VEE Agency because I kept seeing the same problem — businesses putting "
    "effort into their online presence and getting nothing measurable back. "
    "That is a structure problem, and structure is fixable. "
    "You deal with me directly, from the first conversation to the finished work."
)

# ---------------------------------------------------------------- Update user
user = User.objects.first()
if user is None:
    print("No user found. Create a superuser first with: manage.py createsuperuser")
    sys.exit(1)

user.first_name = "Evans"
user.last_name = "Ngumbau"
user.job_title = "Founder & Digital Growth Lead"
user.bio = BIO
user.instagram = "https://www.instagram.com/evansngumbau/"
user.facebook = "https://www.facebook.com/profile.php?id=61593709514800"

# Attach the headshot only if it is not already set.
headshot_path = os.path.join(ROOT, "initial assets", "evans-ngumbau.jpg")
if not user.headshot and os.path.exists(headshot_path):
    with open(headshot_path, "rb") as f:
        user.headshot.save("evans-ngumbau.jpg", File(f), save=False)
    print("  headshot attached")
elif user.headshot:
    print("  headshot already set — skipping")
else:
    print(f"  WARNING: headshot not found at {headshot_path}")

user.save()
print(f"User updated: {user.get_full_name()} ({user.username})")

# --------------------------------------------------------- Update SiteSettings
settings = SiteSettings.load()
if settings is None:
    print("No SiteSettings record found. Create one in /admin/ first.")
    sys.exit(1)

settings.facebook_url = "https://www.facebook.com/profile.php?id=61593709514800"
settings.instagram_url = "https://www.instagram.com/evansngumbau/"
settings.save()
print("SiteSettings updated: Facebook and Instagram URLs set.")
print("\nDone. Restart the dev server to see the changes.")

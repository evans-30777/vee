from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user, primarily the VEE Agency author/owner for blog attribution."""

    bio = models.TextField(blank=True)
    headshot = models.ImageField(upload_to="authors/", blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def display_name(self):
        return self.get_full_name() or self.username

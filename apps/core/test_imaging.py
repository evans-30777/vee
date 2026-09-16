"""Tests for upload image downscaling.

These build real image files rather than mocks, because the failure modes worth
catching here (EXIF rotation, alpha loss, animated GIFs) only show up in real
pixel data.
"""

import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from apps.blog.models import BlogPost
from apps.accounts.models import User

from .imaging import optimise_image_field
from .models import SiteSettings, Testimonial

MEDIA_ROOT = tempfile.mkdtemp()


def make_image(width, height, *, fmt="JPEG", mode="RGB", colour=(220, 70, 20), exif=None):
    image = Image.new(mode, (width, height), colour)
    buffer = BytesIO()
    save_kwargs = {"exif": exif} if exif else {}
    image.save(buffer, format=fmt, **save_kwargs)
    return buffer.getvalue()


def upload(name, data, content_type="image/jpeg"):
    return SimpleUploadedFile(name, data, content_type=content_type)


def open_field(field_file):
    field_file.open()
    field_file.seek(0)
    return Image.open(BytesIO(field_file.read()))


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ImageOptimisationTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_oversized_photo_is_downscaled(self):
        """The core case: a phone-sized photo must not ship at full size."""
        author = User.objects.create_user(username="evans", password="test-pass-123")
        post = BlogPost.objects.create(
            title="Big image",
            slug="big-image",
            excerpt="x",
            body="x",
            author=author,
            featured_image=upload("photo.jpg", make_image(4000, 3000)),
        )

        image = open_field(post.featured_image)
        self.assertLessEqual(image.width, 1600)
        self.assertLessEqual(image.height, 1600)

    def test_aspect_ratio_is_preserved(self):
        author = User.objects.create_user(username="ratio", password="test-pass-123")
        post = BlogPost.objects.create(
            title="Ratio", slug="ratio", excerpt="x", body="x", author=author,
            featured_image=upload("wide.jpg", make_image(4000, 2000)),
        )
        image = open_field(post.featured_image)
        self.assertAlmostEqual(image.width / image.height, 2.0, places=2)

    def test_small_image_is_left_untouched(self):
        """Repeated saves must not re-encode and slowly degrade the same file."""
        original = make_image(500, 400)
        testimonial = Testimonial.objects.create(
            client_name="Small logo",
            quote="x",
            logo=upload("logo.png", make_image(300, 200, fmt="PNG"), "image/png"),
        )
        before = testimonial.logo.size
        testimonial.save()
        testimonial.save()
        testimonial.refresh_from_db()
        self.assertEqual(testimonial.logo.size, before)
        self.assertTrue(original)  # guards against an accidentally empty fixture

    def test_transparency_survives_resizing(self):
        """Client logos are transparent PNGs; flattening them would be visible."""
        testimonial = Testimonial.objects.create(
            client_name="Transparent",
            quote="x",
            logo=upload(
                "logo.png",
                make_image(1200, 1200, fmt="PNG", mode="RGBA", colour=(200, 0, 0, 0)),
                "image/png",
            ),
        )
        image = open_field(testimonial.logo)
        self.assertEqual(image.format, "PNG")
        self.assertIn("A", image.getbands())
        self.assertLessEqual(image.width, 400)

    def test_format_is_preserved_so_extensions_stay_honest(self):
        author = User.objects.create_user(username="fmt", password="test-pass-123")
        post = BlogPost.objects.create(
            title="Format", slug="format", excerpt="x", body="x", author=author,
            featured_image=upload("photo.jpg", make_image(3000, 2000)),
        )
        self.assertEqual(open_field(post.featured_image).format, "JPEG")

    def test_exif_rotation_is_applied(self):
        """Phone photos store rotation as a flag; ignoring it shows them sideways."""
        exif = Image.Exif()
        exif[274] = 6  # Orientation: rotate 90°
        data = make_image(3000, 2000, exif=exif.tobytes())

        author = User.objects.create_user(username="exif", password="test-pass-123")
        post = BlogPost.objects.create(
            title="Rotated", slug="rotated", excerpt="x", body="x", author=author,
            featured_image=upload("rotated.jpg", data),
        )

        image = open_field(post.featured_image)
        # Orientation 6 means the stored landscape frame is really a portrait.
        self.assertGreater(image.height, image.width)

    def test_animated_gif_is_skipped(self):
        """Re-encoding would flatten the animation to one frame."""
        frames = [Image.new("P", (900, 900), i) for i in (1, 2, 3)]
        buffer = BytesIO()
        frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:])
        gif = buffer.getvalue()

        testimonial = Testimonial.objects.create(
            client_name="Animated", quote="x",
            logo=upload("anim.gif", gif, "image/gif"),
        )
        image = open_field(testimonial.logo)
        self.assertEqual(image.format, "GIF")
        self.assertTrue(getattr(image, "is_animated", False))
        self.assertEqual(image.width, 900)  # untouched

    def test_corrupt_file_does_not_break_saving(self):
        """A picture Pillow dislikes must never take down an admin save."""
        testimonial = Testimonial.objects.create(
            client_name="Corrupt", quote="x",
            logo=upload("broken.jpg", b"this is definitely not an image"),
        )
        self.assertEqual(Testimonial.objects.count(), 1)
        self.assertTrue(testimonial.logo.name)

    def test_empty_field_is_a_no_op(self):
        testimonial = Testimonial.objects.create(client_name="No logo", quote="x")
        self.assertFalse(optimise_image_field(testimonial.logo, max_width=100, max_height=100))

    def test_upload_path_does_not_nest_on_repeated_saves(self):
        """The field re-applies upload_to, so passing back a stored path would nest it."""
        author = User.objects.create_user(username="nest", password="test-pass-123")
        post = BlogPost.objects.create(
            title="Nesting", slug="nesting", excerpt="x", body="x", author=author,
            featured_image=upload("photo.jpg", make_image(3000, 2000)),
        )
        for _ in range(3):
            post.save()
        post.refresh_from_db()
        self.assertEqual(post.featured_image.name.count("blog/"), 1)

    def test_site_settings_social_image_is_downscaled(self):
        settings_obj = SiteSettings.objects.create(
            default_social_image=upload("og.jpg", make_image(3000, 3000)),
        )
        image = open_field(settings_obj.default_social_image)
        self.assertLessEqual(image.width, 1200)

    def test_author_headshot_is_downscaled(self):
        author = User.objects.create_user(
            username="headshot", password="test-pass-123",
            headshot=upload("me.jpg", make_image(2500, 2500)),
        )
        self.assertLessEqual(open_field(author.headshot).width, 800)

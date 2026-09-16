"""Downscale uploaded images.

Images reach this site straight from a phone or a camera, where a single
featured image is routinely 3–5MB. Django does no resizing of its own, so
without this every mobile visitor would download the original — which would
undo the front end's performance work on exactly the connections that can
least afford it.
"""

import logging
import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Re-encoding an animated GIF would flatten it to a single frame, so GIFs are
# left alone. Anything Pillow cannot identify is left alone too.
SKIP_FORMATS = {"GIF"}

# MPO is what many phone cameras actually produce; it is JPEG underneath.
JPEG_FORMATS = {"JPEG", "MPO"}


def _save_kwargs(image_format, quality):
    if image_format in JPEG_FORMATS:
        return "JPEG", {"quality": quality, "optimize": True, "progressive": True}
    if image_format == "WEBP":
        return "WEBP", {"quality": quality, "method": 6}
    if image_format == "PNG":
        return "PNG", {"optimize": True}
    return image_format, {}


def optimise_image_field(field_file, *, max_width, max_height, quality=82):
    """Shrink an image field's file in place if it exceeds the given bounds.

    Returns True when the file was rewritten.

    Deliberately conservative:

    - no-op when the image already fits, so saving a record repeatedly does not
      re-encode and progressively degrade the same picture
    - the original format is kept, so transparent PNG logos stay transparent and
      a file's extension never stops matching its contents
    - EXIF orientation is applied, because phone photos are commonly stored
      rotated with a flag rather than rotated in the pixels
    - any failure is logged and swallowed; a picture Pillow dislikes must not
      take down an admin save
    """
    if not field_file:
        return False

    try:
        field_file.open()
        field_file.seek(0)
        image = Image.open(field_file)
        image_format = image.format

        if image_format in SKIP_FORMATS:
            return False

        # Load before the underlying file is closed or replaced.
        image = ImageOps.exif_transpose(image)

        if image.width <= max_width and image.height <= max_height:
            return False

        image.thumbnail((max_width, max_height), Image.LANCZOS)

        target_format, save_kwargs = _save_kwargs(image_format, quality)

        # A JPEG cannot hold an alpha channel; flatten onto white rather than
        # letting Pillow raise.
        if target_format == "JPEG" and image.mode not in ("RGB", "L"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A") if "A" in image.getbands() else None)
            image = background

        buffer = BytesIO()
        image.save(buffer, format=target_format, **save_kwargs)
    except Exception:
        logger.exception("Could not optimise image %s; leaving it unchanged", field_file)
        return False

    # Only the basename: the field re-applies its own upload_to prefix, so
    # passing the stored path back would nest the directory on every save.
    field_file.save(os.path.basename(field_file.name), ContentFile(buffer.getvalue()), save=False)
    return True

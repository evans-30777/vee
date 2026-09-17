"""Rendering for author-written rich text.

Post bodies were plain text run through `linebreaks`, which escapes HTML. That
meant a post could not carry a heading, a list, or a single internal link — and
the blog is normally a site's main internal-linking engine. It showed: the
seeded post on website pricing was *written* with five subheadings, and every
one of them rendered as an ordinary paragraph.

Markdown in, sanitised HTML out. The author is trusted, but sanitising anyway
costs nothing and means a compromised admin account cannot inject a script into
every reader's browser.
"""

import bleach
import markdown
from django.utils.safestring import mark_safe

# Headings start at h2: the post title is the h1, and a body that can emit its
# own h1 breaks the document outline on every page it appears.
ALLOWED_TAGS = {
    "h2", "h3", "h4",
    "p", "br", "hr",
    "ul", "ol", "li",
    "strong", "em", "b", "i", "del",
    "a", "blockquote",
    "code", "pre",
    "table", "thead", "tbody", "tr", "th", "td",
    "img", "figure", "figcaption",
}

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "width", "height", "loading"],
    "th": ["colspan", "rowspan", "scope"],
    "td": ["colspan", "rowspan"],
    "ol": ["start"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "tel"]

MARKDOWN_EXTENSIONS = [
    "extra",        # tables, footnotes, definition lists, fenced code
    "sane_lists",
    "smarty",       # real quotes and dashes, matching the rest of the site
]


def render_markdown(text):
    """Markdown -> sanitised HTML, safe to mark safe."""
    if not text:
        return ""

    html = markdown.markdown(
        text,
        extensions=MARKDOWN_EXTENSIONS,
        output_format="html",
    )

    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )

    # Anything pointing off-site opens in a new tab and cannot reach back
    # through window.opener.
    cleaned = bleach.linkify(
        cleaned,
        callbacks=[_external_links_open_safely],
        skip_tags=["pre", "code"],
        parse_email=False,
    )

    # A Markdown table has no wrapper of its own, so a wide one would push the
    # whole page sideways on a phone.
    cleaned = cleaned.replace(
        "<table>",
        '<div class="table-wrap" tabindex="0" role="region" aria-label="Table"><table class="table">',
    ).replace("</table>", "</table></div>")

    return mark_safe(cleaned)


def _external_links_open_safely(attrs, new=False):
    href = attrs.get((None, "href"), "")
    if href.startswith(("http://", "https://")) and "veeagency.co.ke" not in href:
        attrs[(None, "target")] = "_blank"
        attrs[(None, "rel")] = "noopener noreferrer"
    return attrs


def table_of_contents(html):
    """Headings in the rendered body, for a long post's contents list.

    Returns [] rather than raising when there is nothing to list, so a short
    post simply does not get one.
    """
    import re

    headings = re.findall(r"<(h2|h3)>(.*?)</\1>", html, re.S)
    return [
        {"level": int(tag[1]), "text": bleach.clean(text, tags=set(), strip=True).strip()}
        for tag, text in headings
    ]

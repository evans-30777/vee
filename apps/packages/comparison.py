"""Feature-by-tier comparison for the monthly growth packages.

Why this exists as a matrix rather than three lists
---------------------------------------------------
The cards show what each package *is*. They cannot show what changes between
tiers, because several features are upgrades of the same capability rather than
additions to it: "Basic website audit" and "Full website audit & revamp plan"
are one row, not two. A set-union of the three `features` lists would print both
and read as a mistake.

The tiers are cumulative, confirmed by the owner (2026-09-17): Standard includes
everything in Essential, and Premium includes everything in Standard. So a blank
cell means genuinely not included, and a ticked cell inherited from a lower tier
is still ticked here.

Keeping it in sync
------------------
`test_every_seeded_feature_appears_in_the_comparison` asserts that every string
in every package's `features` list is accounted for below. Add a feature in
Admin without adding it here and that test fails, which is the point: a silently
stale comparison table is worse than none.
"""

INCLUDED = "included"
EXCLUDED = "excluded"

# Slugs of the monthly tiers, cheapest first. The table's columns.
TIER_SLUGS = ["essential", "standard", "premium"]

# (row label, {tier slug: cell}) where a cell is INCLUDED, EXCLUDED, or text
# describing what that tier gets when the capability differs by tier.
COMPARISON_ROWS = [
    (
        "Google Business Profile audit & optimisation",
        {"essential": INCLUDED, "standard": INCLUDED, "premium": INCLUDED},
        "Getting you onto the map, and keeping the listing complete and active.",
    ),
    (
        "Social media profile optimisation",
        {"essential": INCLUDED, "standard": INCLUDED, "premium": INCLUDED},
        "Profiles that look professional and say what you actually do.",
    ),
    (
        "Content creation",
        {"essential": INCLUDED, "standard": INCLUDED, "premium": INCLUDED},
        "The posts themselves — written and designed, not just scheduled.",
    ),
    (
        "Social posting",
        {
            "essential": "3 posts a week — TikTok, Facebook, Instagram",
            "standard": "3 posts a week — TikTok, Facebook, Instagram",
            "premium": "5 posts a week — adds X and LinkedIn",
        },
        "How often you show up, and where.",
    ),
    (
        "Linktree setup & optimisation",
        {"essential": EXCLUDED, "standard": INCLUDED, "premium": INCLUDED},
        "One link in your bios that routes people to the right place.",
    ),
    (
        "Website audit",
        {
            "essential": EXCLUDED,
            "standard": "Basic audit",
            "premium": "Full audit & revamp plan",
        },
        "Finding what on your site is costing you enquiries.",
    ),
    (
        "Search optimisation",
        {
            "essential": EXCLUDED,
            "standard": "SEO optimisation",
            "premium": "Full SEO & AEO optimisation",
        },
        "AEO is being the answer AI assistants give, not just a blue link.",
    ),
    (
        "Competitor analysis",
        {
            "essential": EXCLUDED,
            "standard": "Included",
            "premium": "Full analysis + remediation plan",
        },
        "What the businesses beating you are actually doing.",
    ),
    (
        "Ads campaign management",
        {
            "essential": EXCLUDED,
            "standard": "1 platform",
            "premium": "Across platforms, managed",
        },
        "Media spend is billed separately — this is the management of it.",
    ),
]

# Seeded feature strings that the rows above already cover. Maps the wording in
# Package.features to the row it belongs to, so drift is detectable.
FEATURE_TO_ROW = {
    "Google Business Profile audit & optimization": "Google Business Profile audit & optimisation",
    "Social media profile optimization": "Social media profile optimisation",
    "Content creation": "Content creation",
    "3 posts/week on TikTok, Facebook & Instagram": "Social posting",
    "5 posts/week across TikTok, Facebook, Instagram, X & LinkedIn": "Social posting",
    "Linktree creation & optimization": "Linktree setup & optimisation",
    "Basic website audit": "Website audit",
    "Full website audit & revamp plan": "Website audit",
    "SEO optimization": "Search optimisation",
    "Full SEO & AEO optimization": "Search optimisation",
    "Competitor analysis": "Competitor analysis",
    "Full competitor analysis + remediation plan": "Competitor analysis",
    "Ads management — 1 platform": "Ads campaign management",
    "Expert ads campaign management across platforms": "Ads campaign management",
}


def build_comparison(packages):
    """Rows ready for the template, ordered to match `packages`.

    Returns None when the tiers on the page are not the three this matrix
    describes — a fourth package added in Admin should drop the table rather
    than render a misleading one.
    """
    by_slug = {package.slug: package for package in packages}
    if sorted(by_slug) != sorted(TIER_SLUGS):
        return None

    columns = [by_slug[slug] for slug in TIER_SLUGS]
    rows = []
    for label, cells, note in COMPARISON_ROWS:
        rows.append(
            {
                "label": label,
                "note": note,
                "cells": [
                    {
                        "included": cells[slug] != EXCLUDED,
                        "text": "" if cells[slug] in (INCLUDED, EXCLUDED) else cells[slug],
                    }
                    for slug in TIER_SLUGS
                ],
            }
        )
    return {"columns": columns, "rows": rows}

"""Populate the site with its real content.

Every price, package inclusion and service in here is transcribed from
`vee_website_docs/00_MASTER_WEBSITE_SPEC.md` sections 6 and 7 (the package and
service source of truth). Nothing is invented. If the spec and this file ever
disagree, the spec wins.

Deliberately absent: testimonials and case studies. Those are proof, and proof
is never fabricated — the empty-state rule hides those sections until real,
client-approved records exist.

Safe to re-run. By default existing records are left alone, so running this
against a populated site never overwrites edits made in Admin. Pass --update to
force values back to the spec.
"""

import textwrap

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.blog.models import BlogPost, Category
from apps.core.models import SiteSettings
from apps.locations.models import LocationPage
from apps.packages.models import Package
from apps.services.models import Service

# --------------------------------------------------------------------- Packages
# Spec section 6. Slugs must stay as they are: the "Choose Plan" buttons pass
# them to the contact form, which validates against ContactSubmission.Service.
PACKAGES = [
    {
        "slug": "essential",
        "name": "Essential Growth",
        "billing_type": "monthly",
        "price": 15000,
        "short_description": "Get the fundamentals right — found on Google, consistent on social.",
        "ideal_for": "Businesses putting their online presence in order for the first time",
        "features": [
            "Google Business Profile audit & optimization",
            "Social media profile optimization",
            "3 posts/week on TikTok, Facebook & Instagram",
            "Content creation",
        ],
        "order": 1,
    },
    {
        "slug": "standard",
        "name": "Standard Growth",
        "billing_type": "monthly",
        "price": 25000,
        "short_description": "Everything in Essential, plus search visibility and paid reach.",
        "ideal_for": "Established businesses ready to compete for search traffic",
        "is_highlighted": True,
        "features": [
            "Google Business Profile audit & optimization",
            "Social media profile optimization",
            "3 posts/week on TikTok, Facebook & Instagram",
            "Basic website audit",
            "SEO optimization",
            "Ads management — 1 platform",
            "Competitor analysis",
            "Linktree creation & optimization",
        ],
        "order": 2,
    },
    {
        "slug": "premium",
        "name": "Premium Growth",
        "billing_type": "monthly",
        "price": 45000,
        "short_description": "The full system — search, social, ads and site, managed together.",
        "ideal_for": "Businesses scaling and competing seriously online",
        "features": [
            "Google Business Profile audit & optimization",
            "Social media profile optimization",
            "5 posts/week across TikTok, Facebook, Instagram, X & LinkedIn",
            "Full website audit & revamp plan",
            "Expert ads campaign management across platforms",
            "Full competitor analysis + remediation plan",
            "Full SEO & AEO optimization",
        ],
        "order": 3,
    },
    {
        "slug": "website",
        "name": "Website Development",
        "billing_type": "one_time",
        "price": 30000,
        "price_is_from": True,
        "short_description": (
            "A custom website built around how your business actually sells — "
            "mobile-friendly, SEO and AEO ready, with clear enquiry paths."
        ),
        "ideal_for": "Any business that needs a website that brings in enquiries",
        "features": [
            "Custom design around your brand",
            "Mobile-first build",
            "SEO, AEO & GEO ready structure",
            "Clear enquiry and WhatsApp paths",
            "Google Search Console setup",
            "Launch support",
        ],
        "order": 4,
    },
]

# --------------------------------------------------------------------- Services
# Spec section 7, "Standalone Website Services".
SERVICES = [
    {
        "slug": "website-creation",
        "icon": "WEB",
        "name": "Website Creation",
        "tagline": "Built to bring in enquiries, not just to exist",
        "starting_price": 30000,
        "short_description": (
            "Custom website design and development — mobile-friendly, SEO and AEO ready, "
            "with clear enquiry or booking paths."
        ),
        "full_description": (
            "Your website is usually the first thing a customer checks after they hear about "
            "you. We build it around what your business actually needs it to do: show your "
            "work, sell your products, or take bookings.\n\n"
            "Every build is structured for search from day one rather than optimised as an "
            "afterthought, so the site has a chance of being found instead of only being "
            "shown to people you send there yourself."
        ),
        "deliverables": [
            "Custom design around your brand",
            "Mobile-first build",
            "SEO, AEO and GEO ready structure",
            "Clear enquiry and WhatsApp paths",
            "Google Search Console setup",
            "Launch support",
        ],
        "order": 1,
    },
    {
        "slug": "website-audit-revamp",
        "icon": "FIX",
        "name": "Website Audit & Full Revamp",
        "tagline": "Find out what your current site is costing you",
        "starting_price": 15000,
        "short_description": (
            "Audit, structure review, content and UX improvements, stronger calls-to-action "
            "and clearer enquiry paths."
        ),
        "full_description": (
            "Plenty of businesses already have a website. Far fewer have one that brings in "
            "enquiries. An audit tells you which you have — and what specifically to change.\n\n"
            "From KES 15,000 for existing VEE clients, and from KES 25,000 for new clients, "
            "because a site we did not build takes longer to understand before we can improve it."
        ),
        "deliverables": [
            "Structure and navigation review",
            "Speed and mobile audit",
            "Content and UX improvements",
            "Stronger calls-to-action",
            "Clearer enquiry paths",
        ],
        "order": 2,
    },
    {
        "slug": "website-management",
        "icon": "CARE",
        "name": "Website Management",
        "tagline": "Keep it current without thinking about it",
        "starting_price": 5000,
        "short_description": (
            "Regular content updates, maintenance, monitoring, broken-link and performance checks."
        ),
        "full_description": (
            "Websites decay quietly. Content goes stale, links break, plugins fall behind and "
            "speed drifts — usually without anyone noticing until a customer does.\n\n"
            "From KES 5,000/month we handle updates and monitoring so the site stays accurate "
            "and quick, and you stay focused on running the business."
        ),
        "deliverables": [
            "Regular content updates",
            "Maintenance and monitoring",
            "Broken-link checks",
            "Performance checks",
        ],
        "order": 3,
    },
    {
        "slug": "seo-optimization",
        "icon": "SEO",
        "name": "Full SEO Optimization",
        "tagline": "Get found when customers search",
        "starting_price": 10000,
        "short_description": (
            "On-site SEO including keyword, page structure and technical improvements."
        ),
        "full_description": (
            "Search is where buying decisions usually start. SEO work makes your pages easier "
            "for Google to understand and rank — keywords that match how customers actually "
            "search, page structure that makes sense, and the technical fixes that quietly "
            "hold most sites back.\n\n"
            "No rankings are guaranteed, by us or by anyone honest. What is committed to is "
            "the work and a clear account of what changed."
        ),
        "deliverables": [
            "Keyword research",
            "Page structure improvements",
            "Technical SEO fixes",
            "On-page optimisation",
        ],
        "order": 4,
    },
    {
        "slug": "seo-aeo-optimization",
        "icon": "AEO",
        "name": "Full SEO & AEO Optimization",
        "tagline": "Be the answer, not just a result",
        "starting_price": 15000,
        "short_description": (
            "SEO plus AEO-oriented structuring for AI-driven search and answer experiences."
        ),
        "full_description": (
            "More people now get an answer rather than a list of links — from Google's own "
            "summaries, from voice assistants, and from AI tools they ask directly.\n\n"
            "AEO structures your content so it can be read, quoted and cited by those systems: "
            "direct answers, clear headings, proper FAQ markup. It builds on SEO rather than "
            "replacing it."
        ),
        "deliverables": [
            "Everything in Full SEO Optimization",
            "Direct-answer content structuring",
            "FAQ and schema markup",
            "Answer-engine visibility review",
        ],
        "order": 5,
    },
    {
        "slug": "competitor-analysis",
        "icon": "VS",
        "name": "Competitor Analysis",
        "tagline": "Know exactly what you are up against",
        "starting_price": 5000,
        "short_description": (
            "Comparison against five competitors, with findings across website, Google presence "
            "and social media."
        ),
        "full_description": (
            "Most businesses guess at what their competitors are doing online. This replaces "
            "the guess with a document.\n\n"
            "Five competitors as the base scope, compared on website, Google presence and "
            "social media — what they are doing better, where the gaps are, and which of those "
            "gaps are actually worth your money."
        ),
        "deliverables": [
            "Five competitors as base scope",
            "Website comparison",
            "Google presence comparison",
            "Social media comparison",
            "Findings and opportunities",
        ],
        "order": 6,
    },
    {
        "slug": "digital-ads-management",
        "icon": "ADS",
        "name": "Digital Ads Management",
        "tagline": "Spend that reaches buyers, not noise",
        "starting_price": 5000,
        "short_description": (
            "Campaign management on supported ad platforms. KES 5,000 per platform per campaign; "
            "advertising spend is billed separately."
        ),
        "full_description": (
            "Ads work when the targeting is right and the page they land on is ready. We manage "
            "the campaign end to end and tell you plainly when the money would be better spent "
            "fixing the site first.\n\n"
            "The management fee is KES 5,000 per platform per campaign. What you pay Google or "
            "Meta for the advertising itself is separate and goes directly to them."
        ),
        "deliverables": [
            "Campaign strategy",
            "Audience targeting",
            "Ad creative",
            "Performance reporting",
        ],
        "order": 7,
    },
]

# ---------------------------------------------------------------- Blog categories
# Spec section 9, "Blog Strategy".
CATEGORIES = [
    ("SEO & AEO", "seo-aeo", "Getting found on Google and quoted by AI answer engines."),
    ("Ads & Performance", "ads-performance", "Making advertising spend produce customers."),
    ("Social Media", "social-media", "Staying visible and credible between enquiries."),
    ("Web Development", "web-development", "Websites that bring in business."),
    ("Case Studies", "case-studies", "Real projects and what came out of them."),
]

# --------------------------------------------------------------------- Locations
# Spec section 8 requires each county page to be genuinely different and
# genuinely useful — not one keyword-stuffed page repeated four times.
LOCATIONS = [
    {
        "slug": "nairobi",
        "county": "Nairobi",
        "hero_headline": "Digital Growth Agency for Nairobi Businesses",
        "intro": (
            "Nairobi is the most competitive market in Kenya to be found in. For almost any "
            "service, a customer searching online has a full page of options before they "
            "reach you — so being present is not the same as being chosen."
        ),
        "body": (
            "We work with Nairobi businesses on the parts that decide it: a website that "
            "answers the question a customer actually came with, a Google Business Profile "
            "that is complete and active, and search presence built for how people really "
            "search — usually with a neighbourhood attached, not just \"in Nairobi\".\n\n"
            "Competition here also means your competitors are advertising. That makes it "
            "worth knowing what they are doing before you spend, which is why a competitor "
            "analysis is often the most useful first step for a Nairobi business rather than "
            "an immediate ad campaign.\n\n"
            "We are based in Syokimau, a short distance from the city, and work with Nairobi "
            "clients both remotely and in person."
        ),
        "order": 1,
    },
    {
        "slug": "machakos",
        "county": "Machakos",
        "hero_headline": "Digital Growth Agency in Machakos County",
        "intro": (
            "Machakos County is home ground — VEE Agency is based in Syokimau. Businesses "
            "here are often competing for customers who are physically nearby but searching "
            "online first."
        ),
        "body": (
            "For a lot of Machakos businesses, the gap is not marketing at all. It is that "
            "the business is effectively invisible to someone searching: no Google listing, "
            "or one with an old phone number and no photos. Fixing that is usually the "
            "cheapest improvement available.\n\n"
            "Machakos also has real growth around Syokimau, Mlolongo and Athi River, where "
            "new businesses open constantly and customers genuinely do search before "
            "choosing. Being the one with a working website and a complete Google profile "
            "is often enough to win the enquiry.\n\n"
            "Being local means we can meet, look at your business properly, and understand "
            "who actually walks through your door."
        ),
        "order": 2,
    },
    {
        "slug": "kajiado",
        "county": "Kajiado",
        "hero_headline": "Digital Growth Agency in Kajiado County",
        "intro": (
            "Kajiado County covers fast-growing towns like Kitengela, Ongata Rongai, Ngong "
            "and Kiserian — areas where new businesses open quickly and customers rely "
            "heavily on their phones to decide where to go."
        ),
        "body": (
            "Businesses in Kajiado often serve a specific town rather than the whole county, "
            "which changes what useful search visibility looks like. A salon in Kitengela "
            "does not need to rank across Kenya; it needs to be the obvious choice for "
            "someone searching in Kitengela.\n\n"
            "That makes Google Business Profile work and local search the highest-value "
            "starting point for most Kajiado businesses, with a website that loads quickly "
            "on mobile data and makes calling or messaging effortless.\n\n"
            "Kajiado is one of our primary service areas and is comfortably within reach "
            "from Syokimau."
        ),
        "order": 3,
    },
    {
        "slug": "kiambu",
        "county": "Kiambu",
        "hero_headline": "Digital Growth Agency in Kiambu County",
        "intro": (
            "Kiambu County — Thika, Ruiru, Juja, Kikuyu and Limuru — has one of the densest "
            "concentrations of small and medium businesses in Kenya, and customers who "
            "regularly compare options online before buying."
        ),
        "body": (
            "Density cuts both ways. There are plenty of potential customers nearby, and "
            "plenty of businesses competing for them. In that situation the deciding factor "
            "is often simply which business looks more credible when someone checks — and "
            "that check usually takes seconds.\n\n"
            "For Kiambu businesses we focus on looking genuinely established online: a "
            "professional website, an active Google presence, and social pages that have not "
            "been abandoned. For retail and product businesses, a proper e-commerce setup "
            "often makes sense, since customers here are already comfortable buying online.\n\n"
            "We work with Kiambu clients remotely as standard, with in-person meetings "
            "where they help."
        ),
        "order": 4,
    },
]


class Command(BaseCommand):
    help = "Populate services, packages, locations and blog scaffolding from the master spec."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help=(
                "Overwrite existing records with the spec values. Off by default so that "
                "running this against a live site never clobbers edits made in Admin."
            ),
        )
        parser.add_argument(
            "--with-posts",
            action="store_true",
            help="Also create example blog posts, so blog templates can be reviewed.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        update = options["update"]
        created, skipped = 0, 0

        def upsert(model, slug_field, slug, defaults):
            nonlocal created, skipped
            lookup = {slug_field: slug}
            obj = model.objects.filter(**lookup).first()
            if obj is None:
                obj = model.objects.create(**lookup, **defaults)
                created += 1
            elif update:
                for key, value in defaults.items():
                    setattr(obj, key, value)
                obj.save()
                created += 1
            else:
                skipped += 1
            return obj

        # Site settings — a singleton, and every contact detail is already a
        # model default, so this only needs to exist.
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create()
            self.stdout.write("Created Site settings")

        for data in SERVICES:
            upsert(Service, "slug", data.pop("slug"), data)

        for data in PACKAGES:
            upsert(Package, "slug", data.pop("slug"), data)

        for data in LOCATIONS:
            upsert(LocationPage, "slug", data.pop("slug"), data)

        for name, slug, description in CATEGORIES:
            upsert(Category, "slug", slug, {"name": name, "description": description})

        # Link each location to the services most relevant to it, rather than to
        # everything, so the internal linking stays meaningful.
        for location in LocationPage.objects.all():
            if not location.featured_services.exists():
                location.featured_services.set(
                    Service.objects.filter(
                        slug__in=["website-creation", "seo-aeo-optimization", "website-audit-revamp"]
                    )
                )

        if options["with_posts"]:
            self._create_posts(update)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} record(s) written, {skipped} left untouched"
                f"{' (use --update to overwrite)' if skipped else ''}."
            )
        )
        self.stdout.write(
            "Testimonials and case studies were deliberately not created — "
            "proof is never seeded."
        )

    def _create_posts(self, update):
        author = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if author is None:
            self.stdout.write(self.style.WARNING("No user exists; skipping blog posts."))
            return

        posts = [
            {
                "slug": "website-cost-kenya",
                "title": "How much should a website cost in Kenya?",
                "category": "web-development",
                "excerpt": (
                    "What actually drives the price of a business website, and what you should "
                    "expect at each level."
                ),
                "quick_answer": (
                    "A professional business website in Kenya starts around KES 30,000. What "
                    "moves the price is scope, not page count: a brochure site is straightforward, "
                    "while e-commerce or booking systems cost more because they do more."
                ),
                "body": textwrap.dedent("""\
                    Ask three agencies what a website costs and you will get three very different
                    numbers. That is not necessarily dishonesty — it usually means they are
                    quoting for three different things.

                    Here is what actually moves the price.

                    ## What the site has to do

                    A site that explains your business and collects enquiries is a fundamentally
                    smaller build than one that takes payments or manages bookings. E-commerce
                    needs product management, a cart, checkout and order handling. A hotel
                    booking system needs availability logic. Those are not extra pages, they are
                    extra systems.

                    ## Whether the content exists

                    Many quotes assume you will supply text and images. If you do not have them,
                    someone has to create them, and that is real work. Being honest about this up
                    front avoids the most common cause of a project stalling halfway.

                    ## Whether search was considered

                    A site built first and optimised later usually needs rebuilding to rank. Our
                    [website development](/web-development/) work builds the structure in from day one.
                    Structure, headings, speed and metadata are cheaper to get right during the
                    build than to retrofit afterwards.

                    ## What happens after launch

                    A website is not furniture. Content goes stale, links break and speed drifts.
                    Ask whether the quote includes any support, or whether you are on your own
                    from launch day.

                    ## A reasonable expectation

                    For a professional, mobile-friendly, search-ready business website, KES 30,000
                    is a realistic starting point. Substantially cheaper usually means a template
                    with your logo on it. Substantially more should come with a clear explanation
                    of what the extra buys.
                    """),
                "faqs": [
                    {
                        "question": "Is a cheaper website always worse?",
                        "answer": (
                            "Not always, but ask what is missing. Very low quotes usually skip "
                            "search structure, custom design or post-launch support — costs that "
                            "reappear later."
                        ),
                    },
                    {
                        "question": "How long does a website take to build?",
                        "answer": (
                            "Most business websites take two to four weeks. The biggest variable "
                            "is usually how quickly content and feedback come back, not the build."
                        ),
                    },
                ],
            },
            {
                "slug": "google-business-profile-visibility",
                "title": "Why your business isn't showing up on Google Maps",
                "category": "seo-aeo",
                "excerpt": (
                    "The most common reasons a Kenyan business stays invisible in local search — "
                    "and how to fix each one."
                ),
                "quick_answer": (
                    "Most businesses that do not appear on Google Maps either have no Google "
                    "Business Profile, have one they never verified, or have one that is complete "
                    "but inactive. All three are fixable, usually within days."
                ),
                "body": textwrap.dedent("""\
                    When someone nearby searches for what you sell, Google decides which handful
                    of businesses to show on the map. If you are not among them, the enquiry goes
                    to someone else — and you never know it happened.

                    There are four usual causes.

                    ## You do not have a profile

                    The most common one. A [Google Business Profile](/services/seo-optimization/) is free and separate
                    from having a website. Without it you are largely invisible in local search.

                    ## It exists but was never verified

                    Unverified profiles are heavily limited in what Google will show. Verification
                    usually involves a postcard, a phone call or a video, depending on the
                    business type.

                    ## It is incomplete

                    Google favours profiles that answer a searcher's question without them having
                    to click. Missing hours, no category, no photos and no description all work
                    against you.

                    ## It is complete but dormant

                    A profile that has not been touched in a year signals a business that may not
                    be operating. Posts, fresh photos and replies to reviews all indicate an
                    active business.

                    ## What to do first

                    Search for your own business on Google Maps, on a phone, while not logged in
                    as the owner. What you see is roughly what a customer sees. Start with
                    whichever of the four causes above you just confirmed.
                    """),
                "faqs": [
                    {
                        "question": "How long until my business appears on Google Maps?",
                        "answer": (
                            "After verification, a profile usually appears within a few days. "
                            "Ranking well for competitive searches takes longer and depends on "
                            "completeness, reviews and activity."
                        ),
                    },
                    {
                        "question": "Do I need a website to have a Google Business Profile?",
                        "answer": (
                            "No. They are separate and a profile is free. A website does help "
                            "your profile rank, and gives customers somewhere to go once they "
                            "find you."
                        ),
                    },
                ],
            },
            {
                "slug": "seo-vs-aeo",
                "title": "SEO vs AEO: what changed when AI started answering",
                "category": "seo-aeo",
                "excerpt": (
                    "Search is no longer only ten blue links. Here is what that means for a "
                    "small business in Kenya."
                ),
                "quick_answer": (
                    "SEO gets your page ranked. AEO gets your business named in the answer itself "
                    "— in Google's summaries, voice results and AI assistants. AEO builds on SEO "
                    "rather than replacing it."
                ),
                "body": textwrap.dedent("""\
                    For twenty years the goal of search was simple: rank high enough that someone
                    clicks your link. That is still worth doing, but it is no longer the whole
                    game.

                    Increasingly, people get an answer instead of a list — from Google's own
                    summaries, from a voice assistant, or from an AI tool they asked directly.
                    In each case, something has to decide which business gets named.

                    ## What AEO actually involves

                    Answer Engine Optimization is less exotic than it sounds. It means structuring
                    content so a machine can extract a clean answer from it:

                    - **Answer the question directly**, early, in plain language, instead of building
                      up to it over five paragraphs.
                    - **Use headings that state what the section covers**, so a machine can find the
                      part that answers the question.
                    - **Mark up FAQs properly**, so they can be read as questions and answers.
                    - **Be specific and factual.** Vague marketing copy gives a machine nothing to
                      quote.

                    ## Why this matters more for small businesses

                    Competing with a large company on domain authority is hard. Competing on being
                    the clearest, most specific answer to a local question is much more winnable —
                    a national chain rarely has a good answer for a question about your town.

                    ## What not to do

                    AEO is not a reason to publish thin articles at volume. Answer engines are
                    built to identify genuinely useful content, and filler is the thing they are
                    designed to filter out.

                    The practical version

                    Keep doing SEO. Then make sure each important page answers its main question
                    in the first paragraph, uses honest headings, and includes real FAQs. That is
                    most of AEO.
                    """),
                "faqs": [
                    {
                        "question": "Does AEO replace SEO?",
                        "answer": (
                            "No. AEO builds on SEO. A page still has to be findable and credible "
                            "before it can be quoted in an answer."
                        ),
                    },
                    {
                        "question": "Can a small business realistically compete in AI search?",
                        "answer": (
                            "Often more easily than in traditional search. Being the clearest, "
                            "most specific answer to a local question is winnable in a way that "
                            "out-ranking a national brand is not."
                        ),
                    },
                ],
            },
        ]

        for data in posts:
            category_slug = data.pop("category")
            post = BlogPost.objects.filter(slug=data["slug"]).first()
            if post and not update:
                continue
            if post is None:
                post = BlogPost(slug=data["slug"])
            for key, value in data.items():
                setattr(post, key, value)
            post.author = author
            post.is_published = True
            post.save()
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                post.categories.set([category])

        self.stdout.write("Created example blog posts — review and rewrite in your own voice.")

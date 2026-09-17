from django.core.paginator import Paginator
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.utils.text import Truncator

from apps.accounts.models import User
from apps.core.seo import absolute_url, breadcrumbs, page_meta

from .models import BlogPost, Category

POSTS_PER_PAGE = 9


def _paginate(request, queryset):
    return Paginator(queryset, POSTS_PER_PAGE).get_page(request.GET.get("page"))


def _navigable_categories():
    """Categories that actually contain something.

    An empty category is a dead end: the reader clicks a tag and is told to
    check back later. It is also a thin page for search, so it is neither
    linked nor submitted until it has a post in it.
    """
    return Category.objects.filter(
        is_active=True, posts__in=BlogPost.published.all()
    ).distinct()


def post_list(request):
    context = {
        "page_obj": _paginate(request, BlogPost.published.all()),
        "categories": _navigable_categories(),
        **page_meta(
            request,
            title="SEO, Websites & Digital Growth in Kenya — VEE Agency",
            description=(
                "Practical guidance on SEO, websites, Google Business Profile and ads, "
                "written for business owners in Kenya. No jargon, no filler."
            ),
            page_class="blog",
        ),
    }
    return render(request, "blog/post_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    posts = BlogPost.published.filter(categories=category)
    context = {
        "category": category,
        "page_obj": _paginate(request, posts),
        "categories": _navigable_categories(),
        **page_meta(
            request,
            title=f"{category.name} — VEE Agency Insights",
            description=category.description
            or f"Articles on {category.name} for businesses in Kenya, from VEE Agency.",
            page_class="blog-category",
            noindex=not posts.exists(),
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            ("Blog", reverse("blog:list")),
            (category.name, None),
        ),
    }
    return render(request, "blog/category_detail.html", context)


def post_detail(request, slug):
    post = get_object_or_404(BlogPost.published.select_related("author"), slug=slug)
    context = {
        "post": post,
        "related_posts": BlogPost.published.filter(
            categories__in=post.categories.all()
        ).exclude(pk=post.pk).distinct()[:3],
        **page_meta(
            request,
            title=post.meta_title or f"{post.title} — VEE Agency",
            description=post.meta_description or post.excerpt[:300],
            page_class="blog-post",
            image=post.featured_image.url if post.featured_image else None,
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            ("Blog", reverse("blog:list")),
            (post.title, None),
        ),
        # Links the byline to a real Person entity rather than leaving it text.
        "author_url": absolute_url(
            reverse("blog:author", kwargs={"username": post.author.username})
        ),
    }
    return render(request, "blog/post_detail.html", context)


def author_detail(request, username):
    author = get_object_or_404(User, username=username, is_active=True)
    context = {
        "author": author,
        "page_obj": _paginate(request, BlogPost.published.filter(author=author)),
        **page_meta(
            request,
            title=f"{author.display_name} — Author at VEE Agency",
            description=(
                Truncator(author.bio).chars(155)
                or (
                    f"Articles by {author.display_name} on SEO, websites and digital "
                    f"growth for businesses in Kenya."
                )
            ),
            page_class="blog-author",
        ),
        "breadcrumbs": breadcrumbs(
            ("Home", reverse("core:home")),
            ("Blog", reverse("blog:list")),
            (author.display_name, None),
        ),
    }
    return render(request, "blog/author_detail.html", context)

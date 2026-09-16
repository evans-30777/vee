from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from apps.accounts.models import User
from apps.core.seo import page_meta

from .models import BlogPost, Category

POSTS_PER_PAGE = 9


def _paginate(request, queryset):
    return Paginator(queryset, POSTS_PER_PAGE).get_page(request.GET.get("page"))


def post_list(request):
    context = {
        "page_obj": _paginate(request, BlogPost.published.all()),
        "categories": Category.objects.filter(is_active=True),
        **page_meta(
            request,
            title="Insights on SEO, Websites & Digital Growth in Kenya — VEE Agency",
            description=(
                "Practical articles on SEO & AEO, websites, Google Business Profile, "
                "social media and digital ads for businesses in Nairobi, Machakos, "
                "Kajiado, Kiambu and across Kenya."
            ),
            page_class="blog",
        ),
    }
    return render(request, "blog/post_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    context = {
        "category": category,
        "page_obj": _paginate(request, BlogPost.published.filter(categories=category)),
        "categories": Category.objects.filter(is_active=True),
        **page_meta(
            request,
            title=f"{category.name} — VEE Agency Insights",
            description=category.description
            or f"Articles on {category.name} for businesses in Kenya, from VEE Agency.",
            page_class="blog-category",
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
    }
    return render(request, "blog/post_detail.html", context)


def author_detail(request, username):
    author = get_object_or_404(User, username=username, is_active=True)
    context = {
        "author": author,
        "page_obj": _paginate(request, BlogPost.published.filter(author=author)),
        **page_meta(
            request,
            title=f"{author.display_name} — VEE Agency",
            description=author.bio[:300] or f"Articles written by {author.display_name} at VEE Agency.",
            page_class="blog-author",
        ),
    }
    return render(request, "blog/author_detail.html", context)

from django.shortcuts import render
from django.db.models import Count
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else None,
        'likes_amount': getattr(post, 'likes_count', 0),
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_with_tag if hasattr(tag, 'posts_with_tag') else 0,
    }


def index(request):
    most_popular_posts = (
        Post.objects
        .annotate(likes_count=Count('likes'))
        .order_by('-likes_count')
        .prefetch_related('author', 'tags')
    )[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    most_fresh_posts = (
        Post.objects
        .annotate(likes_count=Count('likes'))
        .order_by('-published_at')
        .prefetch_related('author', 'tags')
    )[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = (
        Post.objects
        .annotate(likes_count=Count('likes'))
        .prefetch_related('author', 'tags', 'comments')
        .get(slug=slug)
    )

    comments = (
        post.comments
        .select_related('author')
        .only('text', 'published_at', 'author__username')
    )

    serialized_comments = [
        {'text': comment.text, 'published_at': comment.published_at, 'author': comment.author.username}
        for comment in comments
    ]

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    related_posts = (
        tag.posts
        .annotate(likes_count=Count('likes'))
        .order_by('-published_at')
        .prefetch_related('author', 'tags', 'comments')
    )[:20]

    most_popular_posts = (
        Post.objects
        .annotate(likes_count=Count('likes'))
        .order_by('-likes_count')
        .prefetch_related('author', 'tags', 'comments')
    )[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})

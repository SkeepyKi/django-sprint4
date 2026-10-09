"""Публикации, профили и комментарии."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = 10


def post_queryset():
    """Посты со связанными объектами и числом комментариев."""
    return Post.objects.select_related(
        'author', 'category', 'location').annotate(
            comment_count=Count('comments')).order_by('-pub_date')


def published_posts(queryset):
    """Доступные всем публикации."""
    return queryset.filter(is_published=True,
                           category__is_published=True,
                           pub_date__lte=timezone.now())


def paginate(request, queryset):
    """Страница с десятью публикациями."""
    return Paginator(queryset,
                     POSTS_PER_PAGE).get_page(request.GET.get('page'))


def index(request):
    """Главная страница."""
    return render(
        request, 'blog/index.html',
        {'page_obj': paginate(request, published_posts(post_queryset()))})


def category_posts(request, category_slug):
    """Публикации категории."""
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    posts = published_posts(post_queryset()).filter(category=category)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': paginate(request, posts),
    })


def post_detail(request, post_id):
    """Автор видит также скрытые и отложенные записи."""
    post = get_object_or_404(post_queryset(), pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(published_posts(post_queryset()), pk=post_id)
    return render(
        request, 'blog/detail.html', {
            'post': post,
            'form': CommentForm(),
            'comments': post.comments.select_related('author'),
        })


def profile(request, username):
    """Профиль пользователя и его публикации."""
    user = get_object_or_404(User, username=username)
    posts = post_queryset().filter(author=user)
    if request.user != user:
        posts = published_posts(posts)
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': paginate(request, posts),
    })


@login_required
def edit_profile(request):
    """Редактирование собственного профиля."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    """Создание публикации от текущего пользователя."""
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Изменение поста доступно только его автору."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Удаление после подтверждения автором."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html',
                  {'form': PostForm(instance=post)})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к доступной публикации."""
    post = get_object_or_404(published_posts(post_queryset()), pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование собственного комментария."""
    comment = get_object_or_404(Comment,
                                pk=comment_id,
                                post_id=post_id,
                                author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария после подтверждения автором."""
    comment = get_object_or_404(Comment,
                                pk=comment_id,
                                post_id=post_id,
                                author=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})

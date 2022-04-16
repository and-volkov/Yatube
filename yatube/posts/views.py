from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

from .models import Comment, Follow, Group, Post, User
from .forms import CommentForm, PostForm

POSTS_PER_PAGE = settings.POSTS_PER_PAGE


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Записи сообщества {Group.__str__(group)}'
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    following = False
    author = User.objects.get(username=username)
    if request.user.is_authenticated:
        user = request.user
        if Follow.objects.filter(user=user, author=author):
            following = True
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профайл пользователя {username}'
    context = {
        'author': author,
        'page_obj': page_obj,
        'title': title,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    title = f'Пост {post.text[:30]}'
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {
        'post': post,
        'post_count': post_count,
        'title': title,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)  # Pre-init form
    if request.method == 'POST' and form.is_valid():
        form.text = form.cleaned_data['text']
        form.group = form.cleaned_data['group']
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    return render(request, template, {'form': form})


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    instance = Post.objects.get(id=post_id)
    form = PostForm(request.POST or None,
                    instance=instance,
                    files=request.FILES or None)  # Pre-init form
    if request.user.id == instance.author_id:
        if request.method == 'POST' and form.is_valid():
            form.text = form.cleaned_data['text']
            form.group = form.cleaned_data['group']
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form, 'is_edit': True})
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    user = request.user
    # list of followed authors
    following = Follow.objects.values_list('author').filter(user=user)
    # Posts of all authors
    post_list = Post.objects.filter(author__in=following)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Подписки пользователя {user.username}'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', author)

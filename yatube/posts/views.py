from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Follow, Post, Group, User
from .forms import CommentForm, PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


SORT_TEN: int = 10


@cache_page(20)
def index(request):
    posts = Post.objects.select_related('group')
    paginator = Paginator(posts, SORT_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all()
    paginator = Paginator(posts, SORT_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def posts_list(request):
    return HttpResponse('Список сообщений')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=author).order_by('-pub_date')
    post_count = author.posts.count()
    paginator = Paginator(posts, SORT_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = author.get_full_name
    title_1 = author.get_username
    following = (request.user != author
                 and request.user.is_authenticated
                 and Follow.objects.filter(
                     user=request.user,
                     author=author).exists())
    context = {
        'following': following,
        'page_obj': page_obj,
        'author': author,
        'title': title,
        'post_count': post_count,
        'title_1': title_1,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = get_object_or_404(User, id=post.author_id)
    post_count = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.all()
    following = (request.user != username
                 and request.user.is_authenticated
                 and Follow.objects.filter(
                     user=request.user,
                     author=username).exists())
    context = {
        'following': following,
        'form': form,
        'username': username,
        'post': post,
        'post_count': post_count,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(
        request,
        'includes/comments.html',
        {'form': form, 'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, SORT_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_follow = get_object_or_404(User, username=username)
    if author_follow != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author_follow
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        author__username=username, user=request.user)
    follow.delete()
    return redirect('posts:profile', username=username)

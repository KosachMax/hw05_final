from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import get_page_context


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    context = get_page_context(Post.objects.all(), request)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    context = {
        'group': group,
    }
    context.update(get_page_context(posts, request))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    following = False
    if request.user.is_authenticated and request.user != author:
        following = Follow.objects.select_related(
            'user', 'author'
        ).exists()
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if not form.is_valid():
        context = {'form': form}
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post_id = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_id
    )
    context = {
        'form': form,
        'is_edit': True,
    }
    if request.user != post_id.author:
        return redirect('posts:post_detail', post_id=post_id.pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id.pk)
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


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post = Post.objects.filter(author__following__user=request.user)
    context = {
        'post': post,
    }
    context.update(get_page_context(post, request))
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(
                User,
                username=username
            )
        )
        return redirect('posts:profile', username)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username)

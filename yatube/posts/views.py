from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group, User, Comment, Follow
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


def get_pg(queryset, request):
    paginator = Paginator(queryset, settings.NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


@cache_page(20, cache='default', key_prefix='index_page')
def index(request):
    context = get_pg(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_pg(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    follow_yourself = False
    if request.user in User.objects.all():
        if author == request.user:
            follow_yourself = True
            following = True
        else:
            if Follow.objects.filter(
                    author=author, user=request.user).exists():
                following = True
    context = {
        'author': author,
        'following': following,
        'follow_yourself': follow_yourself,
    }
    context.update(get_pg(author.posts.all(), request))
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=post.author)
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    context = {'post_count': post_count,
               'post': post,
               'form': form,
               'comments': comments,
               }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    user = request.user
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            valid_form = form.save(commit=False)
            valid_form.author = user
            valid_form.save()
            return redirect('posts:profile', username=user.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    follow_posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'follow_posts': follow_posts,
    }
    context = get_pg(follow_posts, request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follower = Follow.objects.filter(user=user, author=author)
    if user != author and not follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author.username)

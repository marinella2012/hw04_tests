from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator}
     )

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'group.html',
        {
            'page': page,
            'paginator': paginator,
            'group': group,
        }
     )     

@login_required()
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    user1 = get_object_or_404(User, username=username)
    post_list = user1.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {
            'page': page,
            'author': user1,
            'paginator': paginator,
        }
    )

def post_view(request, username, post_id):
    post_list = Post.objects.filter(author__username=username)
    post = get_object_or_404(post_list, id=post_id)
    return render(
        request,
        'post.html',
        {
            'author': post.author,
            'post': post,
        }
    )

@login_required()
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = user.posts.get(id=post_id)
    if request.user != user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post',
                        username=username,
                        post_id=post_id
                        )
    return render(request, 'new_post.html', {'form': form, 'post': post})

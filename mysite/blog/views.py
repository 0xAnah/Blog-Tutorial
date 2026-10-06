from django.shortcuts import render
from django.http import Http404
from .models import Post

# Create your views here.

def post_list(request):
    posts = Post.published.all()
    context = {'posts':posts}
    return render(request, 'blog/post/list.html', context)

def post_detail(request, year, month, day, post):
    try:
        post = Post.published.get(publish__year=year, publish__month=month, publish__day=day, slug=post)
    except Post.DoesNotExist():
        raise Http404("No post found")
    context = {'post': post}
    return render(request, 'blog/post/detail.html', context)
    
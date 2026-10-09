from django.core.paginator import Paginator
from django.views.generic import ListView
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import EmailPostForm
from django.http import Http404
from .models import Post

# Create your views here.


class PostListView(ListView):
    """
        Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    context = {'posts':posts}
    return render(request, 'blog/post/list.html', context)

def post_detail(request, year, month, day, post):
    try:
        post = Post.published.get(publish__year=year, publish__month=month, publish__day=day, slug=post)
    except Post.DoesNotExist():
        raise Http404("No post found")
    context = {'post': post}
    return render(request, 'blog/post/detail.html', context)

def post_share(request, post_id):
    try:
        post = Post.published.get(id=post_id)
    except Post.DoesNotExist():
        raise Http404("No post found")
    
    sent = False 
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form passed validation clean the form
            cd = form.cleaned_data
            # send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comment: {cd['comments']}"
            send_mail(subject=subject, message=message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {'form':form, 'post':post, 'sent': sent}
    return render(request, 'blog/post/share.html', context)
    
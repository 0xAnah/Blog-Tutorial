from django.views.decorators.http import require_POST
from .forms import EmailPostForm, CommentForm
from django.db.models import Count
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.core.mail import send_mail
from django.shortcuts import render
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
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    context = {'post': post, 'comments':comments, 'form': form, 'similar_posts': similar_posts}
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

@require_POST
def post_comment(request, post_id):
    try:
        post = Post.published.get(id=post_id)
    except Post.DoesNotExist():
        raise Http404('No post found')
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the data
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form,'comment': comment})
    
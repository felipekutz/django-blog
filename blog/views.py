from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.contrib.postgres.search import TrigramSimilarity

from django.views.generic import ListView, DetailView
from django.views import View
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail

from taggit.models import Tag

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
    def get_queryset(self):
        tag = self.kwargs.get("tag_slug")
        search = Q()
        if tag:
            tag = get_object_or_404(Tag, slug=tag)
            search.add(Q(tags__in=[tag]), Q.AND)
        
        return self.queryset.filter(search)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.kwargs.get("tag_slug")
        return context

# TODO  change to class base view
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else: 
        comment_form = CommentForm()
    
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id).annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post':post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form, 'similar_posts': similar_posts})

# it looks like a function it will be cleaner
class PostShareView(DetailView):
    model = Post
    form_class = EmailPostForm
    template_name = "blog/post/share.html"

    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id, status='published')
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommend you read {post.title}"
            message = f"Read {post.title} at {post_url}\n \n {cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@theblogemail.com', [cd['to']])
        return render(request=request, template_name=self.template_name,  context={'form': form, 'post': post, 'sent':True})

    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id, status='published')
        form = self.form_class()
        return render(request=request, template_name=self.template_name,  context={'form': form, 'post': post})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query), ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form':form, 'query':query, 'results':results})

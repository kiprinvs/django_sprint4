from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Post, Category, Comment
from .mixins import (
    OnlyAuthorMixin, PostSuccessUrlMixin, ProfileSuccesUrlMixin, CommentMixin
)
from .forms import PostForm, CommentForm, UserForm

MAX_AMOUNT_POSTS = 10

User = get_user_model()


def get_posts_queryset(filters=False, annotations=False):
    base_query = Post.objects.select_related(
        'category',
        'location',
        'author',
    )
    if filters:
        base_query = base_query.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if annotations:
        base_query = base_query.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return base_query


class CategoryListVIew(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = MAX_AMOUNT_POSTS

    def get_category(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
        return category

    def get_queryset(self):
        return get_posts_queryset(
            filters=True,
            annotations=True
        ).filter(
            category=self.get_category()
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()

        context['category'] = category
        return context


class CommentCreateView(LoginRequiredMixin, PostSuccessUrlMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        form.instance.post_id = post.id
        return super().form_valid(form)


class CommentDeleteView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, DeleteView
):
    pass


class CommentUpdateView(
    LoginRequiredMixin, OnlyAuthorMixin, CommentMixin, UpdateView
):
    pass


class PostCreateView(LoginRequiredMixin, ProfileSuccesUrlMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(OnlyAuthorMixin, ProfileSuccesUrlMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    queryset = get_posts_queryset()

    def get_object(self):
        post = super().get_object()
        if (
            self.request.user != post.author
            and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()
            )
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostListView(ListView):
    paginate_by = MAX_AMOUNT_POSTS
    template_name = 'blog/index.html'
    queryset = get_posts_queryset(filters=True, annotations=True)


class PostUpdateView(OnlyAuthorMixin, PostSuccessUrlMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_AMOUNT_POSTS

    def get_user(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return user

    def get_queryset(self):
        queryset = get_posts_queryset(
            filters=self.request.user != self.get_user(),
            annotations=True
        )
        return queryset.filter(author=self.get_user())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user()
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileSuccesUrlMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    form_class = UserForm

    def get_object(self):
        return self.request.user

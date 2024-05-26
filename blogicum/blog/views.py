from datetime import datetime

from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .models import Post, Category, Comment
from .mixins import OnlyAuthorMixin, PostSuccessUrlMixin, ProfileSuccesUrlMixin
from .forms import PostForm, CommentForm, UserForm

MAX_AMOUNT_POSTS = 10

User = get_user_model()


def base_query(post_objects=Post.objects):
    """Базовый запрос к БД"""
    return post_objects.select_related(
        'category',
        'location',
        'author',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(),
    ).order_by(
        '-pub_date'
    ).annotate(comment_count=Count('comments')).all()


class CategoryListVIew(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = MAX_AMOUNT_POSTS

    def get_queryset(self):
        return base_query().filter(category__slug=self.kwargs['category_slug']
                                   ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )

        context['category'] = category
        return context


class CommentCreateView(LoginRequiredMixin, PostSuccessUrlMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, pk=post_id)
        form.instance.post_id = post.id
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, PostSuccessUrlMixin, DeleteView):
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id)

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(LoginRequiredMixin, PostSuccessUrlMixin, UpdateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


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
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            base_query(),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = MAX_AMOUNT_POSTS
    template_name = 'blog/index.html'

    def get_queryset(self):
        return base_query()


class PostUpdateView(OnlyAuthorMixin, PostSuccessUrlMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_AMOUNT_POSTS

    def get_queryset(self):
        if self.request.user.username == self.kwargs['username']:
            return self.request.user.posts.select_related(
                "category",
                "author",
                "location",
            ).order_by(
                '-pub_date'
            ).annotate(comment_count=Count('comments')).all()
        return base_query()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        context['profile'] = user
        post_list = super().get_queryset()
        context['post_list'] = post_list
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileSuccesUrlMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    form_class = UserForm
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self):
        return self.request.user

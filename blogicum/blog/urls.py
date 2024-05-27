from django.urls import include, path

from . import views

app_name = 'blog'

post_urls = [
    path('',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryListVIew.as_view(),
         name='category_posts'),
    path('edit_profile/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:post_id>/', include(post_urls)),
    path('profile/<username>/',
         views.ProfileListView.as_view(),
         name='profile'),
]

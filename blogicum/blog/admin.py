from django.contrib import admin

from .models import Post, Category, Location, Comment


class PostAdmin(admin.ModelAdmin):
    """Редактирование постов"""

    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_editable = (
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_display_links = ('title',)
    list_filter = ('category', 'author', 'location')


class CategoryAdmin(admin.ModelAdmin):
    """Редактирование категорий"""

    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = (
        'description',
        'slug',
        'is_published'
    )
    list_display_links = ('title',)
    list_filter = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'author')


class LocationAdmin(admin.ModelAdmin):
    """Редактирование местоположения"""

    list_display = (
        'name',
        'is_published'
    )
    list_editable = (
        'is_published',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)

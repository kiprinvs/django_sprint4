from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_LENGTH_CHAR_FIELD = 256


class BaseModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и дату."""

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Post(BaseModel):
    """Публикация"""

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=MAX_LENGTH_CHAR_FIELD,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        related_name='posts',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        'Location',
        verbose_name='Местоположение',
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Category(BaseModel):
    """Категория"""

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=MAX_LENGTH_CHAR_FIELD,
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    """Местоположение"""

    name = models.CharField(
        verbose_name='Название места',
        max_length=MAX_LENGTH_CHAR_FIELD,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text

"""Модели публикаций блога."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedModel(models.Model):
    """Общие свойства публикации."""

    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    """Категория публикаций."""

    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор', unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает название."""
        return self.title


class Location(PublishedModel):
    """Место публикации."""

    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        """Возвращает название."""
        return self.name


class Post(PublishedModel):
    """Запись автора."""

    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    image = models.ImageField('Изображение', upload_to='posts/', blank=True)
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.')
    author = models.ForeignKey(
        User, verbose_name='Автор публикации',
        on_delete=models.CASCADE, related_name='posts')
    location = models.ForeignKey(
        Location, verbose_name='Местоположение',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    category = models.ForeignKey(
        Category, verbose_name='Категория',
        on_delete=models.SET_NULL, null=True, related_name='posts')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        """Возвращает заголовок."""
        return self.title


class Comment(models.Model):
    """Комментарий к публикации."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращает начало текста."""
        return self.text[:50]

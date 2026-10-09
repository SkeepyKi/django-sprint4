"""Формы публикаций, комментариев и профиля."""
from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Создание и изменение публикации."""

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Текст комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):
    """Изменяемые поля пользователя."""

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email')

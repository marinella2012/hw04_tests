from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        help_text='Дайте короткое название группы',
        max_length=200
    )
    slug = models.SlugField(
        'Адрес для страницы группы',
        help_text=('Укажите адрес для страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания'),
        max_length=100,
        unique=True
    )
    description = models.TextField(
        'Описание группы',
        help_text='Дайте короткое описание группы',
        max_length=200
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Пост',
        help_text='Напишите что-нибудь в посте'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        text_short = self.text[:15]
        return text_short

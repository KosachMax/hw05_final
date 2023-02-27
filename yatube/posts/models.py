from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from core.models import CreatedModel

User = get_user_model()
LETTERS_IN_POST = 15


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название Группы',
        max_length=200,
        default='-пусто-',
        help_text='Напишите, как будет называться группа'
    )
    slug = models.SlugField(
        verbose_name='Уникальный адрес для страницы с группой',
        unique=True,
        help_text='Добавляется автоматически'
    )
    description = models.TextField(
        verbose_name='Описание Группы',
        max_length=400,
        help_text='Кратко опишите, о чем будет группа'
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Напишите, о чем сейчас думаете'
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Тут указывается автор поста'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        blank=True,
        null=True,
        help_text='Создавайте группы по интересам'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        default_related_name = 'posts'
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:LETTERS_IN_POST]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Запись',
        help_text='Напишите, о чем сейчас думаете'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор коммента',
        help_text='Тут указывается автор коммента'
    )
    text = models.TextField(
        max_length=400,
        verbose_name='Текст коммента',
        help_text='Напишите, о чем сейчас думаете'
    )

    class Meta:
        default_related_name = 'comments'
        ordering = ('-created',)
        verbose_name = 'Коммент'
        verbose_name_plural = 'Комменты'

    def __str__(self):
        return self.text[:LETTERS_IN_POST]


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Кто Подписывается',
        help_text='Тут указывается кто подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписывается',
        help_text='Тут указывается на кого подписывается'
    )
    UniqueConstraint(
        fields=['user', 'author'],
        name='unique_follow_set'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Избранные авторы'

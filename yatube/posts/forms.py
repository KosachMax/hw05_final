from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_texts = {
            'text': 'Любую абракадабру',
            'group': 'Из уже существующих',
            'image': 'Картинка на ваш вкус'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст сообщения',
            'group': 'Группа которой будет принадлежать сообщение',
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст сообщения',
        }
        labels = {
            'text': 'Текст поста'
        }
